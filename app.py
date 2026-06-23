import os
import streamlit as st
import soundfile as sf
import torch
import yt_dlp
from demucs import separate

# Păcălim Demucs și Torchaudio pentru stabilitate pe server
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

st.set_page_config(page_title="AI Audio Separator Pro", page_icon="🎵", layout="centered")

# Design modern (Dark Mode elegant)
st.markdown("""
    <style>
    .main { background-color: #0f172a; color: white; }
    h1 { color: #38bdf8; text-align: center; font-family: 'Helvetica Neue', sans-serif; font-size: 2.5rem; }
    p { text-align: center; color: #94a3b8; }
    .stButton>button { width: 100%; background-color: #0284c7 !important; color: white !important; font-weight: bold; border-radius: 8px; }
    .stButton>button:hover { background-color: #0369a1 !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🎵 AI Audio Separator Pro")
st.write("Separă instant vocea de instrumente folosind Inteligența Artificială!")

# Alegere metodă de introducere
metoda = st.radio("Alege cum vrei să pui piesa:", ("Introduce un link de YouTube", "Încarcă fișier propriu (MP3/WAV)"))

cale_audio_intrare = None

if metoda == "Introduce un link de YouTube":
    youtube_url = st.text_input("Lipește link-ul de YouTube aici 👇", placeholder="https://www.youtube.com/watch?v=...")
    if youtube_url:
        if st.button("📥 Preia melodia de pe YouTube"):
            with st.spinner("Se descarcă audio de pe YouTube..."):
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
                    # Forțăm salvarea direct ca WAV prin yt-dlp simplificat
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([youtube_url])
                    
                    # Căutăm fișierul descărcat
                    for f in os.listdir('.'):
                        if f.startswith('temp_input'):
                            os.rename(f, 'temp_input.wav')
                            break
                    st.success("✅ Melodia a fost preluată cu succes!")
                    cale_audio_intrare = "temp_input.wav"
                except Exception as e:
                    st.error(f"Eroare la descărcarea de pe YouTube: {e}")
                    
        if os.path.exists("temp_input.wav"):
            cale_audio_intrare = "temp_input.wav"
            st.audio(cale_audio_intrare)

else:
    uploaded_file = st.file_uploader("Trage aici fișierul audio (MP3, WAV)", type=["mp3", "wav"])
    if uploaded_file is not None:
        input_filename = "temp_input.wav"
        data, samplerate = sf.read(uploaded_file)
        sf.write(input_filename, data, samplerate)
        cale_audio_intrare = input_filename
        st.audio(cale_audio_intrare)

# Dacă avem o melodie pregătită (fie din YT, fie din Upload)
if cale_audio_intrare:
    st.write("---")
    st.subheader("🎛️ Opțiuni Separare AI")
    
    if st.button("🚀 Lansează Separarea Totală (Voce + Instrumente)"):
        with st.spinner("Modelul AI htdemucs procesează piesa. Poate dura 1-3 minute..."):
            try:
                # Rulăm modelul standard de 4 instrumente (mai rapid și optimizat pentru server)
                separate.main(["-n", "htdemucs", cale_audio_intrare])
                st.success("🎉 Procesare finalizată!")
            except Exception as e:
                st.error("A apărut o eroare în timpul procesării AI.")
                st.exception(e)

    # Playerul Avansat - Apare automat dacă fișierele au fost generate
    cale_voce = "separated/htdemucs/temp_input/vocals.wav"
    cale_tobe = "separated/htdemucs/temp_input/drums.wav"
    cale_bas = "separated/htdemucs/temp_input/bass.wav"
    cale_altele = "separated/htdemucs/temp_input/other.wav" # Chitare, clape etc.

    if os.path.exists(cale_voce):
        st.write("---")
        st.subheader("🎧 Mixer Audio Avansat")
        st.write("Ascultă și descarcă exact ce ai nevoie:")

        # Secțiunea VOCALS
        st.markdown("🎤 **Doar Vocea (Vocals)**")
        st.audio(cale_voce, format='audio/wav')
        with open(cale_voce, "rb") as f:
            st.download_button("⬇️ Descarcă Vocea", f, "voce_izolata.wav", mime="audio/wav")

        st.write("---")

        # Secțiunea INSTRUMENTAL
        st.markdown("🎸 **Instrumental Complet (Tobe + Bas + Melodie)**")
        # Combinăm cele 3 piese de instrumente într-una singură pentru player direct în soundfile
        try:
            v_data, sr = sf.read(cale_tobe)
            b_data, _ = sf.read(cale_bas)
            o_data, _ = sf.read(cale_altele)
            # Adunăm matricile ca să creăm instrumentalul complet
            instrumental_data = v_data + b_data + o_data
            sf.write("separated/htdemucs/temp_input/instrumental.wav", instrumental_data, sr)
            
            st.audio("separated/htdemucs/temp_input/instrumental.wav", format='audio/wav')
            with open("separated/htdemucs/temp_input/instrumental.wav", "rb") as f:
                st.download_button("⬇️ Descarcă Instrumentalul", f, "instrumental_complet.wav", mime="audio/wav")
        except:
            st.info("Ascultă instrumentele separat mai jos:")

        # Elemente secundare detaliate
        with st.expander("🔍 Vezi instrumentele separat (Tobe, Bas, Altele)"):
            st.markdown("🥁 Tobe")
            st.audio(cale_tobe)
            st.markdown("🎸 Bas")
            st.audio(cale_bas)
            st.markdown("🎹 Altele (Chitari/Pian)")
            st.audio(cale_altele)
