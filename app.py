import os
import streamlit as st
import soundfile as sf
import torch
import yt_dlp
import base64
from demucs import separate

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

st.markdown("""
    <style>
    .main { background-color: #0b0f19; color: #e2e8f0; }
    h1 { color: #38bdf8; text-align: center; font-family: 'Helvetica Neue', sans-serif; font-weight: 800; }
    p.subtitle { text-align: center; color: #64748b; font-size: 1.1rem; }
    .stButton>button { width: 100%; background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important; color: white !important; font-weight: bold; border-radius: 8px; border: none; padding: 10px; }
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

    cale_voce = "separated/htdemucs/temp_input/vocals.wav"
    cale_bas = "separated/htdemucs/temp_input/bass.wav"
    cale_tobe = "separated/htdemucs/temp_input/drums.wav"
    cale_altele = "separated/htdemucs/temp_input/other.wav"

    if os.path.exists(cale_voce) and os.path.exists(cale_bas) and os.path.exists(cale_tobe) and os.path.exists(cale_altele):
        st.write("---")
        st.subheader("🎚️ Mixer Audio Studio (Sincronizat)")

        def get_audio_base64(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()

        b64_voce = get_audio_base64(cale_voce)
        b64_bas = get_audio_base64(cale_bas)
        b64_tobe = get_audio_base64(cale_tobe)
        b64_altele = get_audio_base64(cale_altele)

        mixer_html = f"""
        <div style="background-color: #131926; padding: 20px; border-radius: 12px; border: 1px solid #1e293b; max-width: 500px; margin: 0 auto; font-family: sans-serif; color: white;">
            <div style="text-align: center; margin-bottom: 25px;">
                <button id="btn-play" style="background-color: #10b981; color: white; border: none; padding: 12px 28px; font-weight: bold; font-size: 1.1rem; border-radius: 50px; cursor: pointer; margin-right: 10px;">▶ PLAY ALL</button>
                <button id="btn-pause" style="background-color: #ef4444; color: white; border: none; padding: 12px 28px; font-weight: bold; font-size: 1.1rem; border-radius: 50px; cursor: pointer;">⏸ PAUSE</button>
                <div id="status" style="margin-top: 10px; font-size: 0.85rem; color: #10b981;">Mixer pregătit.</div>
            </div>

            <div style="margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px; font-weight: bold;"><span>🎤 Voce (Vocals)</span><span id="val-voce">100%</span></div>
                <input type="range" id="vol-voce" min="0" max="1" step="0.01" value="1" style="width: 100%;">
            </div>
            <div style="margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px; font-weight: bold;"><span>🎸 Bass</span><span id="val-bas">100%</span></div>
                <input type="range" id="vol-bas" min="0" max="1" step="0.01" value="1" style="width: 100%;">
            </div>
            <div style="margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px; font-weight: bold;"><span>🥁 Tobe (Drums)</span><span id="val-tobe">100%</span></div>
                <input type="range" id="vol-tobe" min="0" max="1" step="0.01" value="1" style="width: 100%;">
            </div>
            <div style="margin-bottom: 25px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px; font-weight: bold;"><span>🎹 Instrumente (Melodie)</span><span id="val-altele">100%</span></div>
                <input type="range" id="vol-altele" min="0" max="1" step="0.01" value="1" style="width: 100%;">
            </div>
        </div>

        <script>
            let audioCtx = null;
            let sources = [];
            let gainNodes = {{ "voce": null, "bas": null, "tobe": null, "altele": null }};
            let audioBuffers = {{}};
            let isPlaying = false;
            let startTime = 0;
            let pauseTime = 0;

            const b64Data = {{
                "voce": "{b64_voce}",
                "bas": "{b64_bas}",
                "tobe": "{b64_tobe}",
                "altele": "{b64_altele}"
            }};

            function b64ToArray(base64) {{
                let bin = window.atob(base64);
                let bytes = new Uint8Array(bin.length);
                for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
                return bytes.buffer;
            }}

            async function initAudio() {{
                if (!audioCtx) {{
                    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                    document.getElementById('status').innerText = "Se încarcă muzica în consolă...";
                    let keys = ['voce', 'bas', 'tobe', 'altele'];
                    for(let k of keys) {{
                        audioBuffers[k] = await audioCtx.decodeAudioData(b64ToArray(b64Data[k]));
                    }}
                    document.getElementById('status').innerText = "Mixer activat!";
                }}
            }}

            function playTracks(offset) {{
                sources = [];
                let keys = ['voce', 'bas', 'tobe', 'altele'];
                keys.forEach(k => {{
                    let src = audioCtx.createBufferSource();
                    src.buffer = audioBuffers[k];
                    let gain = audioCtx.createGain();
                    gain.gain.value = document.getElementById('vol-' + k).value;
                    src.connect(gain);
                    gain.connect(audioCtx.destination);
                    gainNodes[k] = gain;
                    sources.push(src);
                    src.start(0, offset);
                }});
                startTime = audioCtx.currentTime - offset;
                isPlaying = true;
                document.getElementById('status').innerText = "🎵 Muzica se aude sincronizat!";
            }}

            document.getElementById('btn-play').addEventListener('click', async () => {{
                await initAudio();
                if (audioCtx.state === 'suspended') await audioCtx.resume();
                if (isPlaying) return;
                playTracks(pauseTime);
            }});

            document.getElementById('btn-pause').addEventListener('click', () => {{
                if (!isPlaying) return;
                pauseTime = audioCtx.currentTime - startTime;
                sources.forEach(s => {{ try{{s.stop();}}catch(e){{}} }});
                isPlaying = false;
                document.getElementById('status').innerText = "⏸️ Pauză";
            }});

            ['voce', 'bas', 'tobe', 'altele'].forEach(k => {{
                document.getElementById('vol-' + k).addEventListener('input', (e) => {{
                    let v = e.target.value;
                    document.getElementById('val-' + k).innerText = Math.round(v * 100) + '%';
                    if (gainNodes[k]) gainNodes[k].gain.setValueAtTime(v, audioCtx.currentTime);
                }});
            }});
        </script>
        """
        st.components.v1.html(mixer_html, height=420)

        st.write("---")
        with st.expander("⬇️ Descarcă fișierele pe telefon"):
            st.download_button("🎤 Descarcă Vocea", open(cale_voce, "rb"), "voce.wav")
            st.download_button("🎸 Descarcă Bass-ul", open(cale_bas, "rb"), "bass.wav")
            st.download_button("🥁 Descarcă Tobele", open(cale_tobe, "rb"), "tobe.wav")
            st.download_button("🎹 Descarcă Instrumentele", open(cale_altele, "rb"), "instrumentale.wav")
