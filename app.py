import streamlit as st
import soundfile as sf
import numpy as np
import os
from scipy.signal import butter, lfilter

st.set_page_config(page_title="Studio Bass Mixer", page_icon="🎸", layout="centered")

# Stil vizual elegant, negru cu verde neon pentru studio
st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    body { background-color: #000000; }
    h1 { color: #ffffff; text-align: center; font-family: 'Helvetica Neue', sans-serif; font-size: 2rem; font-weight: bold; }
    p.subtitle { text-align: center; color: #888888; font-size: 1rem; margin-bottom: 25px; }
    .mixer-card { background-color: #0b0b0c; border: 1px solid #1c1c1e; border-radius: 16px; padding: 20px; margin-top: 15px; }
    .channel-box { background-color: #141416; border-radius: 12px; padding: 15px; margin-bottom: 15px; border: 1px solid #232326; }
    .stButton>button { width: 100%; background-color: #10b981 !important; color: white !important; font-weight: bold; border-radius: 12px; border: none; padding: 14px; font-size: 1.1rem; }
    </style>
""", unsafe_allow_html=True)

st.title("🎸 Studio Bass Mixer")
st.markdown("<p class='subtitle'>Control Melodie + Linie de Bas P-Bass Izolată</p>", unsafe_allow_html=True)

# Filtru digital lowpass optimizat pentru a extrage doar textura de P-Bass (sub 160Hz)
def extract_p_bass(data, fs, cutoff=160, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return lfilter(b, a, data, axis=0)

uploaded_file = st.file_uploader("Încarcă fișierul audio (MP3 sau WAV)", type=["mp3", "wav"])

if uploaded_file is not None:
    full_song_path = "original_song.wav"
    p_bass_path = "p_bass_line.wav"

    if st.button("🚀 Procesează și Izolează Basul"):
        with st.spinner("Se extrage linia de bas din piesa ta..."):
            try:
                # Citim fișierul încărcat de tine
                data, samplerate = sf.read(uploaded_file)
                
                # Salvăm piesa originală completă
                sf.write(full_song_path, data, samplerate)
                
                # Aplicăm filtrul pentru a izola basul tip chitară bas joasă
                bass_data = extract_p_bass(data, samplerate)
                sf.write(p_bass_path, bass_data, samplerate)
                
                st.session_state.mixer_gata = True
            except Exception as e:
                st.error(f"Eroare la deschiderea fișierului: {e}")

    # Dacă fișierele au fost create, afișăm doar cele 2 canale cerute
    if os.path.exists(full_song_path) and os.path.exists(p_bass_path):
        st.write("---")
        st.markdown('<div class="mixer-card">', unsafe_allow_html=True)
        
        # CANALUL 1: MELODIA GENERALĂ
        st.markdown('<div class="channel-box">', unsafe_allow_html=True)
        st.markdown("### 🎵 1. Melodia Completă (Original Song)")
        st.slider("Volum Melodie", 0, 100, 100, key="vol_melodie")
        st.audio(full_song_path)
        st.markdown('</div>', unsafe_allow_html=True)

        # CANALUL 2: LINIA DE BASS
        st.markdown('<div class="channel-box">', unsafe_allow_html=True)
        st.markdown("### 🎸 2. Linia de Bas (P-BASS Filtered)")
        st.slider("Volum Chitară Bas", 0, 100, 100, key="vol_bass")
        st.audio(p_bass_path)
        with open(p_bass_path, "rb") as f:
            st.download_button("⬇️ Descarcă doar Basul (.wav)", f, "p_bass.wav")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
