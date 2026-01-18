import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Pinter Edu", page_icon="🧸", layout="wide")

# --- 2. DISEÑO ---
st.markdown("""
<style>
    html, body, [class*="css"] { font-family: 'Times New Roman', Times, serif; }
    .stApp { background-color: #FDFBF7; background-image: url("https://www.transparenttextures.com/patterns/cream-paper.png"); }
    h1 { color: #4A4A4A; border-bottom: 2px solid #F4D03F; padding-bottom: 10px; }
    .stChatMessage { background-color: #FFFFFF; border: 1px solid #F0F0F0; border-radius: 12px; }
    section[data-testid="stSidebar"] { background-color: #F9F5EB; border-right: 1px solid #E0DND0; }
</style>
""", unsafe_allow_html=True)

# --- 3. CONEXIÓN (EL COMODÍN) ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    # Usamos este nombre que salía en tu lista y nunca falla
    model = genai.GenerativeModel('gemini-flash-latest')
except Exception as e:
    st.error(f"Error de conexión: {e}")

# --- 4. MENÚ LATERAL ---
with st.sidebar:
    st.title("🧸 Menú Pinter")
    modo = st.radio("Elige opción:", ["Asistente de Aula", "Cuentacuentos"])
    st.markdown("---")
    
    if st.button("💾 Descargar Chat"):
        texto = ""
        if "chat_general" in st.session_state:
            for m in st.session_state.chat_general:
                texto += f"{m['role']}: {m['content']}\n"
        elif "chat_cuentos" in st.session_state:
            for m in st.session_state.chat_cuentos:
                texto += f"{m['role']}: {m['content']}\n"
        
        if texto:
            st.download_button("📥 Bajar archivo", texto, "pinter.txt")

# --- 5. LÓGICA PRINCIPAL ---

# MODO ASISTENTE
if modo == "Asistente de Aula":
    st.title("👩‍🏫 Asistente General")
    
    if "chat_general" not in st.session_state: st.session_state.chat_general = []
    
    for m in st.session_state.chat_general:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if pregunta := st.chat_input("Escribe aquí tu consulta..."):
        st.session_state.chat_general.append({"role": "user", "content": pregunta})
        with st.chat_message("user"): st.markdown(pregunta)
        
        with st.chat_message("assistant"):
            caja = st.empty()
            try:
                res = model.generate_content(pregunta)
                caja.markdown(res.
