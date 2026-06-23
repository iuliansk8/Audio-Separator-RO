import os
import streamlit as st
import soundfile as sf
import torch

# Păcălim Demucs și Torchaudio atât la ÎNCĂRCARE, cât și la SALVARE
import demucs.separate
import torchaudio

def _incarcare_audio_simpla(track, channels=2, samplerate=44100):
    data, sr = sf.read(str(track), always_2d=True)
    tensor = torch.tensor(data.T, dtype=torch.float32)
    return tensor

def _salvare_audio_simpla(filepath, src, sample_rate, channels_first=True, bits_per_sample=16, format=None, encoding=None):
    data = src.cpu().transpose(0, 1).numpy() if channels_first else src.cpu().numpy()
    sf.write(str(filepath), data, sample_rate)

# Suprascriem funcțiile problematice din sistem
demucs.separate.load_track = lambda track, *args, **kwargs: _incarcare_audio_simpla(track)
torchaudio.load = lambda track, *args, **kwargs: (_incarcare_audio_simpla(track), 44100)
torchaudio.save = _salvare_audio_simpla

st.set_page_config(page_title="AI Audio Separator", page_icon="🎵", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0f172a; color: white; }
    h1 { color: #38bdf8; text-align: center; font-family: 'Helvetica Neue', sans-serif; }
    p { text-align: center; color: #94a3b8; }
    </style>
""", unsafe_allow_html=True)

st.title("🎵 AI Audio Separator")
st.write("Încarcă o melodie și selectează instrumentul pe care vrei să îl izolezi!")

uploaded_file = st.file_uploader("Trage aici fișierul audio (MP3, WAV)", type=["mp3", "wav"])

option = st.selectbox(
    "Ce dorești să extragi din melodie?",
    ("Doar Vocea (Vocals)", "Doar Toba (Drums)", "Doar Basul (Bass)", "Doar Chitara (Guitar)", "Doar Clapele (Piano)")
)

mapping = {
    "Doar Vocea (Vocals)": "vocals",
    "Doar Toba (Drums)": "drums",
    "Doar Basul (Bass)": "bass",
    "Doar Chitara (Guitar)": "guitar",
    "Doar Clapele (Piano)": "piano"
}

if uploaded_file is not None:
    st.audio(uploaded_file, format='audio/mp3')
    
    if st.button("🚀 Separă Instrumentul Acum"):
        with st.spinner("Inteligența Artificială procesează melodia... Te rugăm să aștepți."):
            try:
                input_filename = "temp_input.wav"
                data, samplerate = sf.read(uploaded_file)
                sf.write(input_filename, data, samplerate)
                
                from demucs import separate
                separate.main(["-n", "htdemucs_6s", input_filename])
                
                instrument_name = mapping[option]
                result_path = f"separated/htdemucs_6s/temp_input/{instrument_name}.wav"
                
                if os.path.exists(result_path):
                    st.success("🎉 Procesare finalizată cu succes!")
                    with open(result_path, "rb") as audio_file:
                        st.audio(audio_file.read(), format='audio/wav')
                        st.download_button(
                            label="⬇️ Descarcă fișierul separat",
                            data=audio_file,
                            file_name=f"{instrument_name}_izolat.wav",
                            mime="audio/wav"
                        )
                else:
                    st.error("Modelul AI a terminat, dar fișierul nu a fost generat corect.")
            
            except Exception as e:
                st.error("A apărut o eroare la procesare.")
                st.exception(e)