import streamlit as st
import os
import time
import glob
import base64
from gtts import gTTS
from PIL import Image
import PyPDF2  # Necesitarás instalarlo: pip install PyPDF2

# Configuración de la página para accesibilidad
st.set_page_config(page_title="Lector de Documentos Accesible", layout="centered")

st.title("🔊 Lector de Documentos para Asistencia Visual")

# Carpeta temporal
if not os.path.exists("temp"):
    os.makedirs("temp")

# --- FUNCIONES DE APOYO ---

def extraer_texto(archivo_subido):
    """Extrae texto de archivos TXT o PDF."""
    if archivo_subido.type == "text/plain":
        return str(archivo_subido.read(), "utf-8")
    elif archivo_subido.type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(archivo_subido)
        texto_completo = ""
        for pagina in pdf_reader.pages:
            texto_completo += pagina.extract_text()
        return texto_completo
    return None

def text_to_speech(text, lang):
    """Convierte texto a audio y lo guarda."""
    tts = gTTS(text, lang=lang)
    filename = f"temp/audio_{int(time.time())}.mp3"
    tts.save(filename)
    return filename

# --- INTERFAZ ---

with st.sidebar:
    st.header("Configuración de Voz")
    idioma = st.radio("Seleccione el idioma de lectura:", ("Español", "English"))
    lg = 'es' if idioma == "Español" else 'en'
    
    st.info("Esta herramienta permite subir archivos PDF o TXT para escucharlos en voz alta.")

# 1. Subida de archivos (Lo más útil para el usuario)
st.subheader("1. Sube tu archivo")
uploaded_file = st.file_uploader("Arrastra aquí tu PDF o archivo de texto", type=["pdf", "txt"])

# 2. Área de texto (Por si prefieren escribir)
st.subheader("2. O escribe el texto directamente")
text_input = st.text_area("Caja de texto:", height=200, placeholder="Escribe o pega algo aquí...")

# Determinar qué texto procesar
final_text = ""
if uploaded_file is not None:
    final_text = extraer_texto(uploaded_file)
    st.success("Archivo cargado con éxito.")
elif text_input:
    final_text = text_input

# 3. Botón de Procesamiento
if st.button("🔊 CONVERTIR Y ESCUCHAR", use_container_width=True):
    if final_text.strip() == "":
        st.warning("Por favor, sube un archivo o escribe algún texto primero.")
    else:
        with st.spinner("Generando audio... por favor espera."):
            archivo_audio = text_to_speech(final_text, lg)
            
            # Reproductor de audio
            st.markdown("### Tu audio listo:")
            with open(archivo_audio, "rb") as f:
                audio_bytes = f.read()
            st.audio(audio_bytes, format="audio/mp3")
            
            # Botón de descarga
            st.download_button(
                label="Descargar archivo de audio",
                data=audio_bytes,
                file_name="lectura_asistida.mp3",
                mime="audio/mp3"
            )

# Limpieza de archivos antiguos
def remove_old_files(n_days=1):
    mp3_files = glob.glob("temp/*.mp3")
    now = time.time()
    for f in mp3_files:
        if os.stat(f).st_mtime < now - (n_days * 86400):
            os.remove(f)

remove_old_files()
