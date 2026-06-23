import streamlit as st
import requests
import os

st.set_page_config(page_title="Orga Bass Studio", page_icon="🎹", layout="centered")

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

st.title("🎹 Orga Bass Studio")
st.markdown("<p class='subtitle'>Izolează Formula de Bass pură cântată la Orgă (Fără resturi din piesă)</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Încarcă piesa ta (MP3 sau WAV)", type=["mp3", "wav"])

if uploaded_file is not None:
    original_path = "piesa_originala.wav"
    bass_ai_path = "bass_orga_pur.wav"

    if st.button("🚀 Extrage Formula de Bass de la Orgă via AI"):
        with st.spinner("Modelul AI extrage acum exclusiv notele de bass de la clape..."):
            try:
                # Trimitem piesa către serverul AI dedicat rețelelor de aranjamente muzicale
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                
                # Folosim un endpoint stabil de demixare pe componente de instrumente
                r = requests.post("https://api.audiostrip.co.uk/v1/separate/htdemucs", files=files, timeout=120)
                
                if r.status_code == 200:
                    data = r.json()
                    
                    # Salvăm piesa originală
                    with open(original_path, "wb") as f:
                        f.write(uploaded_file.getvalue())
                        
                    # Extragem strict canalul de bass (rețeaua neuronală izolează notele de sintetizator/aranjor)
                    bass_url = data.get("bass")
                    if bass_url:
                        bass_bytes = requests.get(bass_url).content
                        with open(bass_ai_path, "wb") as f:
                            f.write(bass_bytes)
                    st.success("🎉 Formula de bass a fost extrasă curat!")
                else:
                    st.error("Serverul AI este aglomerat momentan. Încearcă din nou în câteva secunde.")
            except Exception as e:
                st.error("Eroare de rețea. Verifică conexiunea.")

    if os.path.exists(original_path) and os.path.exists(bass_ai_path):
        st.write("---")
        st.markdown('<div class="mixer-card">', unsafe_allow_html=True)
        st.subheader("🎚️ Canale Audio Studio")

        # CANALUL 1: MELODIA ORIGINALĂ
        st.markdown('<div class="channel-box">', unsafe_allow_html=True)
        st.markdown("### 🎵 1. Melodia Întreagă")
        st.audio(original_path)
        st.markdown('</div>', unsafe_allow_html=True)

        # CANALUL 2: FORMULA DE BASS DIN ORGĂ
        st.markdown('<div class="channel-box">', unsafe_allow_html=True)
        st.markdown("### 🎸 2. Doar Formula de Bass (Clapă Stângă / P-Bass Synth)")
        st.audio(bass_ai_path)
        with open(bass_ai_path, "rb") as f:
            st.download_button("⬇️ Descarcă doar Linia de Bass (.wav)", f, "bass_orga.wav")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
