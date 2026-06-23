import streamlit as st
import soundfile as sf
import numpy as np
import base64
import os

st.set_page_config(page_title="Studio Bass Direct", layout="centered")

st.title("🎹 Studio: Extracție Formula de Bass")

uploaded_file = st.file_uploader("Încarcă melodia (MP3/WAV)", type=["mp3", "wav"])

if uploaded_file is not None:
    if st.button("🚀 PROCESEAZĂ ȘI PREGĂTEȘTE"):
        data, sr = sf.read(uploaded_file)
        
        # Extragem formula (atacul percutant)
        mono = np.mean(data, axis=1) if len(data.shape) > 1 else data
        formula = np.abs(np.diff(mono, prepend=0))
        from scipy.ndimage import gaussian_filter1d
        formula = gaussian_filter1d(formula, sigma=150)
        formula = formula / np.max(np.abs(formula))
        
        # Salvăm fișierele
        sf.write("orig.wav", data, sr)
        sf.write("bass.wav", formula, sr)
        st.rerun()

# Verificăm dacă fișierele există înainte de a le afișa
if os.path.exists("orig.wav") and os.path.exists("bass.wav"):
    def get_audio_html(path, label):
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        return f'''
        <div style="margin-bottom:20px; background:#1a1a1a; padding:15px; border-radius:10px;">
            <p style="color:#ffffff;">{label}</p>
            <audio id="{path}" controls style="width:100%"><source src="data:audio/wav;base64,{b64}" type="audio/wav"></audio>
        </div>'''
    
    st.markdown(get_audio_html("orig.wav", "🎵 Melodia Originală"), unsafe_allow_html=True)
    st.markdown(get_audio_html("bass.wav", "🎹 Formula Bass (Bătaia de clape)"), unsafe_allow_html=True)
    
    st.markdown('''
        <button onclick="
            document.getElementById('orig.wav').play();
            document.getElementById('bass.wav').play();
        " style="width:100%; padding:20px; background:#10b981; border:none; color:white; font-size:20px; font-weight:bold; cursor:pointer; border-radius:10px;">
        ▶️ PORNEȘTE AMBELE SINCRONIZAT
        </button>
    ''', unsafe_allow_html=True)
else:
    st.info("Apasă butonul de mai sus după ce încarci melodia.")
