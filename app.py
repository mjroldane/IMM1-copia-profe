import streamlit as st
import os
import time
import glob
from gtts import gTTS
from langdetect import detect, DetectorFactory
from PIL import Image
import PyPDF2

# Para que los resultados de detección sean consistentes
DetectorFactory.seed = 0

if not os.path.exists("temp"):
    os.makedirs("temp")

st.title("🔊 Lector Inteligente Accesible")

with st.sidebar:
    st.header("Configuración de Voz")
    # Añadimos la opción de Autodetectar
    modo = st.selectbox(
        "Idioma de lectura:",
        ["Autodetectar", "Español", "English", "Français"]
    )
    
    mapa_idiomas = {
        "Español": "es",
        "English": "en",
        "Français": "fr"
    }

# --- ENTRADA DE DATOS ---
uploaded_file = st.file_uploader("Sube un PDF o TXT", type=["pdf", "txt"])
text_input = st.text_area("O pega el texto aquí:", height=150)

final_text = ""
if uploaded_file:
    if uploaded_file.type == "text/plain":
        final_text = str(uploaded_file.read(), "utf-8")
    else:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            final_text += page.extract_text()
elif text_input:
    final_text = text_input

# --- PROCESAMIENTO ---
if st.button("🔊 GENERAR AUDIO", use_container_width=True):
    if final_text.strip():
        # Lógica de detección de idioma
        if modo == "Autodetectar":
            try:
                lang_detected = detect(final_text)
                # Validamos que el idioma detectado esté soportado por nuestra app
                lg = lang_detected if lang_detected in ['es', 'en', 'fr'] else 'es'
                nombre_idioma = "detectado automáticamente"
            except:
                lg = 'es'
                nombre_idioma = "por defecto (Español)"
        else:
            lg = mapa_idiomas[modo]
            nombre_idioma = modo

        with st.spinner(f"Procesando en idioma {nombre_idioma}..."):
            tts = gTTS(final_text, lang=lg)
            nombre_archivo = f"temp/audio_{int(time.time())}.mp3"
            tts.save(nombre_archivo)
            
            st.success(f"Audio listo (Idioma: {lg})")
            with open(nombre_archivo, "rb") as f:
                st.audio(f.read(), format="audio/mp3")
    else:
        st.error("No hay texto para leer.")

# Limpieza básica
def clean_temp():
    files = glob.glob("temp/*.mp3")
    for f in files:
        if os.stat(f).st_mtime < time.time() - 3600: # Borra archivos de más de 1 hora
            os.remove(f)
clean_temp()
