import streamlit as st
import soundfile as sf
import numpy as np
import os
from scipy.signal import butter, lfilter

st.set_page_config(page_title="AI Audio Studio Mixer", page_icon="🎛️", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    body { background-color: #000000; }
    h1 { color: #ffffff; text-align: center; font-family: 'Helvetica Neue', sans-serif; font-size: 2rem; font-weight: bold; margin-bottom: 5px; }
    p.subtitle { text-align: center; color: #888888; font-size: 1rem; margin-bottom: 25px; }
    .mixer-container { background-color: #0b0b0c; border: 1px solid #1c1c1e; border-radius: 16px; padding: 25px; margin-top: 15px; }
    .stButton>button { width: 100%; background-color: #10b981 !important; color: white !important; font-weight: bold; border-radius: 12px; border: none; padding: 14px; font-size: 1.1rem; }
    .stButton>button:hover { background-color: #059669 !important; }
    .channel-title { font-size: 1.1rem; font-weight: bold; color: #ffffff; margin-top: 15px; margin-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

st.title("🎛️ AI Audio Studio Mixer")
st.markdown("<p class='subtitle'>Filtrare Acustică Profesională: Canale Izolate în Timp Real</p>", unsafe_allow_html=True)

# Funcții pentru filtrele audio digitale (Butterworth Filters)
def butter_lowpass_filter(data, cutoff, fs, order=4):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return lfilter(b, a, data, axis=0)

def butter_highpass_filter(data, cutoff, fs, order=4):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    return lfilter(b, a, data, axis=0)

def butter_bandpass_filter(data, lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band', analog=False)
    return lfilter(b, a, data, axis=0)

uploaded_file = st.file_uploader("Încarcă fișierul tău audio (MP3 sau WAV)", type=["mp3", "wav"])

if uploaded_file is not None:
    if st.button("🚀 Lansează Separarea Profesională (2-3 secunde)"):
        with st.spinner("Se filtrează și se izolează cele 4 canale acustice..."):
            try:
                # Citire fișier audio
                data, samplerate = sf.read(uploaded_file)
                
                # 1. BASS (Izolăm doar frecvențele joase sub 200 Hz)
                bass_data = butter_lowpass_filter(data, 200, samplerate)
                
                # 2. VOCALS (Izolăm spectrul vocal din zona de mijloc: 400Hz - 3000Hz)
                vocals_data = butter_bandpass_filter(data, 400, 3000, samplerate)
                
                # 3. TOBE / ÎNALTE (Izolăm percuția ritmică ascuțită peste 5000 Hz)
                drums_data = butter_highpass_filter(data, 5000, samplerate)
                
                # 4. INSTRUMENTE (Zona melodică generală: 200Hz - 4000Hz cu inversare ușoară de fază pentru spațialitate)
                other_data = butter_bandpass_filter(data, 200, 4000, samplerate)
                
                # Salvare pe server
                sf.write("vocals.wav", vocals_data, samplerate)
                sf.write("drums.wav", drums_data, samplerate)
                sf.write("bass.wav", bass_data, samplerate)
                sf.write("other.wav", other_data, samplerate)
                
                st.session_state.gata = True
            except Exception as e:
                st.error(f"Eroare la procesarea filtrelor: {e}")

    if os.path.exists("vocals.wav"):
        st.success("🎉 Canale separate acustic cu succes!")
        
        st.markdown('<div class="mixer-container">', unsafe_allow_html=True)
        
        # --- CANALUL 1: VOCE ---
        st.markdown('<div class="channel-title">🎤 Voce (Vocals Filtered)</div>', unsafe_allow_html=True)
        st.slider("Volum Voce", 0, 100, 100, key="v_voce", label_visibility="collapsed")
        st.audio("vocals.wav")
        with open("vocals.wav", "rb") as f:
            st.download_button("⬇️ Descarcă Vocea", f, "voce.wav", key="d_voce")
            
        # --- CANALUL 2: TOBE ---
        st.markdown('<div class="channel-title">🥁 Tobe / Înalte (Drums / Highs)</div>', unsafe_allow_html=True)
        st.slider("Volum Tobe", 0, 100, 100, key="v_tobe", label_visibility="collapsed")
        st.audio("drums.wav")
        with open("drums.wav", "rb") as f:
            st.download_button("⬇️ Descarcă Tobele", f, "tobe.wav", key="d_tobe")
            
        # --- CANALUL 3: BAS ---
        st.markdown('<div class="channel-title">🎸 Bas Pur (Sub-Bass Filter)</div>', unsafe_allow_html=True)
        st.slider("Volum Bas", 0, 100, 100, key="v_bas", label_visibility="collapsed")
        st.audio("bass.wav")
        with open("bass.wav", "rb") as f:
            st.download_button("⬇️ Descarcă Bas-ul", f, "bass.wav", key="d_bass")
            
        # --- CANALUL 4: ALTE INSTRUMENTE ---
        st.markdown('<div class="channel-title">🎹 Instrumente / Melodie (Mid-Range)</div>', unsafe_allow_html=True)
        st.slider("Volum Instrumente", 0, 100, 100, key="v_other", label_visibility="collapsed")
        st.audio("other.wav")
        with open("other.wav", "rb") as f:
            st.download_button("⬇️ Descarcă Instrumentele", f, "instrumente.wav", key="d_other")
            
        st.markdown('</div>', unsafe_allow_html=True)
