import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Pinter Edu", page_icon="🧸", layout="wide")

# --- DISEÑO (Estilo papel crema) ---
estilo = """
<style>
    html, body, [class*="css"] { font-family: 'Times New Roman', Times, serif; }
    .stApp {
        background-color: #FDFBF7;
        background-image: url("https://www.transparenttextures.com/patterns/cream-paper.png");
    }
    h1 { color: #4A4A4A; border-bottom: 2px solid #F4D03F; padding-bottom: 10px; }
    .stChatMessage { background-color: #FFFFFF; border: 1px solid #F0F0F0; border-radius: 12px; }
    section[data-testid="stSidebar"] { background-color: #F9F5EB; border-right: 1px solid #E0DND0; }
</style>
"""
st.markdown(estilo, unsafe_allow_html=True)

# --- CLAVE DE GOOGLE ---
try:
    clave_secreta = st.secrets["GOOGLE_API_KEY"]
except:
    clave_secreta = "CAMBIAME"

genai.configure(api_key=clave_secreta)

# --- BARRA LATERAL ---
with st.sidebar:
    st.title("🧸 Menú Pinter")
    modo = st.radio("Elige opción:", ["👩‍🏫 Asistente de Aula", "📖 Cuentacuentos (Voz)"])
    st.markdown("---")
    
    # Botón de Guardar
    st.header("💾 Guardar Chat")
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

# --- LÓGICA PRINCIPAL ---

# 1. MODO ASISTENTE
if modo == "👩‍🏫 Asistente de Aula":
    st.title("👩‍🏫 Asistente General")
    
    if "chat_general" not in st.session_state:
        st.session_state.chat_general = []

    for m in st.session_state.chat_general:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    pregunta = st.chat_input("Escribe aquí tu consulta...")
    
    if pregunta:
        st.session_state.chat_general.append({"role": "user", "content": pregunta})
        with st.chat_message("user"):
            st.markdown(pregunta)

        with st.chat_message("assistant"):
            caja = st.empty()
            caja.write("Pensando...")
            try:
                # CAMBIO CLAVE: Usamos gemini-1.5-flash (1500 usos/día)
                modelo = genai.GenerativeModel('gemini-1.5-flash')
                historial = [{"role": ("user" if m["role"]=="user" else "model"), "parts": [m["content"]]} for m in st.session_state.chat_general]
                respuesta = modelo.generate_content(historial)
                caja.markdown(respuesta.text)
                st.session_state.chat_general.append({"role": "assistant", "content": respuesta.text})
                st.rerun()
            except Exception as e:
                caja.error(f"Error: {e}")

# 2. MODO CUENTACUENTOS
elif modo == "📖 Cuentacuentos (Voz)":
    st.title("📖 La Hora del Cuento")
    
    if "chat_cuentos" not in st.session_state:
        st.session_state.chat_cuentos = []

    for m in st.session_state.chat_cuentos:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    tema = st.chat_input("¿De qué quieres el cuento?")
    
    if tema:
        st.session_state.chat_cuentos.append({"role": "user", "content": tema})
        with st.chat_message("user"):
            st.markdown(tema)

        with st.chat_message("assistant"):
            caja = st.empty()
            caja.write("Escribiendo cuento...")
            try:
                prompt_sistema = "Eres un narrador para niños. Escribe texto plano, frases cortas, sin negritas."
                # CAMBIO CLAVE: Modelo compatible y sin límite de 20 mensajes
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
            except Exception as e:
                caja.error(f"Error: {e}")
