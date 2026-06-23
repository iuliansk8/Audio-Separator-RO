import os
import streamlit as st
import soundfile as sf
import torch
import yt_dlp
import base64
from demucs import separate

# Ajustări de bază pentru compatibilitate
import demucs.separate
import torchaudio

def _incarcare_audio_simpla(track, channels=2, samplerate=44100):
    data, sr = sf.read(str(track), always_2d=True)
    tensor = torch.tensor(data.T, dtype=torch.float32)
    return tensor

def _salvare_audio_simpla(filepath, src, sample_rate, channels_first=True, bits_per_sample=16, format=None, encoding=None):
    data = src.cpu().transpose(0, 1).numpy() if channels_first else src.cpu().numpy()
    sf.write(str(filepath), data, sample_rate)

demucs.separate.load_track = lambda track, *args, **kwargs: _incarcare_audio_simpla(track)
torchaudio.load = lambda track, *args, **kwargs: (_incarcare_audio_simpla(track), 44100)
torchaudio.save = _salvare_audio_simpla

st.set_page_config(page_title="AI Audio Studio Mixer", page_icon="🎛️", layout="centered")

# Stil vizual premium tip Studio Dark Mode
st.markdown("""
    <style>
    .main { background-color: #0b0f19; color: #e2e8f0; }
    h1 { color: #38bdf8; text-align: center; font-family: 'Helvetica Neue', sans-serif; font-weight: 800; margin-bottom: 0px; }
    p.subtitle { text-align: center; color: #64748b; font-size: 1.1rem; margin-bottom: 30px; }
    .stRadio>div { justify-content: center; }
    .stButton>button { width: 100%; background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important; color: white !important; font-weight: bold; border-radius: 8px; border: none; padding: 10px; }
    .stButton>button:hover { background: linear-gradient(135deg, #0369a1 0%, #075985 100%) !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🎛️ AI Audio Studio Mixer")
st.markdown("<p class='subtitle'>Descarcă din YouTube, separă melodia și mixează instrumentele în timp real!</p>", unsafe_allow_html=True)

metoda = st.radio("Alege sursa audio:", ("Introduce un link de YouTube", "Încarcă fișier propriu (MP3/WAV)"))

cale_audio_intrare = None

if metoda == "Introduce un link de YouTube":
    youtube_url = st.text_input("Lipește link-ul de YouTube aici 👇", placeholder="https://www.youtube.com/watch?v=...")
    if youtube_url:
        if st.button("📥 Preia melodia de pe YouTube"):
            with st.spinner("Se descarcă de pe YouTube..."):
                try:
                    ydl_opts = {
                        'format': 'bestaudio/best',
                        'outtmpl': 'temp_input.%(ext)s',
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'wav',
                            'preferredquality': '192',
                        }],
                        'keepvideo': False,
                    }
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([youtube_url])
                    
                    for f in os.listdir('.'):
                        if f.startswith('temp_input'):
                            os.rename(f, 'temp_input.wav')
                            break
                    st.success("✅ Melodia a fost preluată!")
                except Exception as e:
                    st.error(f"Eroare YouTube: {e}")
                    
        if os.path.exists("temp_input.wav"):
            cale_audio_intrare = "temp_input.wav"

else:
    uploaded_file = st.file_uploader("Trage aici fișierul audio (MP3, WAV)", type=["mp3", "wav"])
    if uploaded_file is not None:
        input_filename = "temp_input.wav"
        data, samplerate = sf.read(uploaded_file)
        sf.write(input_filename, data, samplerate)
        cale_audio_intrare = input_filename

if cale_audio_intrare:
    if st.button("🚀 Lansează Separarea AI și Deschide Mixerul"):
        with st.spinner("Inteligența Artificială izolează pistele... Te rugăm să aștepți."):
            try:
                separate.main(["-n", "htdemucs", cale_audio_intrare])
                st.success("🎉 Separare completă!")
            except Exception as e:
                st.error("Eroare la procesarea AI.")
                st.exception(e)

    # Căi către cele 4 componente separate
    cale_voce = "separated/htdemucs/temp_input/vocals.wav"
    cale_bas = "separated/htdemucs/temp_input/bass.wav"
    cale_tobe = "separated/htdemucs/temp_input/drums.wav"
    cale_altele = "separated/htdemucs/temp_input/other.wav"

    if os.path.exists(cale_voce) and os.path.exists(cale_bas) and os.path.exists(cale_tobe) and os.path.exists(cale_altele):
        st.write("---")
        st.subheader("🎚️ Mixer Audio Studio (Sincronizat)")
        st.write("Apasă PLAY pentru a porni toată piesa, apoi folosește glisoarele pentru a ajusta volumul fiecărui element în timp real!")

        # Funcție ajutătoare pentru a converti fișierele audio locale în cod binar citit de browser direct
        def get_audio_base64(path):
            with open(path, "rb") as f:
                data = f.read()
            return base64.b64encode(data).decode()

        # Generăm string-urile Base64 pentru HTML5 Web Audio API
        b64_voce = get_audio_base64(cale_voce)
        b64_bas = get_audio_base64(cale_bas)
        b64_tobe = get_audio_base64(cale_tobe)
        b64_altele = get_audio_base64(cale_altele)

        # Inserăm Playerul / Mixerul personalizat în HTML/JavaScript perfect sincronizat
        mixer_html = f"""
        <div style="background-color: #131926; padding: 20px; border-radius: 12px; border: 1px solid #1e293b; max-width: 500px; margin: 0 auto; font-family: sans-serif; color: white;">
            
            <div style="text-align: center; margin-bottom: 25px;">
                <button id="btn-play" style="background-color: #10b981; color: white; border: none; padding: 12px 28px; font-weight: bold; font-size: 1.1rem; border-radius: 50px; cursor: pointer; margin-right: 10px; box-shadow: 0 4px 6px -1px rgba(16, 185, 129, 0.3);">▶ PLAY ALL</button>
                <button id="btn-pause" style="background-color: #ef4444; color: white; border: none; padding: 12px 28px; font-weight: bold; font-size: 1.1rem; border-radius: 50px; cursor: pointer; box-shadow: 0 4px 6px -1px rgba(239, 68, 68, 0.3);">⏸ PAUSE</button>
                <div id="status" style="margin-top: 10px; font-size: 0.85rem; color: #10b981;">Mixer pregătit.</div>
            </div>

            <div style="margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px; font-weight: bold;">
                    <span>🎤 Voce (Vocals)</span>
                    <span id="val-voce">100%</span>
                </div>
                <input type="range" id="vol-voce" min="0" max="1" step="0.01" value="1" style="width: 100%; accent-color: #38bdf8; cursor: pointer;">
            </div>

            <div style="margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px; font-weight: bold;">
                    <span>🎸 Bass</span>
                    <span id="val-bas">100%</span>
                </div>
                <input type="range" id="vol-bas" min="0" max="1" step="0.01" value="1" style="width: 100%; accent-color: #38bdf8; cursor: pointer;">
            </div>

            <div style="margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px; font-weight: bold;">
                    <span>🥁 Tobe (Drums)</span>
                    <span id="val-tobe">100%</span>
                </div>
                <input type="range" id="vol-tobe" min="0" max="1" step="0.01" value="1" style="width: 100%; accent-color: #38bdf8; cursor: pointer;">
            </div>

            <div style="margin-bottom: 25px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px; font-weight: bold;">
                    <span>🎹 Instrumente (Melodie)</span>
                    <span id="val-altele">100%</span>
                </div>
                <input type="range" id="vol-altele" min="0" max="1" step="0.01" value="1" style="width: 100%; accent-color: #38bdf8; cursor: pointer;">
            </div>

        </div>

        <script>
            // Audio Context pentru controlul nativ al volumelor în timp real
            let audioCtx = null;
            let sources = [];
            let gainNodes = {{
                voce: null,
                bas: null,
                tobe: null,
                altele: null
            }};
            let audioBuffers = {{}};
            let isPlaying = false;
            let startTime = 0;
            let pauseTime = 0;

            // Datele audio Base64 convertite în ArrayBuffers în fundal
            const b64Data = {{
                voce: "{b64_voce}",
                bas: "{b64_bas}",
                tobe: "{b64_tobe}",
                altele: "{b64_altele}"
            }};

            function base64ToArrayBuffer(base64) {{
                var binary_string = window.atob(base64);
                var len = binary_string.length;
                var bytes = new Uint8Array(len);
                for (var i = 0; i < len; i++) {{
                    bytes[i] = binary_string.charCodeAt(i);
                }}
                return bytes.buffer;
            }}

            async function initAudio() {{
                if (!audioCtx) {{
                    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                    document.getElementById('status').innerText = "Se încarcă pistele în mixer...";
                    
                    // Decodăm toate cele 4 piste în paralel
                    const keys = ['voce', 'bas', 'tobe', 'altele'];
                    for(let key of keys) {{
                        const arrayBuf = base64ToArrayBuffer(b64Data[key]);
                        audioBuffers[key] = await audioCtx.decodeAudioData(arrayBuf);
                    }}
                    document.getElementById('status').innerText = "Mixerul este gata complet!";
                }}
            }}

            function playTracks(offset) {{
                sources = [];
                const keys = ['voce', 'bas', 'tobe', 'altele'];
                
                keys.forEach(key => {{
                    let source = audioCtx.createBufferSource();
                    source.buffer = audioBuffers[key];
                    
                    let gainNode = audioCtx.createGain();
                    // Setăm volumul curent din glisor
                    const currentVol = document.getElementById('vol-' + key).value;
                    gainNode.gain.value = currentVol;
                    
                    source.connect(gainNode);
                    gainNode.connect(audioCtx.destination);
                    
                    gainNodes[key] = gainNode;
                    sources.push(source);
                    
                    // Pornim toate pistele fix în același timp absolut
                    source.start(0, offset);
                }});
                
                startTime = audioCtx.currentTime - offset;
                isPlaying = true;
                document.getElementById('status').innerText = "🎵 Studio Active (Muzica cântă sincronizat)";
            }}

            function stopTracks() {{
                sources.forEach(source => {{
                    try {{ source.stop(); }} catch(e) {{}}
                }});
                sources = [];
                isPlaying = false;
            }}

            document.getElementById('btn-play').addEventListener('click', async () => {{
                await initAudio();
                if (audioCtx.state === 'suspended') {{
                    await audioCtx.resume();
                }}
                if (isPlaying) return;
                playTracks(pauseTime);
            }});

            document.getElementById('btn-pause').addEventListener('click', () => {{
                if (!isPlaying) return;
                pauseTime = audioCtx.currentTime - startTime;
                // Dacă melodia s-a terminat natural, resetăm la 0
                if (pauseTime >= audioBuffers['voce'].duration) {{
                    pauseTime = 0;
                }}
                stopTracks();
                document.getElementById('status').innerText = "⏸️ Pauză";
            }});

            // Ascultători pentru glisarea volumului în timp real (fără întreruperea piesei)
            ['voce', 'bas', 'tobe', 'altele'].forEach(key => {{
                document.getElementById('vol-' + key).addEventListener('input', (e) => {{
                    const val = e.target.value;
                    document.getElementById('val-' + key).innerText = Math.round(val * 100) + '%';
                    if (gainNodes[key]) {{
                        gainNodes[key].gain.setValueAtTime(val, audioCtx.currentTime);
                    }}
                }});
            }});
        </script>
        """
        
        # Randăm mixerul JS direct în aplicație
        st.components.v1.html(mixer_html, height=400)

        # Butoane standard de salvare, în caz că vor doar să le descarce la final în telefon
        st.write("---")
        with st.expander("⬇️ Vrei să descarci fișierele separat pe telefon?"):
            st.download_button("🎤 Descarcă Vocea (.wav)", open(cale_voce, "rb"), "voce.wav")
            st.download_button("🎸 Descarcă Bass-ul (.wav)", open(cale_bas, "rb"), "bass.wav")
            st.download_button("🥁 Descarcă Tobele (.wav)", open(cale_tobe, "rb"), "tobe.wav")
            st.download_button("🎹 Descarcă Instrumentele (.wav)", open(cale_altele, "rb"), "instrumental.wav")
