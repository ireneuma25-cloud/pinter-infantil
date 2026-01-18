import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Pinter Edu", page_icon="🧸", layout="wide")

# --- DISEÑO ---
st.markdown("""
<style>
    html, body, [class*="css"] { font-family: 'Times New Roman', Times, serif; }
    .stApp { background-color: #FDFBF7; background-image: url("https://www.transparenttextures.com/patterns/cream-paper.png"); }
    h1 { color: #4A4A4A; border-bottom: 2px solid #F4D03F; padding-bottom: 10px; }
    .stChatMessage { background-color: #FFFFFF; border: 1px solid #F0F0F0; border-radius: 12px; }
    section[data-testid="stSidebar"] { background-color: #F9F5EB; border-right: 1px solid #E0DND0; }
</style>
""", unsafe_allow_html=True)

# --- CONEXIÓN ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    # ¡AQUÍ ESTÁ LA SOLUCIÓN! Usamos el modelo que SÍ tienes en tu lista
    model = genai.GenerativeModel('gemini-2.0-flash')
except Exception as e:
    st.error(f"Error de conexión: {e}")

# --- MENÚ LATERAL ---
with st.sidebar:
    st.title("🧸 Menú Pinter")
    modo = st.radio("Elige opción:", ["👩‍🏫 Asistente de Aula", "📖 Cuentacuentos (Voz)"])
    st.markdown("---")
    
    # Botón de descarga
    texto_a_guardar = ""
    if modo == "👩‍🏫 Asistente de Aula" and "chat_general" in st.session_state:
        for m in st.session_state.chat_general:
            role = "PROFE" if m["role"] == "user" else "IA"
            texto_a_guardar += f"{role}: {m['content']}\n\n"
        st.download_button("📥 Descargar Chat", texto_a_guardar, "clase.txt")

# --- LÓGICA DEL CHAT ---
if modo == "👩‍🏫 Asistente de Aula":
    st.title("👩‍🏫 Asistente General")
    if "chat_general" not in st.session_state: st.session_state.chat_general = []
    
    for m in st.session_state.chat_general:
        with
