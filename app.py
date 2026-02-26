import streamlit as st
import os
import time
import glob
from gtts import gTTS
from langdetect import detect, DetectorFactory
from PIL import Image
import PyPDF2

# Configuración de consistencia para la detección
DetectorFactory.seed = 0

if not os.path.exists("temp"):
    os.makedirs("temp")

# --- INTERFAZ PRINCIPAL ---
st.set_page_config(page_title="Asistente de Voz Accesible", page_icon="🔊")

st.title("🔊 Lector Inteligente Accesible")

# Sección de información de idiomas permitidos
with st.expander("🌐 Ver idiomas soportados", expanded=True):
    st.markdown("""
    Esta aplicación puede leer y detectar automáticamente los siguientes idiomas:
    * **Español** (Castellano)
    * **Inglés** (English)
    * **Francés** (Français)
    
    *Nota: Si el sistema detecta otro idioma, intentará leerlo con la configuración en Español por defecto.*
    """)

with st.sidebar:
    st.header("Panel de Control")
    modo = st.selectbox(
        "Preferencia de idioma:",
        ["Autodetectar", "Español", "English", "Français"],
        help="Selecciona 'Autodetectar' para que la IA identifique el idioma del texto por ti."
    )
    
    # Botón para limpiar todo
    if st.button("🗑️ Limpiar Pantalla y Archivos"):
        st.cache_data.clear()
        st.rerun()

    mapa_idiomas = {"Español": "es", "English": "en", "Français": "fr"}

# --- ENTRADA DE DATOS ---
st.subheader("1. Proporciona el texto")
uploaded_file = st.file_uploader("Sube un archivo (PDF o TXT)", type=["pdf", "txt"])

# Usamos una clave (key) para poder limpiar el text_area si fuera necesario
text_input = st.text_area("O escribe/pega el texto aquí:", height=150, key="input_texto")

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
if st.button("🔊 CONVERTIR A VOZHORA", use_container_width=True):
    if final_text.strip():
        # Lógica de detección
        if modo == "Autodetectar":
            try:
                lang_detected = detect(final_text)
                lg = lang_detected if lang_detected in ['es', 'en', 'fr'] else 'es'
                nombre_idioma = f"Detección automática: {lg.upper()}"
            except:
                lg = 'es'
                nombre_idioma = "No detectado (usando Español)"
        else:
            lg = mapa_idiomas[modo]
            nombre_idioma = modo

        with st.spinner(f"Preparando voz para {nombre_idioma}..."):
            tts = gTTS(final_text, lang=lg)
            nombre_archivo = f"temp/audio_{int(time.time())}.mp3"
            tts.save(nombre_archivo)
            
            st.success(f"✅ Lectura lista en {nombre_idioma}")
            with open(nombre_archivo, "rb") as f:
                st.audio(f.read(), format="audio/mp3")
                
            # Opción de descarga accesible
            st.download_button("📥 Descargar Audio", data=open(nombre_archivo, "rb"), file_name="mi_lectura.mp3")
    else:
        st.warning("⚠️ No se encontró texto para procesar. Por favor escribe algo o sube un archivo.")

# Limpieza automática de archivos viejos
def clean_temp():
    now = time.time()
    for f in glob.glob("temp/*.mp3"):
        if os.stat(f).st_mtime < now - 3600:
            os.remove(f)
clean_temp()
