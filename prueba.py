import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Pinter Edu", page_icon="🧸", layout="wide")

# --- MODO CLARO/OSCURO ---
with st.sidebar:
    st.title("🎨 Apariencia")
    tema = st.radio("Elige el modo:", ["Modo Claro ☀️", "Modo Oscuro 🌙"])

if tema == "Modo Claro ☀️":
    f, t, s, b, bu = "#FDFBF7", "#4A4A4A", "#F9F5EB", "#F4D03F", "#FFFFFF"
else:
    f, t, s, b, bu = "#121212", "#E0E0E0", "#1E1E1E", "#BB86FC", "#2D2D2D"

st.markdown(f"""
<style>
    .stApp {{ background-color: {f} !important; color: {t} !important; }}
    section[data-testid="stSidebar"] {{ background-color: {s} !important; }}
    h1, h2, h3, p, span, label {{ color: {t} !important; font-family: 'Times New Roman', serif; }}
    .stChatMessage {{ background-color: {bu} !important; border: 1px solid {b} !important; border-radius: 12px; }}
</style>
""", unsafe_allow_html=True)

# --- CONFIGURAR IA ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    # USAMOS EL NOMBRE MÁS SEGURO DE GOOGLE
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except Exception as e:
    st.error(f"Error de llave: {e}")

# --- MENÚ LATERAL ---
with st.sidebar:
    st.title("🧸 Menú Pinter")
    modo = st.radio("Opción:", ["👩‍🏫 Asistente", "📖 Cuentos"])
    st.markdown("---")
    st.link_button("🚀 Crear Imágenes", "https://www.bing.com/images/create")

# --- LÓGICA ---
if "chat" not in st.session_state: st.session_state.chat = []

st.title("👩‍🏫 Pinter Edu" if modo == "👩‍🏫 Asistente" else "📖 Cuentacuentos")

for m in st.session_state.chat:
    with st.chat_message(m["role"]): st.markdown(m["content"])

pregunta = st.chat_input("Escribe aquí...")
if pregunta:
    st.session_state.chat.append({"role": "user", "content": pregunta})
    with st.chat_message("user"): st.markdown(pregunta)
    with st.chat_message("assistant"):
        try:
            res = model.generate_content(pregunta)
            st.markdown(res.text)
            st.session_state.chat.append({"role": "assistant", "content": res.text})
            if modo == "📖 Cuentos":
                tts = gTTS(text=res.text.replace("*", ""), lang='es')
                audio_bytes = io.BytesIO()
                tts.write_to_fp(audio_bytes)
                st.audio(audio_bytes, format='audio/mp3')
        except Exception as e:
            st.error(f"Error 404 corregido, pero algo falló: {e}")
