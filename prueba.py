import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Pinter Edu", page_icon="🧸", layout="wide")

# --- DISEÑO (Mantenemos tu estilo exacto) ---
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

# --- BLOQUE DE SEGURIDAD ---
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
    
    st.header("💾 Guardar Chat")
    texto_a_guardar = ""
    
    # Lógica para preparar la descarga del chat
    if modo == "👩‍🏫 Asistente de Aula" and "chat_general" in st.session_state:
        for m in st.session_state.chat_general:
            role = "PROFE" if m["role"] == "user" else "IA"
            texto_a_guardar += f"{role}: {m['content']}\n\n"
        st.download_button("📥 Descargar asistente.txt", texto_a_guardar, "asistente.txt")
        
    elif modo == "📖 Cuentacuentos (Voz)" and "chat_cuentos" in st.session_state:
        for m in st.session_state.chat_cuentos:
            role = "PROFE" if m["role"] == "user" else "CUENTO"
            texto_a_guardar += f"{role}: {m['content']}\n\n"
        st.download_button("📥 Descargar cuentos.txt", texto_a_guardar, "cuentos.txt")
    
    st.markdown("---")
    st.link_button("🚀 Crear Imágenes (Bing)", "https://www.bing.com/images/create")

# --- LÓGICA PRINCIPAL ---

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
                # CORRECCIÓN: Usamos el modelo estable para evitar el Error 404
                modelo = genai.GenerativeModel('gemini-1.5-flash')
                respuesta = modelo.generate_content(pregunta)
                caja.markdown(respuesta.text)
                st.session_state.chat_general.append({"role": "assistant", "content": respuesta.text})
                st.rerun()
            except Exception as e:
                caja.error(f"Error: {e}")

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
                # CORRECCIÓN: Modelo 1.5-flash sin el "-8b" para máxima compatibilidad
                prompt_sistema = "Eres un narrador para niños. Escribe texto plano, frases cortas, sin negritas."
                modelo = genai.GenerativeModel('gemini-1.5-flash', system_instruction=prompt_sistema)
                respuesta = modelo.generate_content(tema)
                
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
