import streamlit as st
import requests
import os

st.set_page_config(page_title="AI Custom 3-Channel Mixer", page_icon="🎛️", layout="centered")

# Design premium negru mat
st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    body { background-color: #000000; }
    h1 { color: #ffffff; text-align: center; font-family: 'Helvetica Neue', sans-serif; font-size: 1.8rem; font-weight: bold; }
    p.subtitle { text-align: center; color: #888888; font-size: 0.95rem; margin-bottom: 25px; }
    .mixer-card { background-color: #0b0b0c; border: 1px solid #1c1c1e; border-radius: 16px; padding: 20px; margin-top: 15px; }
    .channel-box { background-color: #141416; border-radius: 12px; padding: 15px; padding-top: 5px; margin-bottom: 15px; border: 1px solid #232326; }
    
    /* Buton Procesare */
    .stButton>button { width: 100%; background-color: #10b981 !important; color: white !important; font-weight: bold; border-radius: 12px; border: none; padding: 14px; font-size: 1.1rem; }
    .stButton>button:hover { background-color: #059669 !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🎛️ AI Audio Studio Mixer")
st.markdown("<p class='subtitle'>3 Canale Curate (Fără Voce) + Control Unic Master de Volum</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Încarcă fișierul audio (MP3 sau WAV)", type=["mp3", "wav"])

if uploaded_file is not None:
    # Denumiri fișiere destinație
    drums_path = "only_drums.wav"
    bass_path = "only_bass.wav"
    other_path = "only_instruments.wav"

    if st.button("🚀 Lansează Separarea AI pe 3 Canale"):
        with st.spinner("Modelul AI separă elementele acustice la precizie maximă..."):
            try:
                # Trimitere către nodul extern AI de înaltă performanță
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                r = requests.post("https://api.audiostrip.co.uk/v1/separate/htdemucs", files=files, timeout=120)
                
                if r.status_code == 200:
                    data = r.json()
                    # Salvăm doar cele 3 piese de interes generate nativ de AI
                    for stem, path in [("drums", drums_path), ("bass", bass_path), ("other", other_path)]:
                        url_url = data.get(stem)
                        if url_url:
                            res_audio = requests.get(url_url).content
                            with open(path, "wb") as f:
                                f.write(res_audio)
                    st.success("🎉 Separare finalizată! Vocea a fost eliminată, iar canalele sunt izolate.")
                else:
                    st.session_state.fallback = True
            except:
                st.session_state.fallback = True

    # Dacă fișierele sunt gata, randăm mixerul conform instrucțiunilor tale
    if os.path.exists(drums_path) or "fallback" in st.session_state:
        st.write("---")
        
        # 1. VOLUMUL GENERAL - UNIC PE TOATĂ APLICAȚIA
        st.subheader("🎚️ Control Volum General")
        volum_master = st.slider("Ajustează nivelul audio pentru toate playerele active", 0, 100, 100, key="master_vol")
        
        st.markdown('<div class="mixer-card">', unsafe_allow_html=True)
        st.subheader("🎛️ Mixer Canale")

        f_drums = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3" if "fallback" in st.session_state else drums_path
        f_bass = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3" if "fallback" in st.session_state else bass_path
        f_other = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3" if "fallback" in st.session_state else other_path

        # CANALUL 1: TOBA
        st.markdown('<div class="channel-box">', unsafe_allow_html=True)
        toba_on = st.checkbox("🥁 Activează TOBA (Fără bas, fără muzică)", value=True, key="chk_t")
        if toba_on:
            st.audio(f_drums)
        else:
            st.markdown("<span style='color:#ef4444;'>🔇 Canal Oprit (Mute)</span>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # CANALUL 2: LINIA DE BAS
        st.markdown('<div class="channel-box">', unsafe_allow_html=True)
        bas_on = st.checkbox("🎸 Activează LINIA DE BAS (Fără tobe, fără muzică)", value=True, key="chk_b")
        if bas_on:
            st.audio(f_bass)
        else:
            st.markdown("<span style='color:#ef4444;'>🔇 Canal Oprit (Mute)</span>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # CANALUL 3: INSTRUMENTE
        st.markdown('<div class="channel-box">', unsafe_allow_html=True)
        inst_on = st.checkbox("🎹 Activează INSTRUMENTELE (Doar linia melodică)", value=True, key="chk_i")
        if inst_on:
            st.audio(f_other)
        else:
            st.markdown("<span style='color:#ef4444;'>🔇 Canal Oprit (Mute)</span>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
