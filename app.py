import streamlit as st
import soundfile as sf
import numpy as np
import base64
import io

st.set_page_config(page_title="Studio Bass Direct", layout="centered")

st.title("🎹 Studio: Extracție Formula de Bass")

uploaded_file = st.file_uploader("Încarcă melodia (MP3/WAV)", type=["mp3", "wav"])

if uploaded_file is not None:
    # Folosim BytesIO pentru a ține totul în memorie, nu pe disc
    if st.button("🚀 PROCESEAZĂ ȘI PREGĂTEȘTE"):
        data, sr = sf.read(uploaded_file)
        
        # Extragem formula (atacul percutant)
        mono = np.mean(data, axis=1) if len(data.shape) > 1 else data
        formula = np.abs(np.diff(mono, prepend=0))
        from scipy.ndimage import gaussian_filter1d
        formula = gaussian_filter1d(formula, sigma=150)
        formula = formula / np.max(np.abs(formula))
        
        # Salvăm în memorie (BytesIO)
        orig_buf = io.BytesIO()
        bass_buf = io.BytesIO()
        sf.write(orig_buf, data, sr, format='WAV')
        sf.write(bass_buf, formula, sr, format='WAV')
        
        st.session_state.orig_b64 = base64.b64encode(orig_buf.getvalue()).decode()
        st.session_state.bass_b64 = base64.b64encode(bass_buf.getvalue()).decode()
        st.rerun()

# Dacă avem datele în sesiune, afișăm playerele
if "orig_b64" in st.session_state:
    st.markdown(f'''
        <div style="margin-bottom:20px; background:#1a1a1a; padding:15px; border-radius:10px;">
            <p>🎵 Melodia Originală:</p>
            <audio id="audio_orig" controls style="width:100%"><source src="data:audio/wav;base64,{st.session_state.orig_b64}" type="audio/wav"></audio>
            <p style="margin-top:20px;">🎹 Formula Bass (Bătaia de clape):</p>
            <audio id="audio_bass" controls style="width:100%"><source src="data:audio/wav;base64,{st.session_state.bass_b64}" type="audio/wav"></audio>
        </div>
        <button onclick="
            document.getElementById('audio_orig').play();
            document.getElementById('audio_bass').play();
        " style="width:100%; padding:20px; background:#10b981; border:none; color:white; font-size:20px; font-weight:bold; cursor:pointer; border-radius:10px;">
        ▶️ PORNEȘTE AMBELE SINCRONIZAT
        </button>
    ''', unsafe_allow_html=True)
else:
    st.info("Încarcă melodia și apasă butonul pentru a începe.")
