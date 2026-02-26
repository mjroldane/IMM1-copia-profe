import streamlit as st
import os
import time
import glob
from gtts import gTTS
from langdetect import detect, DetectorFactory
from PIL import Image
import PyPDF2

# Configuración de página
st.set_page_config(page_title="Lector Accesible", layout="centered")

# --- DISEÑO DE ALTO CONTRASTE Y COLORES AMENOS ---
st.markdown(
    """
    <style>
    /* Fondo general de la aplicación (Color Crema) */
    .stApp {
        background-color: #FDF6E3;
    }
    
    /* Color de todos los textos principales (Azul muy oscuro) */
    h1, h2, h3, p, span, label {
        color: #002B36 !important;
        font-weight: 500;
    }

    /* Estilo para el área de texto (Blanco puro con borde marcado) */
    .stTextArea textarea {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 2px solid #073642 !important;
        font-size: 18px !important;
    }

    /* Estilo para los botones */
    .stButton>button {
        background-color: #073642 !important;
        color: white !important;
        border-radius: 10px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
    }
    
    /* Estilo para la barra lateral (Un tono un poco más oscuro para diferenciar) */
    [data-testid="stSidebar"] {
        background-color: #EEE8D5;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- INICIO DE LA APP ---
st.title("🔊 Lector Inteligente Accesible")

with st.expander("🌐 Idiomas y Ayuda", expanded=True):
    st.write("Esta herramienta lee textos en **Español, Inglés y Francés**.")
    st.write("El fondo crema y las letras oscuras están diseñados para reducir la fatiga visual.")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("Configuración")
    modo = st.selectbox(
        "Modo de Idioma:",
        ["Autodetectar", "Español", "English", "Français"]
    )
    
    if st.button("🗑️ Limpiar Todo"):
        st.rerun()

# --- CUERPO DE LA APP ---
uploaded_file = st.file_uploader("Sube un documento (PDF o TXT)", type=["pdf", "txt"])
text_input = st.text_area("O pega el texto aquí:", height=200, placeholder="Escribe algo aquí...")

# Lógica para extraer texto (simplificada para el ejemplo)
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

# --- GENERACIÓN DE AUDIO ---
if st.button("🔊 CONVERTIR Y ESCUCHAR", use_container_width=True):
    if final_text.strip():
        # Detección
        if modo == "Autodetectar":
            try:
                lg = detect(final_text)
                if lg not in ['es', 'en', 'fr']: lg = 'es'
            except:
                lg = 'es'
        else:
            mapa = {"Español": "es", "English": "en", "Français": "fr"}
            lg = mapa[modo]

        with st.spinner("Generando audio..."):
            tts = gTTS(final_text, lang=lg)
            # Creamos carpeta temp si no existe
            if not os.path.exists("temp"): os.makedirs("temp")
            path = f"temp/audio_{int(time.time())}.mp3"
            tts.save(path)
            
            st.audio(path)
            st.success(f"Lectura lista en idioma: {lg.upper()}")
    else:
        st.error("Por favor, ingresa un texto primero.")
