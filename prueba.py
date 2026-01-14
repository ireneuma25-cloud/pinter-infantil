import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io
import os

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Pinter Edu", page_icon="🧸", layout="wide")

# --- 2. SELECTOR DE MODO (En la barra lateral) ---
with st.sidebar:
    st.title("🎨 Personalización")
    tema = st.radio("Elige el modo de lectura:", ["Modo Claro ☀️", "Modo Oscuro 🌙"])
    st.markdown("---")

# --- 3. LÓGICA DE COLORES ---
if tema == "Modo Claro ☀️":
    color_fondo = "#FDFBF7"
    color_texto = "#4A4A4A"
    color_sidebar = "#F9F5EB"
    color_borde = "#F4D03F"
    color_burbuja = "#FFFFFF"
else:
    color_fondo = "#121212"
    color_texto = "#E0E0E0"
    color_sidebar = "#1E1E1E"
    color_borde = "#BB86FC"
    color_burbuja = "#2D2D2D"

# --- 4. APLICAR ESTILO CSS ---
estilo = f"""
<style>
    /* Fondo y texto general */
    .stApp {{
        background-color: {color_fondo} !important;
        color: {color_texto} !important;
    }}
    
    /* Barra lateral */
    section[data-testid="stSidebar"] {{
        background-color: {color_sidebar} !important;
    }}

    /* Títulos y textos */
    h1, h2, h3, p, span, label {{
        color: {color_texto} !important;
        font-family: 'Times New Roman', Times, serif;
    }}

    /* Burbujas del chat */
    .stChatMessage {{
        background-color: {color_burbuja} !important;
        border: 1px solid {color_borde} !important;
        color: {color_texto} !important;
        border-radius: 15px;
    }}

    /* Línea debajo del título */
    h1 {{
        border-bottom: 2px solid {color_borde};
        padding-bottom: 10px;
    }}
</style>
"""
st.markdown(estilo, unsafe_allow_html=True)

# --- 5. CLAVE DE GOOGLE (Caja fuerte) ---
try:
    clave_secreta = st.secrets["GOOGLE_API_KEY"]
except:
    clave_secreta = "CAMBIAME"

genai.configure(api_key=clave_secreta)

# --- 6. BARRA LATERAL (Resto de opciones) ---
with st.sidebar:
    st.title("🧸 Menú Pinter")
    modo = st.radio("Elige opción:", ["👩‍🏫 Asistente de Aula", "📖 Cuentacuentos (Voz)"])
    st.markdown("---")
    st.link_button("🚀 Crear Imágenes (Bing)", "https://www.bing.com/images/create")

# --- 7. LÓGICA DEL CHAT ---
if "chat_general" not in st.session_state: st.session_state.chat_general = []
if "chat_cuentos" not in st.session_state: st.session_state.chat_cuentos = []

if modo == "👩‍🏫 Asistente de Aula":
    st.title("👩‍🏫 Asistente General")
    for m in st.session_state.chat_general:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    
    pregunta = st.chat_input("Escribe aquí tu consulta...")
    if pregunta:
        st.session_state.chat_general.append({"role": "user", "content": pregunta})
        with st.chat_message("user"): st.markdown(pregunta)
        with st.chat_message("assistant"):
            caja = st.empty()
            try:
                modelo = genai.GenerativeModel('gemini-1.5-flash-8b')
                res = modelo.generate_content(pregunta)
                caja.markdown(res.text)
                st.session_state.chat_general.append({"role": "assistant", "content": res.text})
            except Exception as e: caja.error(f"Error: {e}")

elif modo == "📖 Cuentacuentos (Voz)":
    st.title("📖 La Hora del Cuento")
    for m in st.session_state.chat_cuentos:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    tema_cuento = st.chat_input("¿De qué quieres el cuento?")
    if tema_cuento:
        st.session_state.chat_cuentos.append({"role": "user", "content": tema_cuento})
        with st.chat_message("user"): st.markdown(tema_cuento)
        with st.chat_message("assistant"):
            caja = st.empty()
            try:
                modelo = genai.GenerativeModel('gemini-1.5-flash-8b')
                res = modelo.generate_content(f"Eres un cuentacuentos infantil. Escribe un cuento corto sobre {tema_cuento}. Sin negritas ni símbolos.")
                texto_limpio = res.text.replace("*", "").replace("#", "")
                caja.markdown(res.text)
                st.session_state.chat_cuentos.append({"role": "assistant", "content": res.text})
                
                # Generar audio
                tts = gTTS(text=texto_limpio, lang='es')
                audio_bytes = io.BytesIO()
                tts.write_to_fp(audio_bytes)
                st.audio(audio_bytes, format='audio/mp3')
            except Exception as e: caja.error(f"Error: {e}")
