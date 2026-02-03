import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io
import os
import base64 

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Pinter Edu", page_icon="logo2.png", layout="wide")

# --- 2. FUNCIÓN MÁGICA: IMAGEN INTOCABLE ---
def imagen_segura(ruta_imagen, ancho_css, clase_extra=""):
    if os.path.exists(ruta_imagen):
        with open(ruta_imagen, "rb") as img_file:
            b64_string = base64.b64encode(img_file.read()).decode()
        html = f"""
            <img src="data:image/png;base64,{b64_string}" class="{clase_extra}"
            style="width:{ancho_css}; pointer-events: none; user-select: none; -webkit-user-drag: none; display: block; margin: auto;">
        """
        st.markdown(html, unsafe_allow_html=True)

# --- 3. CSS PROFESIONAL (RESPONSIVE + ESTILO) ---
st.markdown("""
<style>
    html, body, [class*="css"] { font-family: 'Times New Roman', serif; }
    img { pointer-events: none !important; }
    [data-testid="StyledFullScreenButton"] { display: none !important; }
    
    /* Móvil: Ocultar logo esquina y centrar título */
    @media only screen and (max-width: 768px) {
        .logo-esquina { display: none !important; }
        h1 { text-align: center; }
    }
    
    /* Cajas de resultados más bonitas */
    .stTextArea textarea { font-size: 16px !important; line-height: 1.5 !important; }
</style>
""", unsafe_allow_html=True)

# --- 4. BARRA LATERAL (DISEÑO Y TEMAS) ---
with st.sidebar:
    imagen_segura("logo1.png", "85%") 
    st.write("") 
    tema = st.radio("Apariencia:", ["🌞 Claro", "🌙 Oscuro"], horizontal=True)
    
    # Línea separadora compacta
    st.markdown("<hr style='margin-top: -5px; margin-bottom: 20px; border: 0; border-top: 1px solid #aaaaaa;'>", unsafe_allow_html=True)

# Lógica de Colores (Diseño Aterciopelado)
if tema == "🌞 Claro":
    c_bg_app = "#FDFBF7"
    c_text_main = "#4A4A4A"
    c_sidebar = "#F9F5EB"
    c_sidebar_text = "#4A4A4A" 
    c_caja_chat = "#FFFFFF"
    c_input_bg = "#FFFFFF" 
    c_input_text = "#000000"
    c_btn_bg = "#F0F0F0"
    c_btn_text = "#000000"
    c_border = "#DDDDDD"
    img_fondo = 'url("https://www.transparenttextures.com/patterns/cream-paper.png")'
else:
    c_bg_app = "#3E2F28"      
    c_text_main = "#FFFFFF"   
    c_sidebar = "#4E3B32"     
    c_sidebar_text = "#FFFFFF" 
    c_caja_chat = "#5D473D"   
    c_input_bg = "#FFF8E7"    
    c_input_text = "#3E2F28"  
    c_btn_bg = "#F4D03F"      
    c_btn_text = "#1E1611"    
    c_border = "#F4D03F"
    img_fondo = 'url("https://www.transparenttextures.com/patterns/black-linen.png")'

# Inyectar Colores
st.markdown(f"""
<style>
    .stApp {{ background-color: {c_bg_app}; background-image: {img_fondo}; }}
    html, body, h1, h2, h3, p, label, div, .stMarkdown {{ color: {c_text_main} !important; }}
    section[data-testid="stSidebar"] {{ background-color: {c_sidebar}; border-right: 1px solid {c_border}; }}
    section[data-testid="stSidebar"] * {{ color: {c_sidebar_text} !important; }}
    .stTextInput input, .stTextArea textarea {{ background-color: {c_input_bg} !important; color: {c_input_text} !important; border: 2px solid {c_border} !important; }}
    .stButton > button {{ background-color: {c_btn_bg} !important; color: {c_btn_text} !important; border: 1px solid {c_text_main} !important; font-weight: bold !important; }}
    .stChatMessage {{ background-color: {c_caja_chat}; border: 1px solid {c_border}; }}
    .stInfo, .stSuccess {{ background-color: {c_caja_chat} !important; color: {c_text_main} !important; border: 1px solid {c_border}; }}
</style>
""", unsafe_allow_html=True)

