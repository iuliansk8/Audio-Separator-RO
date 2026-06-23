import streamlit as st
import requests
import os

st.set_page_config(page_title="Studio P-Bass AI Mixer", page_icon="🎸", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    body { background-color: #000000; }
    h1 { color: #ffffff; text-align: center; font-family: 'Helvetica Neue', sans-serif; font-size: 2rem; font-weight: bold; }
    p.subtitle { text-align: center; color: #888888; font-size: 1rem; margin-bottom: 25px; }
    .mixer-card { background-color: #0b0b0c; border: 1px solid #1c1c1e; border-radius: 16px; padding: 25px; margin-top: 15px; }
    .channel-box { background-color: #141416; border-radius: 12px; padding: 15px; margin-bottom: 15px; border: 1px solid #232326; }
    .stButton>button { width: 100%; background-color: #10b981 !important; color: white !important; font-weight: bold; border-radius: 12px; border: none; padding: 14px; font-size: 1.1rem; }
    .master-btn>div>button { background-color: #3b82f6 !important; font-size: 1.3rem; padding: 16px; }
    </style>
""", unsafe_allow_html=True)

st.title("🎸 Studio P-Bass AI Mixer")
st.markdown("<p class='subtitle'>Linie de Bas Izolată prin AI + Sincronizare Perfectă la Redare</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Încarcă fișierul audio (MP3 sau WAV)", type=["mp3", "wav"])

if uploaded_file is not None:
    original_path = "song_original.wav"
    bass_ai_path = "bass_pure_ai.wav"

    if st.button("🚀 Extrage Linia de Bas Pură prin AI"):
        with st.spinner("Inteligența Artificială izolează acum linia de bas..."):
            try:
                # Trimitem piesa la procesorul AI extern rapid
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                r = requests.post("https://api.audiostrip.co.uk/v1/separate/htdemucs", files=files, timeout=120)
                
                if r.status_code == 200:
                    data = r.json()
                    
                    # Salvăm piesa originală
                    with open(original_path, "wb") as f:
                        f.write(uploaded_file.getvalue())
                        
                    # Descărcăm doar basul izolat complet de AI
                    bass_url = data.get("bass")
                    if bass_url:
                        bass_bytes = requests.get(bass_url).content
                        with open(bass_ai_path, "wb") as f:
                            f.write(bass_bytes)
                            
                    st.success("🎉 Izolarea AI a fost finalizată cu succes!")
                else:
                    st.error("Serverul AI este ocupat. Reîncărcați și încercați din nou.")
            except Exception as e:
                st.error("A apărut o eroare la conexiunea cu algoritmul AI.")

    if os.path.exists(original_path) and os.path.exists(bass_ai_path):
        st.write("---")
        
        # SCRIPT JAVASCRIPT PENTRU SINCRONIZARE PERFECTĂ FĂRĂ BLOCAJE DE SERVER
        st.components.v1.html("""
        <script>
        function playBoth() {
            var audios = window.parent.document.getElementsByTagName('audio');
            for(var i=0; i<audios.length; i++){
                audios[i].currentTime = Math.max(audios[0].currentTime, audios[1].currentTime);
                audios[i].play();
            }
        }
        function pauseBoth() {
            var audios = window.parent.document.getElementsByTagName('audio');
            for(var i=0; i<audios.length; i++){
                audios[i].pause();
            }
        }
        </script>
        <div style="display: flex; gap: 10px; justify-content: center;">
            <button onclick="playBoth()" style="background-color: #10b981; color: white; border: none; padding: 12px 30px; font-weight: bold; border-radius: 8px; cursor: pointer; font-size: 16px;">▶️ PORNEȘTE AMÂNDOUĂ (Sincronizat)</button>
            <button onclick="pauseBoth()" style="background-color: #ef4444; color: white; border: none; padding: 12px 30px; font-weight: bold; border-radius: 8px; cursor: pointer; font-size: 16px;">⏸️ PAUZĂ COMUNĂ</button>
        </div>
        """, height=60)

        st.markdown('<div class="mixer-card">', unsafe_allow_html=True)
        
        # CANALUL 1
        st.markdown('<div class="channel-box">', unsafe_allow_html=True)
        st.markdown("### 🎵 1. Melodia Completă")
        st.audio(original_path)
        st.markdown('</div>', unsafe_allow_html=True)

        # CANALUL 2
        st.markdown('<div class="channel-box">', unsafe_allow_html=True)
        st.markdown("### 🎸 2. Doar Linia de Bas (AI P-BASS)")
        st.audio(bass_ai_path)
        with open(bass_ai_path, "rb") as f:
            st.download_button("⬇️ Descarcă linia de bas curată", f, "bass_ai.wav")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
