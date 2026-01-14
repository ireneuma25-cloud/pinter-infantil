import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Pinter Edu", page_icon="🧸", layout="wide")

# --- 2. SELECTOR DE MODO (En la barra lateral) ---
with st.sidebar:
    st.title("🎨 Personalización")
    tema = st.radio("Elige el modo de lectura:", ["Modo Claro ☀️", "Modo Oscuro 🌙"])
    st.markdown("---")

# --- 3. LÓGICA DE COLORES ---
if tema == "Modo Claro ☀️":
    color_fondo, color_texto, color_sidebar, color_borde, color_burbuja = "#FDFBF7", "#4A4A4A", "#F9F5EB", "#F4D03F", "#FFFFFF"
else:
    color_fondo, color_texto, color_sidebar, color_borde, color_burbuja = "#121212", "#E0E0E0", "#1E1E1E", "#BB86FC", "#2D2D2D"

# --- 4. APLICAR ESTILO CSS ---
st.markdown(f"""
<style>
    .stApp {{ background-color: {color_fondo} !important; color: {color_texto} !important; }}
    section[data-testid="stSidebar"] {{ background-color: {color_sidebar} !important; }}
    h1, h2, h3, p, span, label, .stMarkdown {{ color: {color_texto} !important; font-family: 'Times New Roman', serif; }}
    .stChatMessage {{ background-color: {color_burbuja} !important; border: 1px solid {color_borde} !important; border-radius: 15px; }}
    h1 {{ border-bottom: 2px solid {color_borde}; padding-bottom: 10px; }}
</style>
""", unsafe_allow_html=True)

# --- 5. CONFIGURAR IA ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    # USAMOS EL MODELO ESTÁNDAR QUE NO DA ERROR 404
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Error de configuración: {e}")

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
            try:
                res = model.generate_content(pregunta)
                st.markdown(res.text)
                st.session_state.chat_general.append({"role": "assistant", "content": res.text})
            except Exception as e: st.error(f"Error: {e}")

elif modo == "📖 Cuentacuentos (Voz)":
    st.title("📖 La Hora del Cuento")
    for m in st.session_state.chat_cuentos:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    tema_cuento = st.chat_input("¿De qué quieres el cuento?")
    if tema_cuento:
        st.session_state.chat_cuentos.append({"role": "user", "content": tema_cuento})
        with st.chat_message("user"): st.markdown(tema_cuento)
        with st.chat_message("assistant"):
            try:
                res = model.generate_content(f"Eres un cuentacuentos infantil. Cuento corto sobre {tema_cuento}. Sin negritas.")
                st.markdown(res.text)
                st.session_state.chat_cuentos.append({"role": "assistant", "content": res.text})
                tts = gTTS(text=res.text.replace("*", ""), lang='es')
                audio_bytes = io.BytesIO()
                tts.write_to_fp(audio_bytes)
                st.audio(audio_bytes, format='audio/mp3')
            except Exception as e: st.error(f"Error: {e}")
