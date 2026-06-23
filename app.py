import os
import streamlit as st
import soundfile as sf
import torch
import yt_dlp
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

st.set_page_config(page_title="AI Audio Separator", page_icon="🎵", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0f172a; color: white; }
    h1 { color: #38bdf8; text-align: center; font-family: 'Helvetica Neue', sans-serif; font-size: 2.3rem; font-weight: bold; }
    p.subtitle { text-align: center; color: #94a3b8; font-size: 1.1rem; }
    .stButton>button { width: 100%; background-color: #0284c7 !important; color: white !important; font-weight: bold; border-radius: 8px; border: none; padding: 12px; }
    .stButton>button:hover { background-color: #0369a1 !important; }
    .track-box { background-color: #1e293b; padding: 12px; border-radius: 8px; margin-top: 15px; margin-bottom: 5px; border-left: 5px solid #38bdf8; }
    .track-title { font-size: 1.1rem; font-weight: bold; color: #f1f5f9; }
    </style>
""", unsafe_allow_html=True)

st.title("🎵 AI Audio Separator")
st.markdown("<p class='subtitle'>Descarcă de pe YouTube sau încarcă piese, apoi separă instrumentele!</p>", unsafe_allow_html=True)

metoda = st.radio("Alege sursa audio:", ("Introduce un link de YouTube", "Încarcă fișier propriu (MP3/WAV)"))

cale_audio_intrare = None

# IZOLARE COMPLETĂ REPREZENTÂND SURSA SELECTATĂ
if metoda == "Introduce un link de YouTube":
    youtube_url = st.text_input("Lipește link-ul de YouTube aici 👇", placeholder="https://www.youtube.com/watch?v=...")
    if youtube_url:
        if st.button("📥 Preia melodia de pe YouTube"):
            with st.spinner("Se descarcă de pe YouTube..."):
                try:
                    if os.path.exists("temp_input.wav"):
                        os.remove("temp_input.wav")
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
                        if f.startswith('temp_input') and f.endswith('.wav'):
                            st.success("✅ Melodia a fost preluată!")
                            break
                except Exception as e:
                    st.error(f"Eroare YouTube: {e}")

    if os.path.exists("temp_input.wav"):
        cale_audio_intrare = "temp_input.wav"

else:
    # Dacă este selectat fișier local, ignorăm total restul verificărilor de YouTube
    uploaded_file = st.file_uploader("Trage aici fișierul audio (MP3, WAV)", type=["mp3", "wav"])
    if uploaded_file is not None:
        if not os.path.exists("temp_input.wav"):
            input_filename = "temp_input.wav"
            data, samplerate = sf.read(uploaded_file)
            sf.write(input_filename, data, samplerate)
        cale_audio_intrare = "temp_input.wav"

# Butonul rulează doar dacă fișierul de intrare este pregătit corect
if cale_audio_intrare and os.path.exists(cale_audio_intrare):
    if st.button("🚀 Lansează Separarea AI"):
        with st.spinner("Inteligența Artificială izolează pistele..."):
            try:
                separate.main(["-n", "mdx_extra_q", cale_audio_intrare])
                st.success("🎉 Separare completă!")
            except Exception as e:
                st.error("Eroare la procesarea AI.")
                st.exception(e)

    cale_voce = "separated/mdx_extra_q/temp_input/vocals.wav"
    cale_bas = "separated/mdx_extra_q/temp_input/bass.wav"
    cale_tobe = "separated/mdx_extra_q/temp_input/drums.wav"
    cale_altele = "separated/mdx_extra_q/temp_input/other.wav"

    if os.path.exists(cale_voce):
        st.write("---")
        st.subheader("🎛️ Canale Audio Separate")

        st.markdown('<div class="track-box"><div class="track-title">🎤 Voce (Vocals)</div></div>', unsafe_allow_html=True)
        st.audio(cale_voce)
        with open(cale_voce, "rb") as f:
            st.download_button("⬇️ Descarcă Vocea", f, "voce.wav", mime="audio/wav")

        st.markdown('<div class="track-box"><div class="track-title">🎸 Bass</div></div>', unsafe_allow_html=True)
        st.audio(cale_bas)
        with open(cale_bas, "rb") as f:
            st.download_button("⬇️ Descarcă Bass-ul", f, "bass.wav", mime="audio/wav")

        st.markdown('<div class="track-box"><div class="track-title">🥁 Tobă (Drums)</div></div>', unsafe_allow_html=True)
        st.audio(cale_tobe)
        with open(cale_tobe, "rb") as f:
            st.download_button("⬇️ Descarcă Tobele", f, "tobe.wav", mime="audio/wav")

        st.markdown('<div class="track-box"><div class="track-title">🎹 Instrumente (Melodie/Other)</div></div>', unsafe_allow_html=True)
        st.audio(cale_altele)
        with open(cale_altele, "rb") as f:
            st.download_button("⬇️ Descarcă Instrumentele", f, "instrumente.wav", mime="audio/wav")
