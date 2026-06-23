import streamlit as st
import soundfile as sf
import numpy as np
import os
from scipy.signal import butter, lfilter

st.set_page_config(page_title="Orga Bass Local Studio", page_icon="🎹", layout="centered")

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

st.title("🎹 Orga Bass Local Studio")
st.markdown("<p class='subtitle'>Izolator de Formulă și Bătaie Bass de la Orgă (Fără Erori de Rețea)</p>", unsafe_allow_html=True)

# Filtru de Studio Bandpass reglat special pentru frecvențele clapei stângi (70Hz - 240Hz)
def extract_orga_bass_formula(data, fs, lowcut=70, highcut=240, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band', analog=False)
    filtered = lfilter(b, a, data, axis=0)
    
    # Amplificare dinamică puternică pentru a scoate notele clapei în evidență
    return filtered * 9.0

uploaded_file = st.file_uploader("Încarcă piesa ta (MP3 sau WAV)", type=["mp3", "wav"])

if uploaded_file is not None:
    original_path = "piesa_originala.wav"
    orga_bass_path = "bataie_bass_orga.wav"

    if st.button("🚀 Izolează Instant Formula de Bass de la Orgă"):
        with st.spinner("Se extrag notele și ritmul clapei stângi..."):
            try:
                # Citire locală direct de pe serverul tău
                data, samplerate = sf.read(uploaded_file)
                
                # Salvăm piesa originală
                sf.write(original_path, data, samplerate)
                
                # Aplicăm izolatorul de acorduri și bătăi de orgă
                if len(data.shape) > 1:  # Stereo
                    bass_data = np.zeros_like(data)
                    bass_data[:, 0] = extract_orga_bass_formula(data[:, 0], samplerate)
                    bass_data[:, 1] = extract_orga_bass_formula(data[:, 1], samplerate)
                else:  # Mono
                    bass_data = extract_orga_bass_formula(data, samplerate)
                
                # Protectie împotriva distorsiunii
                bass_data = np.clip(bass_data, -1.0, 1.0)
                sf.write(orga_bass_path, bass_data, samplerate)
                
                st.session_state.orga_gata = True
            except Exception as e:
                st.error(f"Eroare la procesarea fișierului: {e}")

    if os.path.exists(original_path) and os.path.exists(orga_bass_path):
        st.write("---")
        st.markdown('<div class="mixer-card">', unsafe_allow_html=True)
        st.subheader("🎚️ Playere Monitorizare Studio")

        # PLAYER 1: MELODIA TA
        st.markdown('<div class="channel-box">', unsafe_allow_html=True)
        st.markdown("### 🎵 1. Melodia Completă")
        st.audio(original_path)
        st.markdown('</div>', unsafe_allow_html=True)

        # PLAYER 2: FORMULA DE CLAPĂ
        st.markdown('<div class="channel-box">', unsafe_allow_html=True)
        st.markdown("### 🎹 2. Doar Formula / Bătaia de Bass din Orgă")
        st.audio(orga_bass_path)
        with open(orga_bass_path, "rb") as f:
            st.download_button("⬇️ Descarcă Formula de Bass (.wav)", f, "bataie_bass_orga.wav")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
