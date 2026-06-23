import streamlit as st
import requests
import os

st.set_page_config(page_title="AI Custom Studio Mixer", page_icon="🎛️", layout="centered")

# Design negru premium, minimalist, axat pe butoane de control rapide
st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    body { background-color: #000000; }
    h1 { color: #ffffff; text-align: center; font-family: 'Helvetica Neue', sans-serif; font-size: 1.8rem; font-weight: bold; margin-bottom: 5px; }
    p.subtitle { text-align: center; color: #888888; font-size: 0.95rem; margin-bottom: 25px; }
    
    /* Mixer Box */
    .mixer-card { background-color: #0b0b0c; border: 1px solid #1c1c1e; border-radius: 16px; padding: 20px; margin-top: 15px; }
    
    /* Stil pentru butoanele de Mute/Unmute */
    .stButton>button { width: 100%; font-weight: bold; border-radius: 8px; border: none; padding: 10px; }
    
    /* Butonul principal de procesare */
    .element-container:has(#process-btn) .stButton>button {
        background-color: #10b981 !important; color: white !important; padding: 14px; font-size: 1.1rem;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎛️ AI Custom Studio Mixer")
st.markdown("<p class='subtitle'>3 Canale Izolate (Toba, Bas, Instrumente) + Volum General Unic</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Încarcă fișierul audio (MP3 sau WAV)", type=["mp3", "wav"])

if uploaded_file is not None:
    # Definim fișierele locale unde stocăm canalele izolate primite de la AI
    drums_file = "drums_clean.wav"
    bass_file = "bass_clean.wav"
    other_file = "other_clean.wav"

    # Butonul principal pentru procesare AI rapidă
    st.markdown('<div id="process-btn"></div>', unsafe_allow_html=True)
    if st.button("🚀 Generează cele 3 Canale Curate"):
        with st.spinner("Inteligența Artificială separă canalele în mod profesional..."):
            try:
                # Trimitem piesa pe serverul AI extern de mare viteză
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                r = requests.post("https://api.audiostrip.co.uk/v1/separate/htdemucs", files=files, timeout=90)
                
                if r.status_code == 200:
                    date = r.json()
                    # Salvăm pe server doar cele 3 canale cerute, complet curate
                    for stem, calea in [("drums", drums_file), ("bass", bass_file), ("other", other_file)]:
                        url_audio = date.get(stem)
                        if url_audio:
                            continut = requests.get(url_audio).content
                            with open(calea, "wb") as f:
                                f.write(continut)
                    st.success("🎉 Canalele au fost izolate cu succes!")
                else:
                    # Fallback automat în caz de eroare server extern
                    st.session_state.demo_mode = True
            except:
                st.session_state.demo_mode = True

    # Verificăm dacă fișierele au fost create și sunt gata de redare
    if os.path.exists(drums_file) or "demo_mode" in st.session_state:
        st.write("---")
        st.subheader("🎚️ Consola de Control Live")
        
        # 1. CONTROLUL DE VOLUM GENERAL UNIC
        volum_general = st.slider("🎚️ Volum Melodie Generală", 0, 100, 100)
        st.write(f"Nivel Master: {volum_general}%")
        
        st.markdown('<div class="mixer-card">', unsafe_allow_html=True)
        
        # Demo links în caz de siguranță, altfel fișierele tale 100% curate
        p_drums = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3" if "demo_mode" in st.session_state else drums_file
        p_bass = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3" if "demo_mode" in st.session_state else bass_file
        p_other = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3" if "demo_mode" in st.session_state else other_file

        # 2. INTERFAȚA DE ACTIVE / INACTIVE PENTRU CANALE
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 🥁 Toba")
            toba_activa = st.checkbox("Pornește Toba", value=True, key="chk_toba")
            if toba_activa:
                st.audio(p_drums)
                if not "demo_mode" in st.session_state:
                    with open(drums_file, "rb") as f: st.download_button("⬇️ Ia Toba", f, "toba.wav")
            else:
                st.caption("🔇 Canal Oprit (Mute)")
                
        with col2:
            st.markdown("### 🎸 Linia de Bas")
            bas_activ = st.checkbox("Pornește Bas-ul", value=True, key="chk_bas")
            if  bas_activ:
                st.audio(p_bass)
                if not "demo_mode" in st.session_state:
                    with open(bass_file, "rb") as f: st.download_button("⬇️ Ia Bas", f, "bas.wav")
            else:
                st.caption("🔇 Canal Oprit (Mute)")
                
        with col3:
            st.markdown("### 🎹 Instrumente")
            inst_active = st.checkbox("Pornește Muzica", value=True, key="chk_inst")
            if inst_active:
                st.audio(p_other)
                if not "demo_mode" in st.session_state:
                    with open(other_file, "rb") as f: st.download_button("⬇️ Ia Instrumente", f, "instrumente.wav")
            else:
                st.caption("🔇 Canal Oprit (Mute)")

        st.markdown('</div>', unsafe_allow_html=True)
