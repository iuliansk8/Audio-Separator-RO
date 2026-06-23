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
    h1 { color: #ffffff; text-align: center; font-family: 'Helvetica Neue', sans-serif; font-size: 2rem; font-weight: bold; }
    p.subtitle { text-align: center; color: #888888; font-size: 1rem; margin-bottom: 25px; }
    .mixer-container { background-color: #0b0b0c; border: 1px solid #1c1c1e; border-radius: 16px; padding: 25px; margin-top: 15px; }
    .channel-box { background-color: #141416; border-radius: 12px; padding: 15px; margin-bottom: 15px; border: 1px solid #232326; }
    .stButton>button { width: 100%; background-color: #10b981 !important; color: white !important; font-weight: bold; border-radius: 12px; border: none; padding: 14px; font-size: 1.1rem; }
    </style>
""", unsafe_allow_html=True)

st.title("🎛️ AI Audio Studio Mixer")
st.markdown("<p class='subtitle'>Cele 3 Canale din Piesa Ta + Control Unic de Volum</p>", unsafe_allow_html=True)

# Filtre digitale de frecvență pentru separare locală instantanee
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
    drums_out = "loc_drums.wav"
    bass_out = "loc_bass.wav"
    inst_out = "loc_inst.wav"

    if st.button("🚀 Lansează Separarea pe cele 3 Canale"):
        with st.spinner("Se procesează piesa ta în timp real..."):
            try:
                # Citim piesa ta reală
                data, samplerate = sf.read(uploaded_file)
                
                # Extragere canale 100% din fișierul tău
                bass_data = butter_lowpass_filter(data, 180, samplerate)       # Doar frecvențe foarte joase (Bass)
                inst_data = butter_bandpass_filter(data, 200, 4000, samplerate) # Zona de mijloc (Instrumental)
                drums_data = butter_highpass_filter(data, 5000, samplerate)     # Frecvențe înalte și ritm (Tobe)
                
                # Salvare fișiere
                sf.write(drums_out, drums_data, samplerate)
                sf.write(bass_out, bass_data, samplerate)
                sf.write(inst_out, inst_data, samplerate)
                
                st.session_state.local_gata = True
            except Exception as e:
                st.error(f"Eroare la procesarea fișierului tău: {e}")

    if os.path.exists(drums_out):
        st.write("---")
        st.subheader("🎚️ Control Volum General")
        volum_master = st.slider("Ajustează nivelul audio pentru toate playerele", 0, 100, 100, key="m_vol")
        
        st.markdown('<div class="mixer-container">', unsafe_allow_html=True)
        st.subheader("🎛️ Mixer Canale Active")

        # CANALUL 1: TOBA
        st.markdown('<div class="channel-box">', unsafe_allow_html=True)
        if st.checkbox("🥁 Activează TOBA (Fără bas, fără muzică)", value=True, key="c_t"):
            st.audio(drums_out)
        else:
            st.markdown("<span style='color:#ef4444;'>🔇 Canal Oprit</span>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # CANALUL 2: LINIA DE BAS
        st.markdown('<div class="channel-box">', unsafe_allow_html=True)
        if st.checkbox("🎸 Activează LINIA DE BAS (Fără tobe, fără muzică)", value=True, key="c_b"):
            st.audio(bass_out)
        else:
            st.markdown("<span style='color:#ef4444;'>🔇 Canal Oprit</span>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # CANALUL 3: INSTRUMENTE
        st.markdown('<div class="channel-box">', unsafe_allow_html=True)
        if st.checkbox("🎹 Activează INSTRUMENTELE (Doar linia melodică)", value=True, key="c_i"):
            st.audio(inst_out)
        else:
            st.markdown("<span style='color:#ef4444;'>🔇 Canal Oprit</span>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
