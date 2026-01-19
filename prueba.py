import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io
import random
import json
import os
import base64 

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Pinter Edu", page_icon="🧸", layout="wide")

# --- 2. FUNCIÓN MÁGICA: IMAGEN INTOCABLE ---
def imagen_segura(ruta_imagen, ancho_px):
    if os.path.exists(ruta_imagen):
        with open(ruta_imagen, "rb") as img_file:
            b64_string = base64.b64encode(img_file.read()).decode()
        st.markdown(
            f'<img src="data:image/png;base64,{b64_string}" '
            f'style="width:{ancho_px}px; pointer-events: none; user-select: none; -webkit-user-drag: none; display: block; margin-left: auto;">',
            unsafe_allow_html=True
        )

# --- 3. GESTIÓN DEL TEMA Y LOGO LATERAL ---
with st.sidebar:
    # Logo del Menú (logo1.png)
    imagen_segura("logo1.png", 180)
    st.write("") 
    tema = st.radio("Apariencia:", ["🌞 Claro", "🐻 Chocolate"], horizontal=True)
    st.markdown("---")

# Lógica de Colores
if tema == "🌞 Claro":
    c_bg_app = "#FDFBF7"
    c_text_main = "#4A4A4A"
    c_sidebar = "#F9F5EB"
    c_sidebar_text = "#4A4A4A" 
    c_caja_chat = "#FFFFFF"
    c_input_bg = "#FFFFFF" 
    c_input_text = "#000000"
    c_placeholder = "#666666" 
    c_btn_bg = "#F0F0F0"
    c_btn_text = "#000000"
    c_border = "#DDDDDD"
    img_fondo = 'url("https://www.transparenttextures.com/patterns/cream-paper.png")'
else:
    c_bg_app = "#1E1611"      
    c_text_main = "#FFFFFF"   
    c_sidebar = "#2B2118"     
    c_sidebar_text = "#FFFFFF" 
    c_caja_chat = "#3E2F26"   
    c_input_bg = "#FFF8E7"    
    c_input_text = "#1E1611"  
    c_placeholder = "#555555" 
    c_btn_bg = "#F4D03F"      
    c_btn_text = "#1E1611"    
    c_border = "#F4D03F"
    img_fondo = 'none'

# CSS GENERAL (AQUÍ ESTÁ EL TRUCO PARA SUBIRLO TODO)
st.markdown(f"""
<style>
    /* Reduce el espacio vacío de arriba del todo */
    .block-container {{
        padding-top: 2rem !important; 
    }}

    html, body, [class*="css"] {{ font-family: 'Times New Roman', serif; color: {c_text_main}; }}
    .stApp {{ background-color: {c_bg_app}; background-image: {img_fondo}; }}
    
    /* Menú */
    section[data-testid="stSidebar"] {{ background-color: {c_sidebar}; border-right: 1px solid {c_border}; }}
    section[data-testid="stSidebar"] .stRadio label, section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] div, 
    section[data-testid="stSidebar"] h1 {{ color: {c_sidebar_text} !important; }}
    button[kind="header"], span[data-testid="stArrow"] {{ color: {c_sidebar_text} !important; }}
    
    /* Títulos alineados */
    h1 {{ 
        color: {c_text_main} !important; 
        border-bottom: 2px solid #F4D03F; 
        margin-top: 0px !important;
        padding-top: 10px !important;
    }}
    
    h2, h3, h4, label, p, .stMarkdown {{ color: {c_text_main} !important; }}
    
    /* Inputs y Botones */
    input[type="text"], textarea, .stTextArea textarea, .stTextInput input {{ background-color: {c_input_bg} !important; color: {c_input_text} !important; border: 2px solid {c_border} !important; }}
    ::placeholder {{ color: {c_placeholder} !important; opacity: 1 !important; }}
    .stButton > button {{ background-color: {c_btn_bg} !important; color: {c_btn_text} !important; border: 1px solid {c_text_main} !important; font-weight: bold !important; }}
    .stButton > button:hover {{ filter: brightness(115%); transform: scale(1.02); }}
    
    /* Cajas */
    .stChatMessage {{ background-color: {c_caja_chat}; border: 1px solid {c_border}; border-radius: 12px; }}
    .stMetric, .stCheckbox {{ background-color: {c_caja_chat}; color: {c_text_main}; padding: 10px; border-radius: 10px; border: 1px solid {c_border}; }}
</style>
""", unsafe_allow_html=True)

# --- 4. CONEXIÓN ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-flash-latest')
except Exception as e:
    st.error(f"Error de conexión: {e}")

# --- 5. MENÚ LATERAL (CON EMOJIS) ---
with st.sidebar:
    modo = st.radio("Herramientas:", [
        "👩‍🏫 Asistente de Aula", 
        "✍️ Redactor de Informes",
        "⭐ Medallero Semanal", 
        "📝 Asamblea y Lista", 
        "📖 Cuentacuentos"
    ])
    
    st.markdown("---")
    if st.button("💾 Descargar Chat"):
        texto = ""
        if "chat_general" in st.session_state:
            for m in st.session_state.chat_general:
                texto += f"{m['role']}: {m['content']}\n"
        if texto:
            st.download_button("📥 Bajar archivo", texto, "pinter.txt")

# --- 6. FUNCIÓN PARA EL ENCABEZADO (ALINEAR TÍTULO Y LOGO) ---
def crear_encabezado(titulo_texto):
    # Creamos dos columnas: Izquierda (Título) y Derecha (Logo)
    # Align="bottom" intenta que el texto y la imagen se alineen abajo
    c_titulo, c_logo = st.columns([8, 1.5], gap="medium")
    
    with c_titulo:
        # Título SIN emoji
        st.title(titulo_texto)
        
    with c_logo:
        # Logo seguro (logo.png)
        imagen_segura("logo.png", 100) # Tamaño 100 para que quede elegante

