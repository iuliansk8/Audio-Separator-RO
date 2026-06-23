import streamlit as st
import soundfile as sf
import numpy as np
import os

st.set_page_config(page_title="Pro Bass Formula Studio", page_icon="🎹", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    .mixer-card { background-color: #1a1a1a; padding: 25px; border-radius: 15px; }
    </style>
""", unsafe_allow_html=True)

st.title("🎹 Studio: Extracție Formula de Bass")

uploaded_file = st.file_uploader("Încarcă melodia", type=["mp3", "wav"])

if uploaded_file is not None:
    if st.button("🚀 Extrage Formula de atac (Percuție Bass)"):
        data, sr = sf.read(uploaded_file)
        
        # Facem un mix mono pentru analiză
        mono = np.mean(data, axis=1) if len(data.shape) > 1 else data
        
        # Detectăm "Formula" - extragem atacurile (transientii) prin derivare
        # Asta izolează "bătaia" clapei, nu sunetul lung și bâzâit
        formula = np.diff(mono, prepend=0)
        formula = np.abs(formula) # Păstrăm doar atacul
        
        # Netezim ca să nu fie un bâzâit, ci o "lovitură" percutantă
        from scipy.ndimage import gaussian_filter1d
        formula = gaussian_filter1d(formula, sigma=200)
        
        # Normalizare și salvare
        formula = formula / np.max(np.abs(formula))
        sf.write("formula_bass.wav", formula, sr)
        sf.write("original.wav", data, sr)
        st.session_state.gata = True

    if "gata" in st.session_state:
        # Sincronizare prin HTML - ambele playere pornesc la același "Play"
        st.components.v1.html("""
        <div style="background:#1a1a1a; padding:20px; border-radius:15px;">
            <p>🎵 Melodia Originală:</p>
            <audio id="audio1" src="https://raw.githubusercontent.com/iuliansk8/audio-separator-ro/main/original.wav" controls style="width:100%"></audio>
            <p style="margin-top:20px;">🎹 Formula Bass (Bătaia):</p>
            <audio id="audio2" src="https://raw.githubusercontent.com/iuliansk8/audio-separator-ro/main/formula_bass.wav" controls style="width:100%"></audio>
            <button onclick="playAll()" style="width:100%; padding:15px; background:#10b981; border:none; color:white; font-weight:bold; cursor:pointer; margin-top:20px;">▶️ PORNEȘTE AMBELE SINCRONIZAT</button>
        </div>
        <script>
            function playAll() {
                document.getElementById('audio1').play();
                document.getElementById('audio2').play();
            }
        </script>
        """, height=300)
