import streamlit as st
import os
import time
import glob
from gtts import gTTS
from PIL import Image
import PyPDF2

# Configuración inicial
if not os.path.exists("temp"):
    os.makedirs("temp")

st.title("🔊 Lector Multilingüe Accesible")

# --- BARRA LATERAL PARA IDIOMAS ---
with st.sidebar:
    st.header("Configuración")
    
    # Añadimos Francés a las opciones
    idioma_nombre = st.radio(
        "Seleccione el idioma de lectura:",
        ("Español", "English", "Français")
    )
    
    # Diccionario de mapeo para gTTS
    mapa_idiomas = {
        "Español": "es",
        "English": "en",
        "Français": "fr"
    }
    lg = mapa_idiomas[idioma_nombre]
    
    st.write(f"Configurado en: **{idioma_nombre}**")

# --- LÓGICA DE CARGA ---
st.subheader("1. Carga de contenido")
uploaded_file = st.file_uploader("Sube un archivo (PDF o TXT)", type=["pdf", "txt"])
text_input = st.text_area("O pega el texto aquí:", height=150)

# Extraer texto si hay archivo
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

# --- BOTÓN DE ACCIÓN ---
if st.button("🔊 GENERAR AUDIO", use_container_width=True):
    if final_text.strip():
        with st.spinner(f"Generando voz en {idioma_nombre}..."):
            # Generar audio
            tts = gTTS(final_text, lang=lg)
            nombre_archivo = f"temp/audio_{lg}_{int(time.time())}.mp3"
            tts.save(nombre_archivo)
            
            # Reproducción
            st.success(f"¡Listo! Audio generado en {idioma_nombre}")
            with open(nombre_archivo, "rb") as f:
                st.audio(f.read(), format="audio/mp3")
    else:
        st.error("Por favor, ingresa texto o sube un archivo primero.")