# --- 7. LÓGICA PRINCIPAL ---

# MODO 1: ASISTENTE
if modo == "👩‍🏫 Asistente de Aula":
    crear_encabezado("Asistente General") # Título limpio
    
    if "chat_general" not in st.session_state: st.session_state.chat_general = []
    
    for m in st.session_state.chat_general:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if pregunta := st.chat_input("Consulta..."):
        st.session_state.chat_general.append({"role": "user", "content": pregunta})
        with st.chat_message("user"): st.markdown(pregunta)
        with st.chat_message("assistant"):
            caja = st.empty()
            try:
                res = model.generate_content(pregunta)
                caja.markdown(res.text)
                st.session_state.chat_general.append({"role": "assistant", "content": res.text})
            except Exception as e: caja.error(f"Error: {e}")

# MODO 2: REDACTOR
elif modo == "✍️ Redactor de Informes":
    crear_encabezado("Redactor Mágico de Notas") # Título limpio
    st.info("Convierte tus notas rápidas en textos profesionales.")
    
    col1, col2 = st.columns(2)
    with col1:
        nombre_alumno = st.text_input("Nombre del alumno/a:", placeholder="Ej: Lucas")
        puntos_clave = st.text_area("Puntos clave:", placeholder="Ej: come bien, pega...", height=150)
        tono = st.select_slider("Tono:", options=["Muy Formal", "Cercano", "Muy Cariñoso"], value="Cercano")
        
        st.write("")
        if st.button("✨ Generar Informe"):
            if nombre_alumno and puntos_clave:
                prompt = f"Actúa como maestra. Redacta mensaje para padres de {nombre_alumno}. Tono: {tono}. Puntos: {puntos_clave}."
                try:
                    res = model.generate_content(prompt)
                    st.session_state.resultado_informe = res.text
                except Exception as e: st.error(f"Error: {e}")

    with col2:
        st.subheader("📝 Resultado:")
        if "resultado_informe" in st.session_state:
            st.text_area("Copia el resultado:", value=st.session_state.resultado_informe, height=300)

# MODO 3: MEDALLERO
elif modo == "⭐ Medallero Semanal":
    crear_encabezado("Medallero de la Clase") # Título limpio
    
    if "puntos_alumnos" not in st.session_state:
        nombres = ["Lucas", "Sofía", "Mateo", "Valentina", "Hugo", "Martín"]
        st.session_state.puntos_alumnos = {nombre: 0 for nombre in nombres}

    # Sección de Guardado
    with st.expander("💾 GUARDAR / CARGAR", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            st.code(json.dumps(st.session_state.puntos_alumnos), language="json")
        with c2:
            codigo_carga = st.text_input("Pega código aquí:")
            if st.button("🔄 Recuperar"):
                try:
                    st.session_state.puntos_alumnos = json.loads(codigo_carga)
                    st.rerun()
                except: st.error("Error")

    st.markdown("---")
    cols = st.columns(3)
    idx = 0
    for nombre, estrellas in st.session_state.puntos_alumnos.items():
        with cols[idx % 3]:
            st.subheader(f"👤 {nombre}")
            st.markdown(f"### {'⭐' * estrellas}")
            b1, b2 = st.columns(2)
            if b1.button("➕", key=f"m_{nombre}"):
                st.session_state.puntos_alumnos[nombre] += 1
                st.rerun()
            if b2.button("➖", key=f"r_{nombre}"):
                if st.session_state.puntos_alumnos[nombre] > 0:
                    st.session_state.puntos_alumnos[nombre] -= 1
                    st.rerun()
            st.markdown("---")
        idx += 1

# MODO 4: ASAMBLEA
elif modo == "📝 Asamblea y Lista":
    crear_encabezado("Control de Asamblea") # Título limpio
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("📋 Configurar Clase")
        default = "Lucas, Sofía, Mateo, Valentina, Hugo, Martín"
        texto = st.text_area("Nombres:", value=default, height=150)
        lista = [n.strip() for n in texto.split(",") if n.strip()]

    with col2:
        st.subheader("✅ Asistencia")
        presentes = []
        cols_lista = st.columns(3)
        for i, al in enumerate(lista):
            if cols_lista[i % 3].checkbox(f"👤 {al}", value=True, key=al):
                presentes.append(al)
        st.info(f"Asistencia: {len(presentes)} / {len(lista)}")

    st.markdown("---")
    if st.button("🌟 Elegir ENCARGADO"):
        if presentes:
            elegido = random.choice(presentes)
            st.balloons()
            st.success(f"## ¡El encargado es: {elegido}! 👑")

# MODO 5: CUENTACUENTOS
elif modo == "📖 Cuentacuentos":
    crear_encabezado("La Hora del Cuento") # Título limpio
    
    if "chat_cuentos" not in st.session_state: st.session_state.chat_cuentos = []

    for m in st.session_state.chat_cuentos:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if tema := st.chat_input("Tema del cuento..."):
        st.session_state.chat_cuentos.append({"role": "user", "content": tema})
        with st.chat_message("user"): st.markdown(tema)
        with st.chat_message("assistant"):
            caja = st.empty()
            caja.write("✨ Escribiendo...")
            try:
                res = model.generate_content(f"Cuento infantil corto sobre: {tema}")
                caja.markdown(res.text)
                st.session_state.chat_cuentos.append({"role": "assistant", "content": res.text})
                
                txt = res.text.replace("*", "").replace("#", "")
                tts = gTTS(text=txt, lang='es')
                bio = io.BytesIO()
                tts.write_to_fp(bio)
                st.audio(bio, format='audio/mp3')
            except Exception as e: caja.error(f"Error: {e}")
