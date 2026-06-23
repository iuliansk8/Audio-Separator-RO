import streamlit as st
import soundfile as sf
import numpy as np
import os
from scipy.signal import butter, lfilter

st.set_page_config(page_title="P-Bass Studio Mixer", page_icon="🎸", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    body { background-color: #000000; }
    h1 { color: #ffffff; text-align: center; font-family: 'Helvetica Neue', sans-serif; font-size: 2rem; font-weight: bold; }
    p.subtitle { text-align: center; color: #888888; font-size: 1rem; margin-bottom: 25px; }
    .mixer-card { background-color: #0b0b0c; border: 1px solid #1c1c1e; border-radius: 16px; padding: 25px; margin-top: 15px; }
    .channel-box { background-color: #141416; border-radius: 12px; padding: 15px; margin-bottom: 15px; border: 1px solid #232326; }
    .stButton>button { width: 100%; background-color: #10b981 !important; color: white !important; font-weight: bold; border-radius: 12px; border: none; padding: 14px; font-size: 1.1rem; }
    </style>
""", unsafe_allow_html=True)

st.title("🎸 P-Bass Studio Mixer")
st.markdown("<p class='subtitle'>Melodia Ta + Linie de Bas Ultra-Amplificată</p>", unsafe_allow_html=True)

# Filtru Lowpass foarte agresiv (taie tot peste 120Hz) pentru a lăsa doar sub-bass-ul pur
def extract_deep_bass(data, fs, cutoff=120, order=6):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    bass = lfilter(b, a, data, axis=0)
    # Amplificăm masiv (de 8 ori) semnalul ca să sune foarte tare și clar
    return bass * 8.0

uploaded_file = st.file_uploader("Încarcă fișierul audio (MP3 sau WAV)", type=["mp3", "wav"])

if uploaded_file is not None:
    original_path = "melodie_originala.wav"
    bass_path = "numai_bass.wav"

    if st.button("🚀 Generează Melodia și Basul P-Bass"):
        with st.spinner("Se procesează piesa ta local..."):
            try:
                # Citim fișierul audio încărcat de tine
                data, samplerate = sf.read(uploaded_file)
                
                # Salvăm piesa originală pe server
                sf.write(original_path, data, samplerate)
                
                # Extragem și amplificăm doar linia de bas din piesa ta
                if len(data.shape) > 1:  # Stereo
                    bass_data = np.zeros_like(data)
                    bass_data[:, 0] = extract_deep_bass(data[:, 0], samplerate)
                    bass_data[:, 1] = extract_deep_bass(data[:, 1], samplerate)
                else:  # Mono
                    bass_data = extract_deep_bass(data, samplerate)
                
                # Limitează semnalul ca să nu distorsioneze distrugător
                bass_data = np.clip(bass_data, -1.0, 1.0)
                sf.write(bass_path, bass_data, samplerate)
                
                st.session_state.canale_gata = True
            except Exception as e:
                st.error(f"Eroare la procesarea fișierului: {e}")

    if os.path.exists(original_path) and os.path.exists(bass_path):
        st.write("---")
        st.markdown('<div class="mixer-card">', unsafe_allow_html=True)
        st.subheader("🎚️ Playere Audio Independente")

        # CANALUL 1: MELODIA ORIGINALĂ
        st.markdown('<div class="channel-box">', unsafe_allow_html=True)
        st.markdown("### 🎵 1. Melodia Completă (Original)")
        st.audio(original_path)
        st.markdown('</div>', unsafe_allow_html=True)

        # CANALUL 2: DOAR LINIA DE BAS TARE ȘI CLAR
        st.markdown('<div class="channel-box">', unsafe_allow_html=True)
        st.markdown("### 🎸 2. Doar Linia de Bas (P-BASS Pure)")
        st.audio(bass_path)
        with open(bass_path, "rb") as f:
            st.download_button("⬇️ Descarcă doar Basul (.wav)", f, "bas_curat.wav")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
