import os
import streamlit as st
import soundfile as sf
import yt_dlp
from audio_separator.separator import Separator

st.set_page_config(page_title="AI Audio Separator Pro", page_icon="🎛️", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0f172a; color: white; }
    h1 { color: #38bdf8; text-align: center; font-family: 'Helvetica Neue', sans-serif; font-size: 2.3rem; font-weight: bold; }
    p.subtitle { text-align: center; color: #94a3b8; font-size: 1.1rem; }
    .stButton>button { width: 100%; background-color: #0284c7 !important; color: white !important; font-weight: bold; border-radius: 8px; border: none; padding: 12px; }
    .stButton>button:hover { background-color: #0369a1 !important; }
    .track-box { background-color: #1e293b; padding: 12px; border-radius: 8px; margin-top: 15px; margin-bottom: 5px; border-left: 5px solid #38bdf8; }
    .track-title { font-size: 1.1rem; font-weight: bold; color: #f1f5f9; }
    </style>
""", unsafe_allow_html=True)

st.title("🎛️ AI Audio Separator Pro")
st.markdown("<p class='subtitle'>Sistem ultra-stabil bazat pe modele ONNX (UVR)</p>", unsafe_allow_html=True)

metoda = st.radio("Alege sursa audio:", ("Introduce un link de YouTube", "Încarcă fișier propriu (MP3/WAV)"))

cale_audio_intrare = "temp_input.wav"

# Resetăm fișierele vechi la pornire proaspătă
if 'procesat' not in st.session_state:
    st.session_state.procesat = False

if metoda == "Introduce un link de YouTube":
    youtube_url = st.text_input("Lipește link-ul de YouTube aici 👇", placeholder="https://www.youtube.com/watch?v=...")
    if youtube_url:
        if st.button("📥 Preia melodia de pe YouTube"):
            with st.spinner("Se descarcă de pe YouTube..."):
                try:
                    if os.path.exists(cale_audio_intrare):
                        os.remove(cale_audio_intrare)
                    ydl_opts = {
                        'format': 'bestaudio/best',
                        'outtmpl': 'temp_input.%(ext)s',
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'wav',
                            'preferredquality': '192',
                        }],
                        'keepvideo': False,
                    }
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([youtube_url])
                    
                    if os.path.exists("temp_input.wav"):
                        st.success("✅ Melodia a fost preluată! Acum poți apăsa butonul de mai jos.")
                        st.session_state.procesat = False
                except Exception as e:
                    st.error(f"Eroare YouTube: {e}")

else:
    uploaded_file = st.file_uploader("Trage aici fișierul audio (MP3, WAV)", type=["mp3", "wav"])
    if uploaded_file is not None:
        if not os.path.exists(cale_audio_intrare):
            data, samplerate = sf.read(uploaded_file)
            sf.write(cale_audio_intrare, data, samplerate)
            st.session_state.procesat = False

# Procesarea efectivă
if os.path.exists(cale_audio_intrare):
    if st.button("🚀 Lansează Separarea AI"):
        with st.spinner("Se încarcă modelul ONNX ultra-light..."):
            try:
                # Curățăm piese vechi ca să nu se încurce
                for f in os.listdir('.'):
                    if f.startswith("Vocals_") or f.startswith("Instrumental_"):
                        os.remove(f)

                # Folosește modelul special decuplat care separă perfect Vocea de Instrumental fără să consume RAM
                separator = Separator()
                separator.load_model(model_filename='Kim_Vocal_2.onnx')
                
                st.write("Separare în curs...")
                output_files = separator.separate(cale_audio_intrare)
                
                # Redenumire pentru acces ușor
                for file in output_files:
                    if "Vocals" in file:
                        os.rename(file, "vocals_output.wav")
                    elif "Instrumental" in file:
                        os.rename(file, "instrumental_output.wav")
                
                st.session_state.procesat = True
                st.success("🎉 Separare completă!")
            except Exception as e:
                st.error(f"Eroare la procesare: {e}")

    # Afișare rezultate separate (Voce și Instrumentalul complet)
    if st.session_state.procesat and os.path.exists("vocals_output.wav") and os.path.exists("instrumental_output.wav"):
        st.write("---")
        st.subheader("🎛️ Rezultate Obținute")

        st.markdown('<div class="track-box"><div class="track-title">🎤 Voce (Vocals Only)</div></div>', unsafe_allow_html=True)
        st.audio("vocals_output.wav")
        with open("vocals_output.wav", "rb") as f:
            st.download_button("⬇️ Descarcă Vocea", f, "voce.wav", mime="audio/wav")

        st.markdown('<div class="track-box"><div class="track-title">🎸 Instrumental Complet (Tobe + Bas + Melodie)</div></div>', unsafe_allow_html=True)
        st.audio("instrumental_output.wav")
        with open("instrumental_output.wav", "rb") as f:
            st.download_button("⬇️ Descarcă Instrumentalul", f, "instrumental.wav", mime="audio/wav")
