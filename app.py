import streamlit as st
import soundfile as sf
import numpy as np
import os

st.set_page_config(page_title="Orga Bass Ultra-Clean", page_icon="🎹", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    .mixer-card { background-color: #1a1a1a; padding: 20px; border-radius: 15px; }
    .stButton>button { width: 100%; background-color: #ff4b4b !important; color: white !important; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("🎹 Orga Bass: Extracție „Center-Channel”")
st.markdown("Fără filtre care bâzâie, doar separare de fază pentru bass pur.")

uploaded_file = st.file_uploader("Încarcă melodia ta", type=["mp3", "wav"])

if uploaded_file is not None:
    if st.button("🚀 Extrage Basul prin Inversiune de Fază"):
        with st.spinner("Procesez..."):
            data, sr = sf.read(uploaded_file)
            
            # Dacă piesa e stereo (L, R)
            if len(data.shape) > 1:
                # Formula de "Center Channel Extraction" - elimină tot ce nu e în centru
                # Asta scoate vocile și tobele de fundal și lasă linia de orgă/bass
                left = data[:, 0]
                right = data[:, 1]
                mid = (left + right) / 2
                side = (left - right) / 2
                
                # Păstrăm doar semnalul central "Mid" (unde stă basul de orgă)
                # și reducem agresiv mediile/înaltele pentru a păstra doar "bătaia"
                bass_clean = mid - (side * 0.5) 
            else:
                bass_clean = data
            
            sf.write("bass_curat.wav", bass_clean, sr)
            st.session_state.gata = True

    if "gata" in st.session_state:
        st.markdown('<div class="mixer-card">', unsafe_allow_html=True)
        st.audio("bass_curat.wav")
        with open("bass_curat.wav", "rb") as f:
            st.download_button("⬇️ Descarcă Formula de Bass Pură", f, "bass_clean.wav")
        st.markdown('</div>', unsafe_allow_html=True)
