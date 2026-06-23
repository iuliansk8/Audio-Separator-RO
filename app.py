import os
import streamlit as st
import soundfile as sf

st.set_page_config(page_title="AI Audio Separator Ultra-Light", page_icon="⚡", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0f172a; color: white; }
    h1 { color: #10b981; text-align: center; font-family: 'Helvetica Neue', sans-serif; font-size: 2.3rem; font-weight: bold; }
    p.subtitle { text-align: center; color: #94a3b8; font-size: 1.1rem; }
    .stButton>button { width: 100%; background-color: #10b981 !important; color: white !important; font-weight: bold; border-radius: 8px; border: none; padding: 12px; font-size: 1.1rem; }
    .stButton>button:hover { background-color: #059669 !important; }
    .track-box { background-color: #1e293b; padding: 12px; border-radius: 8px; margin-top: 15px; margin-bottom: 5px; border-left: 5px solid #10b981; }
    .track-title { font-size: 1.1rem; font-weight: bold; color: #f1f5f9; }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ AI Audio Separator Ultra-Light")
st.markdown("<p class='subtitle'>Separare rapidă (Voce / Instrumental) fără erori de memorie</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Încarcă fișierul tău audio (MP3 sau WAV)", type=["mp3", "wav"])

cale_intrare = "input_piesa.wav"

if uploaded_file is not None:
    if not os.path.exists(cale_intrare):
        data, samplerate = sf.read(uploaded_file)
        sf.write(cale_intrare, data, samplerate)
        if os.path.exists("output_audio"):
            import shutil
            shutil.rmtree("output_audio")

    if st.button("🚀 Lansează Separarea AI (Aproximativ 20-30 secunde)"):
        with st.spinner("Modelul ultra-light procesează canalele..."):
            try:
                # Folosim spleeter direct din terminal pentru eficiență maximă și izolare de RAM
                os.system(f"python -m spleeter separate -p spleeter:2stems -o output_audio {cale_intrare}")
                st.success("🎉 Separare completă!")
            except Exception as e:
                st.error(f"Eroare la procesare: {e}")

    # Căile standard unde salvează spleeter:2stems
    cale_vocals = "output_audio/input_piesa/vocals.wav"
    cale_accompaniment = "output_audio/input_piesa/accompaniment.wav"

    if os.path.exists(cale_vocals) and os.path.exists(cale_accompaniment):
        st.write("---")
        st.subheader("🎛️ Canale Audio Separate")

        st.markdown('<div class="track-box"><div class="track-title">🎤 Voce (Vocals Only)</div></div>', unsafe_allow_html=True)
        st.audio(cale_vocals)
        with open(cale_vocals, "rb") as f:
            st.download_button("⬇️ Descarcă Vocea", f, "voce.wav", mime="audio/wav")

        st.markdown('<div class="track-box"><div class="track-title">🎸 Instrumental Complet (Negative)</div></div>', unsafe_allow_html=True)
        st.audio(cale_accompaniment)
        with open(cale_accompaniment, "rb") as f:
            st.download_button("⬇️ Descarcă Instrumentalul", f, "instrumental.wav", mime="audio/wav")
