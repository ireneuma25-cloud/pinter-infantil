import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Pinter Edu", page_icon="🧸", layout="wide")

# --- 2. SELECTOR DE MODO ---
with st.sidebar:
    st.title("🎨 Apariencia")
    tema = st.radio("Elige el modo:", ["Modo Claro ☀️", "Modo Oscuro 🌙"])
    st.markdown("---")

# --- 3. LÓGICA DE COLORES ---
if tema == "Modo Claro ☀️":
    color_fondo, color_texto, color_sidebar, color_borde, color_burbuja = "#FDFBF7", "#4A4A4A", "#F9F5EB", "#F4D03F", "#FFFFFF"
    imagen_fondo = 'url("https://www.transparenttextures.com/patterns/cream-paper.png")'
else:
    color_fondo, color_texto, color_sidebar, color_borde, color_burbuja = "#121212", "#E0E0E0", "#1E1E1E", "#BB86FC", "#2D2D2D"
    imagen_fondo = "none"

st.markdown(f"""
<style>
    html, body, [class*="css"] {{ font-family: 'Times New Roman', Times, serif; color: {color_texto} !important; }}
    .stApp {{ background-color: {color_fondo} !important; background-image: {imagen_fondo}; }}
    h1 {{ color: {color_texto}; border-bottom: 2px solid {color_borde}; padding-bottom: 10px; }}
    .stChatMessage {{ background-color: {color_burbuja} !important; border: 1px solid {color_borde} !important; border-radius: 12px; }}
    section[data-testid="stSidebar"] {{ background-color: {color_sidebar} !important; }}
</style>
""", unsafe_allow_html=True)

# --- 4. CONFIGURAR IA (Nombre de modelo seguro) ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    # Probamos con el nombre corto, que es el más compatible
    modelo_ia = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Error de configuración: {e}")

# --- 5. BARRA LATERAL (Tu menú original) ---
with st.sidebar:
    st.title("🧸 Menú Pinter")
    modo = st.radio("Elige opción:", ["👩‍🏫 Asistente de Aula", "📖 Cuentacuentos (Voz)"])
    st.markdown("---")
    
    # Lógica de guardar (Tu código)
    texto_a_guardar = ""
    if modo == "👩‍🏫 Asistente de Aula" and "chat_general" in st.session_state:
        for m in st.session_state.chat_general:
            role = "PROFE" if m["role"] == "user" else "IA"
            texto_a_guardar += f"{role}: {m['content']}\n\n"
    elif modo == "📖 Cuentacuentos (Voz)" and "chat_cuentos" in st.session_state:
        for m in st.session_state.chat_cuentos:
            role = "PROFE" if m["role"] == "user" else "CUENTO"
            texto_a_guardar += f"{role}: {m['content']}\n\n"

    if texto_a_guardar:
        st.download_button("📥 Descargar .txt", texto_a_guardar, "chat_pinter.txt")
    
    st.markdown("---")
    st.link_button("🚀 Crear Imágenes (Bing)", "https://www.bing.com/images/create")

# --- 6. LÓGICA PRINCIPAL ---
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
                # Quitamos el historial complejo para evitar errores de versión
                respuesta = modelo_ia.generate_content(pregunta)
                caja.markdown(respuesta.text)
                st.session_state.chat_general.append({"role": "assistant", "content": respuesta.text})
            except Exception as e: caja.error(f"Error: {e}")

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
            caja.write("Escribiendo...")
            try:
                res = modelo_ia.generate_content(f"Cuento corto sobre {tema}. Sin negritas.")
                texto_limpio = res.text.replace("*", "").replace("#", "")
                caja.markdown(res.text)
                st.session_state.chat_cuentos.append({"role": "assistant", "content": res.text})
                
                tts = gTTS(text=texto_limpio, lang='es')
                audio_bytes = io.BytesIO()
                tts.write_to_fp(audio_bytes)
                st.audio(audio_bytes, format='audio/mp3')
            except Exception as e: caja.error(f"Error: {e}")