# --- 5. CONEXIÓN IA ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-flash-latest')
except Exception as e:
    st.error(f"Error de conexión: {e}")

# --- 6. MENÚ DE HERRAMIENTAS (EL GIRO MAESTRO) ---
with st.sidebar:
    # AQUÍ ESTÁN LAS NUEVAS HERRAMIENTAS PEDAGÓGICAS
    modo = st.radio("Herramientas Docentes:", [
        "📄 Traductor Pedagógico (LOMLOE)", 
        "🧠 Cuentos Terapéuticos",
        "🔢 Diseñador ABN & Retos",
        "👩‍🏫 Chat Asistente General"
    ])
    
    st.markdown("<hr style='margin-top: -5px; margin-bottom: 20px; border: 0; border-top: 1px solid #aaaaaa;'>", unsafe_allow_html=True)
    
    if st.button("💾 Descargar Sesión"):
        st.info("Función en mantenimiento (Pronto disponible)")

# --- 7. HEADER ---
def crear_encabezado(titulo):
    c_txt, c_img = st.columns([0.85, 0.15])
    with c_txt:
        st.markdown(f"<h1 style='border-bottom: 2px solid #F4D03F; padding-bottom: 10px;'>{titulo}</h1>", unsafe_allow_html=True)
    with c_img:
        imagen_segura("logo.png", "100%", "logo-esquina")

# --- 8. LÓGICA DE LAS HERRAMIENTAS ---

# === HERRAMIENTA 1: TRADUCTOR PEDAGÓGICO ===
if modo == "📄 Traductor Pedagógico (LOMLOE)":
    crear_encabezado("Traductor a Lenguaje Técnico")
    st.info("Transforma observaciones cotidianas en informes profesionales listos para la administración.")
    
    c1, c2 = st.columns(2)
    with c1:
        observacion = st.text_area("¿Qué ha pasado? (Lenguaje normal):", 
                                   placeholder="Ej: Hoy Juanito le ha quitado el juguete a María y cuando le he reñido se ha puesto a llorar y a patalear.",
                                   height=150)
        contexto = st.text_input("Contexto del alumno (Opcional):", placeholder="Ej: 4 años, posible retraso madurativo.")
        
        if st.button("✨ Generar Informe Profesional"):
            if observacion:
                prompt = f"""
                Actúa como una experta en Pedagogía y legislación educativa (LOMLOE).
                Tengo esta observación de aula en lenguaje coloquial: "{observacion}".
                Contexto: {contexto}.
                
                Redacta un párrafo para un informe oficial. 
                - Usa terminología técnica (regulación emocional, habilidades sociales, tolerancia a la frustración).
                - Mantén un tono objetivo y profesional.
                - No inventes datos, solo traduce lo que te he dicho.
                """
                with st.spinner("Consultando manuales pedagógicos..."):
                    try:
                        res = model.generate_content(prompt)
                        st.session_state.resultado_traductor = res.text
                    except Exception as e: st.error(f"Error: {e}")
    
    with c2:
        st.subheader("📝 Texto para el Informe:")
        if "resultado_traductor" in st.session_state:
            st.text_area("Resultado:", value=st.session_state.resultado_traductor, height=250)


