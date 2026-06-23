import streamlit as st
import soundfile as sf
import numpy as np
import os
from scipy.signal import butter, lfilter

st.set_page_config(page_title="Studio P-Bass Mixer", page_icon="🎸", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    body { background-color: #000000; }
    h1 { color: #ffffff; text-align: center; font-family: 'Helvetica Neue', sans-serif; font-size: 2rem; font-weight: bold; }
    p.subtitle { text-align: center; color: #888888; font-size: 1rem; margin-bottom: 25px; }
    .mixer-card { background-color: #0b0b0c; border: 1px solid #1c1c1e; border-radius: 16px; padding: 25px; margin-top: 15px; }
    .slider-title { font-size: 1.1rem; font-weight: bold; color: #10b981; margin-top: 15px; }
    .stButton>button { width: 100%; background-color: #10b981 !important; color: white !important; font-weight: bold; border-radius: 12px; border: none; padding: 14px; font-size: 1.1rem; }
    </style>
""", unsafe_allow_html=True)

st.title("🎸 Studio P-Bass Mixer Pro")
st.markdown("<p class='subtitle'>Sincronizare Perfectă: Controlează Volumele dintr-un singur Play!</p>", unsafe_allow_html=True)

# Filtru acustic optimizat + amplificare x3 pentru un bas clar și foarte puternic
def extract_powerful_bass(data, fs, cutoff=300, order=4):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    bass = lfilter(b, a, data, axis=0)
    return bass * 3.5  # Amplificăm masiv linia de bas ca să se audă tare și clar

uploaded_file = st.file_uploader("Încarcă fișierul audio (MP3 sau WAV)", type=["mp3", "wav"])

if uploaded_file is not None:
    if st.button("🚀 Procesează și Sincronizează Canalele"):
        with st.spinner("Se izolează și se amplifică linia de bas..."):
            try:
                data, samplerate = sf.read(uploaded_file)
                
                # Dacă e stereo, lucrăm pe ambele canale
                if len(data.shape) > 1:
                    bass_data = np.zeros_like(data)
                    bass_data[:, 0] = extract_powerful_bass(data[:, 0], samplerate)
                    bass_data[:, 1] = extract_powerful_bass(data[:, 1], samplerate)
                else:
                    bass_data = extract_powerful_bass(data, samplerate)
                
                # Salvăm matricele în starea aplicației pentru mixerul live
                st.session_state.orig_data = data
                st.session_state.bass_data = bass_data
                st.session_state.rate = samplerate
                st.session_state.ready = True
            except Exception as e:
                st.error(f"Eroare la procesare: {e}")

    if "ready" in st.session_state and st.session_state.ready:
        st.write("---")
        st.markdown('<div class="mixer-card">', unsafe_allow_html=True)
        st.subheader("🎚️ Potențiometre Mixer Live")

        # Cele două glisoare de volum controlate în timp real
        vol_melodie = st.slider("🎵 Volum Melodie Originală", 0, 100, 80, key="v_mel")
        vol_bass = st.slider("🎸 Volum Linie de Bas (TARI ȘI CLAR)", 0, 200, 150, key="v_bas") # Permite boost până la 200%

        # Combinăm matematic cele două canale în funcție de poziția sliderelor tale
        factor_mel = vol_melodie / 100.0
        factor_bass = vol_bass / 100.0
        
        # Mixajul live direct în player
        mixed_data = (st.session_state.orig_data * factor_mel) + (st.session_state.bass_data * factor_bass)
        
        # Limităm semnalul ca să nu distorsioneze difuzoarele (clipping protection)
        mixed_data = np.clip(mixed_data, -1.0, 1.0)
        
        # Exportăm mixul rezultat într-un fișier temporar pe care îl asculți
        output_file = "studio_mix.wav"
        sf.write(output_file, mixed_data, st.session_state.rate)

        st.markdown('<p class="slider-title">🎧 Player Audio Unic (Apasă Play și ambele pornesc deodată):</p>', unsafe_allow_html=True)
        st.audio(output_file)
        
        with open(output_file, "rb") as f:
            st.download_button("⬇️ Descarcă Mixul Tău Custom (.wav)", f, "mix_studio.wav")

        st.markdown('</div>', unsafe_allow_html=True)
