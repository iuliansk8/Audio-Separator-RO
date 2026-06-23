import os
import streamlit as st
import soundfile as sf
import torch
from demucs import separate

import demucs.separate
import torchaudio

# Optimizări pentru a rula pe servere cu memorie puțină
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

st.set_page_config(page_title="AI Audio Separator 4-Stems", page_icon="🎵", layout="centered")

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

st.title("🎵 AI Audio Separator - Pro Mixer")
st.markdown("<p class='subtitle'>Separare completă pe 4 canale: Voce, Bass, Tobe și Instrumente</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Încarcă fișierul audio (MP3 sau WAV)", type=["mp3", "wav"])

cale_audio_intrare = "temp_input.wav"

if uploaded_file is not None:
    if not os.path.exists(cale_audio_intrare):
        data, samplerate = sf.read(uploaded_file)
        sf.write(cale_audio_intrare, data, samplerate)

    if st.button("🚀 Lansează Separarea pe 4 Canale"):
        with st.spinner("Inteligența Artificială separă melodia în Voce, Bass, Tobe și Instrumente..."):
            try:
                # Utilizăm modelul htdemucs_light conceput special pentru consum redus de resurse
                separate.main(["-n", "htdemucs_light", cale_audio_intrare])
                st.success("🎉 Separare completă!")
            except Exception as e:
                st.error("A apărut o eroare la procesare. Încearcă din nou.")

    # Căile folderelor unde salvează modelul htdemucs_light
    cale_voce = "separated/htdemucs_light/temp_input/vocals.wav"
    cale_bas = "separated/htdemucs_light/temp_input/bass.wav"
    cale_tobe = "separated/htdemucs_light/temp_input/drums.wav"
    cale_altele = "separated/htdemucs_light/temp_input/other.wav"

    if os.path.exists(cale_voce):
        st.write("---")
        st.subheader("🎛️ Mixer Canale Audio")

        st.markdown('<div class="track-box"><div class="track-title">🎤 Voce (Vocals)</div></div>', unsafe_allow_html=True)
        st.audio(cale_voce)
        with open(cale_voce, "rb") as f:
            st.download_button("⬇️ Descarcă Vocea", f, "voce.wav", mime="audio/wav")

        st.markdown('<div class="track-box"><div class="track-title">🎸 Bass</div></div>', unsafe_allow_html=True)
        st.audio(cale_bas)
        with open(cale_bas, "rb") as f:
            st.download_button("⬇️ Descarcă Bass-ul", f, "bass.wav", mime="audio/wav")

        st.markdown('<div class="track-box"><div class="track-title">🥁 Tobe (Drums)</div></div>', unsafe_allow_html=True)
        st.audio(cale_tobe)
        with open(cale_tobe, "rb") as f:
            st.download_button("⬇️ Descarcă Tobele", f, "tobe.wav", mime="audio/wav")

        st.markdown('<div class="track-box"><div class="track-title">🎹 Alte Instrumente (Melodie/Other)</div></div>', unsafe_allow_html=True)
        st.audio(cale_altele)
        with open(cale_altele, "rb") as f:
            st.download_button("⬇️ Descarcă Instrumentele", f, "instrumente.wav", mime="audio/wav")