# === HERRAMIENTA 2: CUENTOS TERAPÉUTICOS ===
elif modo == "🧠 Cuentos Terapéuticos":
    crear_encabezado("Cuentos de Neuroeducación")
    st.info("Crea historias personalizadas para gestionar emociones y conflictos específicos.")
    
    col_input, col_out = st.columns([1, 1])
    
    with col_input:
        problema = st.text_input("¿Qué queremos trabajar?", placeholder="Ej: Celos del hermano pequeño, miedo a la oscuridad...")
        interes = st.text_input("¿Qué le gusta al niño/a?", placeholder="Ej: Los dinosaurios, el espacio, las princesas...")
        edad = st.select_slider("Edad del grupo:", options=["3 años", "4 años", "5 años"], value="4 años")
        
        if st.button("📖 Escribir Cuento"):
            if problema and interes:
                prompt = f"""
                Escribe un cuento infantil corto para un niño de {edad}.
                Objetivo terapéutico: Trabajar {problema}.
                Tema principal: {interes}.
                
                Usa metáforas sencillas de neuroeducación para que el niño entienda su emoción.
                El tono debe ser calmado, empático y con final positivo.
                """
                with st.spinner("Imaginando historia..."):
                    try:
                        res = model.generate_content(prompt)
                        st.session_state.cuento_texto = res.text
                        
                        # Generar Audio
                        texto_limpio = res.text.replace("*", "")
                        tts = gTTS(text=texto_limpio, lang='es')
                        bio = io.BytesIO()
                        tts.write_to_fp(bio)
                        st.session_state.cuento_audio = bio
                        
                    except Exception as e: st.error(f"Error: {e}")
    
    with col_out:
        if "cuento_texto" in st.session_state:
            st.subheader("🎧 Escuchar:")
            if "cuento_audio" in st.session_state:
                st.audio(st.session_state.cuento_audio, format='audio/mp3')
            
            st.subheader("📜 Leer:")
            st.write(st.session_state.cuento_texto)


# === HERRAMIENTA 3: DISEÑADOR ABN ===
elif modo == "🔢 Diseñador ABN & Retos":
    crear_encabezado("Diseñador de Actividades ABN")
    st.info("Genera actividades de matemáticas manipulativas basadas en el método ABN.")
    
    c1, c2 = st.columns(2)
    with c1:
        objetivo = st.text_input("Objetivo Matemático:", placeholder="Ej: Conteo, amigos del 10, subitización...")
        materiales = st.text_input("Materiales disponibles:", placeholder="Ej: Piñas, piedras, tapones, ceras...")
        
        if st.button("🎲 Diseñar Actividad"):
            if objetivo:
                prompt = f"""
                Eres experta en el método ABN (Algoritmo Basado en Números) para Educación Infantil.
                Diseña una actividad paso a paso.
                Objetivo: {objetivo}.
                Materiales: {materiales}.
                
                Estructura:
                1. Asamblea (Introducción).
                2. Desarrollo (Manipulación).
                3. Cierre (Metacognición).
                """
                with st.spinner("Diseñando reto matemático..."):
                    try:
                        res = model.generate_content(prompt)
                        st.session_state.resultado_abn = res.text
                    except Exception as e: st.error(f"Error: {e}")

    with c2:
        if "resultado_abn" in st.session_state:
            st.markdown(st.session_state.resultado_abn)


# === HERRAMIENTA 4: CHAT GENERAL (EXTRA) ===
elif modo == "👩‍🏫 Chat Asistente General":
    crear_encabezado("Asistente Pedagógico")
    if "chat_general" not in st.session_state: st.session_state.chat_general = []
    
    for m in st.session_state.chat_general:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if pregunta := st.chat_input("Pregunta sobre didáctica, dudas, ideas..."):
        st.session_state.chat_general.append({"role": "user", "content": pregunta})
        with st.chat_message("user"): st.markdown(pregunta)
        with st.chat_message("assistant"):
            caja = st.empty()
            try:
                res = model.generate_content(f"Actúa como maestra experta en infantil. {pregunta}")
                caja.markdown(res.text)
                st.session_state.chat_general.append({"role": "assistant", "content": res.text})
            except Exception as e: caja.error(f"Error: {e}")
