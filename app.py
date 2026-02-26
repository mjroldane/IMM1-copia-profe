import streamlit as st
import os
import time
import glob
from gtts import gTTS
from langdetect import detect, DetectorFactory
from PIL import Image
import PyPDF2

# 1. Configuración de página (Limpio, sin CSS inyectado)
st.set_page_config(
    page_title="Lector de Documentos",
    page_icon="🔊",
    layout="centered"
)

# Configuración de consistencia para la detección
DetectorFactory.seed = 0

if not os.path.exists("temp"):
    os.makedirs("temp")

# 2. Encabezado
st.title("🔊 Lector Inteligente de Documentos")
st.markdown("Herramienta de accesibilidad para convertir texto y archivos a audio.")

# 3. Barra Lateral
with st.sidebar:
    st.header("Configuración")
    modo = st.selectbox(
        "Idioma de lectura:",
        ["Autodetectar", "Español", "English", "Français"]
    )
    
    st.write("---")
    if st.button("🗑️ Limpiar Pantalla"):
        st.rerun()

# 4. Entrada de Datos
st.subheader("1. Carga tu contenido")
uploaded_file = st.file_uploader("Sube un PDF o TXT", type=["pdf", "txt"])
text_input = st.text_area("O pega el texto aquí:", height=200, placeholder="Escribe algo...")

# Lógica para extraer texto
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

# 5. Procesamiento y Audio
st.write("---")
if st.button("🔊 CONVERTIR A AUDIO", use_container_width=True):
    if final_text.strip():
        # Detección de idioma
        if modo == "Autodetectar":
            try:
                lg_detected = detect(final_text)
                lg = lg_detected if lg_detected in ['es', 'en', 'fr'] else 'es'
                info_msg = f"Idioma detectado: {lg.upper()}"
            except:
                lg = 'es'
                info_msg = "No se pudo detectar, usando Español por defecto."
        else:
            mapa = {"Español": "es", "English": "en", "Français": "fr"}
            lg = mapa[modo]
            info_msg = f"Idioma seleccionado: {modo}"

        with st.spinner("Generando audio..."):
            tts = gTTS(final_text, lang=lg)
            path = f"temp/audio_{int(time.time())}.mp3"
            tts.save(path)
            
            st.info(info_msg)
            with open(path, "rb") as f:
                audio_bytes = f.read()
            st.audio(audio_bytes, format="audio/mp3")
            
            st.download_button(
                label="📥 Descargar MP3",
                data=audio_bytes,
                file_name="lectura.mp3",
                mime="audio/mp3"
            )
    else:
        st.warning("Por favor, introduce algún texto primero.")

# Limpieza automática
def clean_temp():
    for f in glob.glob("temp/*.mp3"):
        if os.stat(f).st_mtime < time.time() - 3600:
            os.remove(f)
clean_temp()
