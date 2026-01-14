import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io
import os

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Pinter Edu", page_icon="🧸", layout="wide")

# --- 2. SELECTOR DE MODO (En la barra lateral) ---
with st.sidebar:
    st.title("🎨 Apariencia")
    tema = st.radio("Elige el modo:", ["Modo Claro ☀️", "Modo Oscuro 🌙"])
    st.markdown("---")

# --- 3. LÓGICA DE COLORES DINÁMICOS ---
if tema == "Modo Claro ☀️":
    color_fondo = "#FDFBF7"
    color_texto = "#4A4A4A"
    color_sidebar = "#F9F5EB"
    color_borde = "#F4D03F"
    color_burbuja = "#FFFFFF"
    imagen_fondo = 'url("https://www.transparenttextures.com/patterns/cream-paper.png")'
else:
    color_fondo = "#121212"
    color_texto = "#E0E0E0"
    color_sidebar = "#1E1E1E"
    color_borde = "#BB86FC"
    color_burbuja = "#2D2D2D"
    imagen_fondo = "none"

# --- 4. DISEÑO CSS ACTUALIZADO ---
estilo = f"""
<style>
    html, body, [class*="css"] {{ 
        font-family: 'Times New Roman', Times, serif; 
        color: {color_texto} !important;
    }}
    .stApp {{
        background-color: {color_fondo} !important;
        background-image: {imagen_fondo};
    }}
    h1 {{ color: {color_texto}; border-bottom: 2px solid {color_borde}; padding-bottom: 10px; }}
    .stChatMessage {{ 
        background-color: {color_burbuja} !important; 
        border: 1px solid {color_borde} !important; 
        border-radius: 12px; 
    }}
    section[data-testid="stSidebar"] {{ 
        background-color: {color_sidebar} !important; 
    }}
    /* Asegurar que el texto de los inputs se vea bien */
    .stTextInput input {{ color: {color_texto} !important; }}
</style>
"""
st.markdown(estilo, unsafe_allow_html=True)

# --- 5. CLAVE DE GOOGLE ---
try:
    clave_secreta = st.secrets["GOOGLE_API_KEY"]
except:
    clave_secreta = "CAMBIAME"

genai.configure(api_key=clave_secreta)

# --- 6. BARRA LATERAL (Menú y Guardado) ---
with st.sidebar:
    st.title("🧸 Menú Pinter")
    modo = st.radio("Elige opción:", ["👩‍🏫 Asistente de Aula", "📖 Cuentacuentos (Voz)"])
    st.markdown("---")
    
    # Lógica de Guardar Chat
    texto_a_guardar = ""
    nombre_fichero = "chat.txt"
    if modo == "👩‍🏫 Asistente de Aula" and "chat_general" in st.session_state:
        for m in st.session_state.chat_general:
            role = "PROFE" if m["role"] == "user" else "IA"
            texto_a_guardar += f"{role}: {m['content']}\n\n"
        nombre_fichero = "asistente.txt"
    elif modo == "📖 Cuentacuentos (Voz)" and "chat_cuentos" in st.session_state:
        for m in st.session_state.chat_cuentos:
            role = "PROFE" if m["role"] == "user" else "CUENTO"
            texto_a_guardar += f"{role}: {m['content']}\n\n"
        nombre_fichero = "cuentos.txt"

    if texto_a_guardar:
        st.download_button("📥 Descargar .txt", texto_a_guardar, nombre_fichero)
    
    st.markdown("---")
    st.link_button("🚀 Crear Imágenes (Bing)", "https://www.bing.com/images/create")

# --- 7. LÓGICA PRINCIPAL ---

# 1. MODO ASISTENTE
if modo == "👩‍🏫 Asistente de Aula":
    st.title("👩‍🏫 Asistente General")
    if "chat_general" not in st.session_state: st.session_state.chat_general = []

    for m in st.session_state.chat_general:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    pregunta = st.chat_input("Escribe aquí tu consulta...")
    if pregunta:
        st.session_state.chat_general.append({"role": "user", "content": pregunta})
        with st.chat_message("user"): st.markdown(pregunta)
        with st.chat_message("assistant"):
            caja = st.empty()
            caja.write("Pensando...")
            try:
                # He puesto 1.5-flash porque el 2.5 a veces falla
                modelo = genai.GenerativeModel('gemini-1.5-flash')
                historial = [{"role": ("user" if m["role"]=="user" else "model"), "parts": [m["content"]]} for m in st.session_state.chat_general]
                respuesta = modelo.generate_content(historial)
                caja.markdown(respuesta.text)
                st.session_state.chat_general.append({"role": "assistant", "content": respuesta.text})
                st.rerun()
            except Exception as e: caja.error(f"Error: {e}")

# 2. MODO CUENTACUENTOS
elif modo == "📖 Cuentacuentos (Voz)":
    st.title("📖 La Hora del Cuento")
    if "chat_cuentos" not in st.session_state: st.session_state.chat_cuentos = []

    for m in st.session_state.chat_cuentos:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    tema = st.chat_input("¿De qué quieres el cuento?")
    if tema:
        st.session_state.chat_cuentos.append({"role": "user", "content": tema})
        with st.chat_message("user"): st.markdown(tema)
        with st.chat_message("assistant"):
            caja = st.empty()
            caja.write("Escribiendo cuento...")
            try:
                prompt_sistema = "Eres un narrador para niños. Escribe texto plano, frases cortas, sin negritas."
                modelo = genai.GenerativeModel('gemini-1.5-flash', system_instruction=prompt_sistema)
                historial = [{"role": ("user" if m["role"]=="user" else "model"), "parts": [m["content"]]} for m in st.session_state.chat_cuentos]
                respuesta = modelo.generate_content(historial)
                texto_limpio = respuesta.text.replace("*", "").replace("#", "")
                caja.markdown(respuesta.text)
                st.session_state.chat_cuentos.append({"role": "assistant", "content": respuesta.text})
                
                # Audio
                tts = gTTS(text=texto_limpio, lang='es')
                audio_bytes = io.BytesIO()
                tts.write_to_fp(audio_bytes)
                st.audio(audio_bytes, format='audio/mp3')
                st.rerun()
            except Exception as e: caja.error(f"Error: {e}")
