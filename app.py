import streamlit as st
import os
import time
import glob
from gtts import gTTS
from langdetect import detect, DetectorFactory
from PIL import Image
import PyPDF2

# Configuración de página - ¡Debe ser el primer comando de Streamlit!
st.set_page_config(
    page_title="Lector Accesible",
    page_icon="🔊",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Configuración de consistencia para la detección de idioma
DetectorFactory.seed = 0

# Crear carpeta temporal si no existe
if not os.path.exists("temp"):
    os.makedirs("temp")

# ==============================================================================
# --- CORRECCIÓN DE CSS: ALTO CONTRASTE Y LEGIBILIDAD EXTREMA ---
# ==============================================================================
# Usamos colores que garantizan una relación de contraste superior a 7:1
st.markdown(
    """
    <style>
    /* 1. Fondo general de la aplicación */
    .stApp {
        background-color: #FDF6E3 !important; /* Crema muy suave */
    }
    
    /* 2. Color de todos los textos principales */
    /* Usamos !important para forzar el cambio en todos los elementos */
    h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown {
        color: #002B36 !important; /* Azul medianoche oscuro (Alto Contraste) */
    }
    p, span, label {
        font-weight: 500 !important; /* Un poco más grueso para leer mejor */
    }

    /* 3. Estilo para el área de texto (INPUT) */
    .stTextArea textarea {
        background-color: #FFFFFF !important; /* Fondo blanco puro */
        color: #000000 !important; /* Texto negro puro */
        border: 2px solid #073642 !important; /* Borde oscuro y visible */
        font-size: 18px !important; /* Letra más grande */
        font-family: Arial, sans-serif !important;
    }
    
    /* 4. Estilo para el uploader de archivos */
    [data-testid="stFileUploader"] {
        border: 2px solid #073642;
        padding: 1rem;
        border-radius: 10px;
        background-color: white;
    }
    
    /* 5. Estilo para el botón principal - Grande y visible */
    .stButton>button {
        background-color: #073642 !important; /* Fondo oscuro */
        color: white !important; /* Letra blanca */
        border-radius: 10px !important;
        padding: 1rem !important;
        font-weight: bold !important;
        font-size: 20px !important;
        border: none !important;
        width: 100% !important; /* Ocupa todo el ancho */
    }
    .stButton>button:hover {
        background-color: #002B36 !important; /* Fondo más oscuro al pasar el mouse */
    }
    
    /* 6. Estilo para la barra lateral */
    [data-testid="stSidebar"] {
        background-color: #EEE8D5 !important; /* Un tono crema más oscuro */
        color: #002B36 !important;
    }
    
    /* 7. Estilo para los mensajes de éxito/error */
    .stAlert {
        border-radius: 10px;
        border: 2px solid;
    }
    div[data-testid="stExpander"] {
        background-color: white;
        border: 1px solid #073642;
        border-radius: 10px;
        color: #002B36 !important;
    }
    div[data-testid="stExpander"] h1, 
    div[data-testid="stExpander"] h2, 
    div[data-testid="stExpander"] h3 {
        color: #002B36 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==============================================================================
# --- CUERPO DE LA APLICACIÓN: INTERFAZ MEJORADA ---
# ==============================================================================

# Encabezado principal
st.title("🔊 Lector Inteligente Accesible")

# Sección de Ayuda e Información de Idiomas
with st.expander("🌐 Ver Idiomas Soportados y Ayuda", expanded=True):
    st.markdown("""
    ### ¡Bienvenido!
    Esta herramienta lee textos en voz alta en los siguientes idiomas:
    * **Español**
    * **Inglés** (English)
    * **Francés** (Français)
    
    *Nota: Si el sistema detecta otro idioma, lo leerá con la configuración en Español por defecto.*
    
    He diseñado esta página con colores de **alto contraste** y un **fondo ameno** para reducir la fatiga visual.
    """)

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("Configuración de Voz")
    modo = st.selectbox(
        "Modo de Idioma:",
        ["Autodetectar", "Español", "English", "Français"],
        help="Selecciona 'Autodetectar' para que la IA identifique el idioma del texto."
    )
    
    mapa_idiomas = {"Español": "es", "English": "en", "Français": "fr"}

    st.write("---")
    # Botón para limpiar todo
    if st.button("🗑️ Limpiar Pantalla"):
        # Esto reinicia la app para limpiar los campos
        st.rerun()

# --- ÁREA DE TRABAJO (CENTRO) ---
st.subheader("1. Proporciona el Contenido")

uploaded_file = st.file_uploader(
    "Sube un archivo de documento (PDF o TXT):", 
    type=["pdf", "txt"],
    key="file_uploader" # Clave única para facilitar la limpieza
)

# Usamos una clave (key) para el text_area
text_input = st.text_area(
    "O escribe/pega el texto directamente aquí:", 
    height=250, 
    key="input_texto",
    placeholder="Escribe algo aquí..."
)

# --- LÓGICA DE EXTRACCIÓN DE TEXTO ---
final_text = ""
if uploaded_file:
    if uploaded_file.type == "text/plain":
        # Manejo de archivos de texto plano
        try:
            final_text = str(uploaded_file.read(), "utf-8")
            st.success("✅ Texto extraído del archivo TXT con éxito.")
        except:
            st.error("❌ Error al leer el archivo TXT. Asegúrate de que use codificación UTF-8.")
    else:
        # Manejo de archivos PDF
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            texto_pdf = ""
            for page in pdf_reader.pages:
                texto_pdf += page.extract_text()
            
            # Limpieza básica para PDFs que a veces tienen caracteres raros
            final_text = " ".join(texto_pdf.split())
            st.success("✅ Texto extraído del archivo PDF con éxito.")
        except:
            st.error("❌ Error al leer el archivo PDF. El archivo podría estar protegido o corrupto.")

# Si hay archivo, priorizamos ese texto; si no, usamos el del área de texto
if not final_text and text_input:
    final_text = text_input

st.write("---")
# --- SECCIÓN DE ACCIÓN Y RESULTADOS ---
st.subheader("2. Generar y Escuchar")

# Botón grande y visible para la acción principal
convertir_btn = st.button("🔊 CONVERTIR A AUDIO AHORA", use_container_width=True)

if convertir_btn:
    if final_text and final_text.strip():
        # Lógica de detección o selección de idioma
        if modo == "Autodetectar":
            try:
                lang_detected = detect(final_text)
                # Validamos que el idioma detectado esté soportado
                lg = lang_detected if lang_detected in ['es', 'en', 'fr'] else 'es'
                nombre_idioma = f"Detección automática: {lg.upper()}"
            except:
                # Fallback seguro en caso de error
                lg = 'es'
                nombre_idioma = "No se pudo detectar (usando Español)"
        else:
            lg = mapa_idiomas[modo]
            nombre_idioma = modo

        with st.spinner(f"Preparando la voz en {nombre_idioma}... Por favor espera."):
            try:
                # Convertir texto a audio
                tts = gTTS(final_text, lang=lg)
                nombre_archivo = f"temp/audio_{int(time.time())}.mp3"
                tts.save(nombre_archivo)
                
                # Feedback visual y reproductor de audio
                st.write(f"### Tu audio en {nombre_idioma} está listo:")
                with open(nombre_archivo, "rb") as f:
                    audio_bytes = f.read()
                st.audio(audio_bytes, format="audio/mp3", start_time=0)
                
                st.success("✅ ¡Conversión completada con éxito!")
                
                # Opción de descarga accesible
                st.download_button(
                    label="📥 Descargar archivo de audio MP3",
                    data=audio_bytes,
                    file_name=f"lectura_asistida_{lg}_{int(time.time())}.mp3",
                    mime="audio/mp3",
                    help="Guarda el audio para escucharlo más tarde."
                )
            except:
                st.error("❌ Ocurrió un error inesperado al generar el audio. El texto podría ser demasiado largo.")
    else:
        st.warning("⚠️ No se encontró texto para procesar. Por favor escribe algo o sube un archivo.")

# --- LIMPIEZA AUTOMÁTICA DE ARCHIVOS ANTIGUOS ---
def clean_temp_files():
    """Borra archivos MP3 antiguos de la carpeta temp."""
    now = time.time()
    for f in glob.glob("temp/*.mp3"):
        # Borra archivos que tengan más de 1 hora de antigüedad
        if os.stat(f).st_mtime < now - 3600:
            os.remove(f)
            # print(f"Limpieza: Archivo {f} borrado.")

clean_temp_files()
