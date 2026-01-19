import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io
import random
import json
import os 

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Pinter Edu", page_icon="🧸", layout="wide")

# --- 2. CSS PARA OCULTAR BOTONES Y AJUSTES VISUALES ---
st.markdown("""
<style>
    /* Bloquear clics y arrastre en imágenes */
    img {
        pointer-events: none !important;
        -webkit-user-drag: none !important;
        user-select: none !important;
    }
    
    /* Ocultar botones de pantalla completa y menú de imagen */
    [data-testid="StyledFullScreenButton"], [data-testid="stImage"] button {
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
    }
    
    /* Eliminar borde hover en imágenes */
    [data-testid="stImage"]:hover {
        box-shadow: none !important;
    }

    /* Ajuste de Fuente y Colores */
    html, body, [class*="css"] { font-family: 'Times New Roman', serif; }
</style>
""", unsafe_allow_html=True)

# --- 3. GESTIÓN DEL TEMA Y LOGO LATERAL ---
with st.sidebar:
    # === LOGO NUEVO EN EL MENÚ (logo1.png) ===
    if os.path.exists("logo1.png"):
        c1, c2, c3 = st.columns([0.2, 2, 0.2]) 
        with c2:
            st.image("logo1.png", use_column_width=True) 
    else:
        st.warning("⚠️ Sube 'logo1.png'")
        st.markdown("---")
    
    st.write("") 
    # HEMOS CAMBIADO EL NOMBRE A "🌙 Tema Oscuro"
    tema = st.radio("Apariencia:", ["🌞 Claro", "🌙 Tema Oscuro"], horizontal=True)
    st.markdown("---")

# Lógica de Colores
if tema == "🌞 Claro":
    # TEMA CLARO (Igual que antes)
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
    # TEMA OSCURO (NUEVO COLOR MARRÓN MÁS SUAVE)
    # Antes era #1E1611 (Casi negro), ahora es #3E2F28 (Madera oscura)
    c_bg_app = "#3E2F28"      
    c_text_main = "#FFFFFF"   
    c_sidebar = "#4E3B32"     # Barra lateral un poco más clara para contraste
    c_sidebar_text = "#FFFFFF" 
    c_caja_chat = "#5D473D"   # Cajas del chat un poco más claras
    
    c_input_bg = "#FFF8E7"    # Mantenemos papel crema para leer bien
    c_input_text = "#3E2F28"  
    c_placeholder = "#555555" 
    
    c_btn_bg = "#F4D03F"      
    c_btn_text = "#1E1611"    
    c_border = "#F4D03F"
    img_fondo = 'none'

# Inyectamos el CSS de colores
st.markdown(f"""
<style>
    .stApp {{ background-color: {c_bg_app}; background-image: {img_fondo}; }}
    html, body, h1, h2, h3, p, label, div {{ color: {c_text_main} !important; }}
    
    /* Menú Lateral */
    section[data-testid="stSidebar"] {{ background-color: {c_sidebar}; border-right: 1px solid {c_border}; }}
    section[data-testid="stSidebar"] * {{ color: {c_sidebar_text} !important; }}
    
    /* Inputs */
    .stTextInput input, .stTextArea textarea {{ background-color: {c_input_bg} !important; color: {c_input_text} !important; border: 2px solid {c_border} !important; }}
    
    /* Botones */
    .stButton > button {{ background-color: {c_btn_bg} !important; color: {c_btn_text} !important; border: 1px solid {c_text_main} !important; font-weight: bold !important; }}
    
    /* Chat */
    .stChatMessage {{ background-color: {c_caja_chat}; border: 1px solid {c_border}; }}
</style>
""", unsafe_allow_html=True)

# --- 4. CONEXIÓN ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-flash-latest')
except Exception as e:
    st.error(f"Error de conexión: {e}")

# --- 5. MENÚ LATERAL ---
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

# --- 6. FUNCIÓN DE ENCABEZADO ---
def crear_encabezado(titulo_texto):
    c_texto, c_logo = st.columns([0.85, 0.15]) 
    
    with c_texto:
        st.markdown(f"<h1 style='border-bottom: 2px solid #F4D03F; padding-bottom: 10px;'>{titulo_texto}</h1>", unsafe_allow_html=True)
        
    with c_logo:
        if os.path.exists("logo.png"):
            st.image("logo.png", use_column_width=True)

# --- 7. LÓGICA PRINCIPAL ---

# MODO 1: ASISTENTE
if modo == "👩‍🏫 Asistente de Aula":
    crear_encabezado("Asistente General")
    
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
    crear_encabezado("Redactor Mágico de Notas")
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
    crear_encabezado("Medallero de la Clase")
    
    if "puntos_alumnos" not in st.session_state:
        nombres = ["Lucas", "Sofía", "Mateo", "Valentina", "Hugo", "Martín"]
        st.session_state.puntos_alumnos = {nombre: 0 for nombre in nombres}

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
    crear_encabezado("Control de Asamblea")
    
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
    crear_encabezado("La Hora del Cuento")
    
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
