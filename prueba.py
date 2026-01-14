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
    .stChatMessage { background-color: #FFFFFF; border: 1px solid #F0F0F0; border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

# --- CONEXIÓN ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    # USAMOS EL 1.5 QUE ES EL QUE FUNCIONA
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Error de conexión: {e}")

# --- MENÚ LATERAL ---
with st.sidebar:
    st.title("🧸 Menú Pinter")
    modo = st.radio("Opción:", ["Asistente de Aula", "Cuentacuentos"])

# --- LÓGICA ---
if "chat" not in st.session_state: st.session_state.chat = []

st.title("👩‍🏫 Asistente" if modo == "Asistente de Aula" else "📖 Cuentacuentos")

for m in st.session_state.chat:
    with st.chat_message(m["role"]): st.markdown(m["content"])

pregunta = st.chat_input("Escribe aquí...")
if pregunta:
    st.session_state.chat.append({"role": "user", "content": pregunta})
    with st.chat_message("user"): st.markdown(pregunta)
    with st.chat_message("assistant"):
        try:
            # Aquí es donde se genera la respuesta
            res = model.generate_content(pregunta)
            st.markdown(res.text)
            st.session_state.chat.append({"role": "assistant", "content": res.text})
            
            if modo == "Cuentacuentos":
                tts = gTTS(text=res.text.replace("*", ""), lang='es')
                audio_bytes = io.BytesIO()
                tts.write_to_fp(audio_bytes)
                st.audio(audio_bytes, format='audio/mp3')
        except Exception as e:
            st.error(f"Error técnico: {e}")
