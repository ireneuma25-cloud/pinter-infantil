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

# --- CONEXIÓN SEGURA ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    # CAMBIO MÁGICO: Usamos el nombre con apellido "-001" que es el más estable
    model = genai.GenerativeModel('gemini-1.5-flash-001')
except Exception as e:
    st.error(f"Error de conexión: {e}")

# --- MENÚ ---
with st.sidebar:
    st.title("🧸 Menú Pinter")
    modo = st.radio("Opción:", ["👩‍🏫 Asistente de Aula", "📖 Cuentacuentos (Voz)"])
    st.markdown("---")
    st.info("💡 Consejo: Si se atasca, recarga la página.")

# --- LÓGICA DEL CHAT ---
if modo == "👩‍🏫 Asistente de Aula":
    st.title("👩‍🏫 Asistente General")
    if "chat_general" not in st.session_state: st.session_state.chat_general = []
    
    for m in st.session_state.chat_general:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if pregunta := st.chat_input("Escribe aquí..."):
        st.session_state.chat_general.append({"role": "user", "content": pregunta})
        with st.chat_message("user"): st.markdown(pregunta)
        
        with st.chat_message("assistant"):
            caja = st.empty()
            try:
                # Enviamos la pregunta al modelo "001"
                res = model.generate_content(pregunta)
                caja.markdown(res.text)
                st.session_state.chat_general.append({"role": "assistant", "content": res.text})
            except Exception as e:
                caja.error(f"Error: {e}")

elif modo == "📖 Cuentacuentos (Voz)":
    st.title("📖 La Hora del Cuento")
    if "chat_cuentos" not in st.session_state: st.session_state.chat_cuentos = []

    for m in st.session_state.chat_cuentos:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if tema := st.chat_input("¿De qué quieres el cuento?"):
        st.session_state.chat_cuentos.append({"role": "user", "content": tema})
        with st.chat_message("user"): st.markdown(tema)
        
        with st.chat_message("assistant"):
            caja = st.empty()
            caja.write("Escribiendo...")
            try:
                # Pedimos el cuento
                prompt = f"Escribe un cuento corto para niños sobre: {tema}. Usa lenguaje sencillo."
                res = model.generate_content(prompt)
                texto_limpio = res.text.replace("*", "").replace("#", "")
                
                caja.markdown(res.text)
                st.session_state.chat_cuentos.append({"role": "assistant", "content": res.text})
                
                # Audio
                tts = gTTS(text=texto_limpio, lang='es')
                audio_bytes = io.BytesIO()
                tts.write_to_fp(audio_bytes)
                st.audio(audio_bytes, format='audio/mp3')
            except Exception as e:
                caja.error(f"Error: {e}")
