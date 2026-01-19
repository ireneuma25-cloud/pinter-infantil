import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io
import random
import json

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Pinter Edu", page_icon="🧸", layout="wide")

# --- 2. GESTIÓN DEL TEMA (NEBULOSA LENTA) ---
with st.sidebar:
    st.title("🧸 Menú Pinter")
    tema = st.radio("Apariencia:", ["🌞 Claro", "🐻 Chocolate"], horizontal=True)
    st.markdown("---")

# Definir Colores y Animación CSS
if tema == "🌞 Claro":
    # --- TEMA CLARO (Nebulosa de Vainilla) ---
    # Solo 2 colores muy parecidos (Beige y Crema) moviéndose MUY LENTO
    css_fondo = """
        background: linear-gradient(120deg, #FDFBF7, #F5E6D3, #FDFBF7);
        background-size: 400% 400%;
        animation: gradient 60s ease infinite;
    """
    c_texto = "#4A4A4A"
    c_sidebar = "rgba(253, 251, 247, 0.9)" 
    c_caja = "rgba(255, 255, 255, 0.85)" # Casi opaco
    c_borde = "rgba(0,0,0,0.05)"

else:
    # --- TEMA OSCURO (Nebulosa de Café) ---
    # Solo 2 colores oscuros (Café solo y Café con leche muy oscuro)
    css_fondo = """
        background: linear-gradient(120deg, #1E1611, #2E221A, #1E1611);
        background-size: 400% 400%;
        animation: gradient 60s ease infinite;
    """
    c_texto = "#E6DCCF" 
    c_sidebar = "rgba(43, 33, 24, 0.95)"
    c_caja = "rgba(54, 41, 32, 0.9)" # Madera oscura
    c_borde = "rgba(255,255,255,0.05)"

# Inyectamos el CSS (Estilos)
st.markdown(f"""
<style>
    /* Animación LENTA (60 segundos) */
    @keyframes gradient {{
        0% {{background-position: 0% 50%;}}
        50% {{background-position: 100% 50%;}}
        100% {{background-position: 0% 50%;}}
    }}

    html, body, [class*="css"] {{ font-family: 'Times New Roman', serif; color: {c_texto}; }}
    
    /* Fondo animado */
    .stApp {{ {css_fondo} }}
    
    h1, h2, h3 {{ color: {c_texto} !important; border-bottom: 2px solid #F4D03F; }}
    
    /* Cajas y elementos */
    .stChatMessage {{ background-color: {c_caja}; border: 1px solid {c_borde}; border-radius: 12px; }}
    section[data-testid="stSidebar"] {{ background-color: {c_sidebar}; border-right: 1px solid {c_borde}; }}
    .stMetric, .stCheckbox {{ background-color: {c_caja}; color: {c_texto}; padding: 10px; border-radius: 10px; border: 1px solid {c_borde}; }}
    
    /* Inputs */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {{ color: {c_texto}; background-color: {c_caja}; border: 1px solid {c_borde}; }}
    p {{ color: {c_texto}; }}
</style>
""", unsafe_allow_html=True)

# --- 3. CONEXIÓN ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-flash-latest')
except Exception as e:
    st.error(f"Error de conexión: {e}")

# --- 4. MENÚ LATERAL ---
with st.sidebar:
    modo = st.radio("Herramientas:", [
        "👩‍🏫 Asistente de Aula", 
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

# --- 5. LÓGICA PRINCIPAL ---

# MODO 1: ASISTENTE
if modo == "👩‍🏫 Asistente de Aula":
    st.title("👩‍🏫 Asistente General")
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

# MODO 2: MEDALLERO
elif modo == "⭐ Medallero Semanal":
    st.title("⭐ Medallero de la Clase")
    st.info("Sistema de puntos.")

    if "puntos_alumnos" not in st.session_state:
        nombres = ["Lucas", "Sofía", "Mateo", "Valentina", "Hugo", "Martín"]
        st.session_state.puntos_alumnos = {nombre: 0 for nombre in nombres}

    with st.expander("💾 GUARDAR / CARGAR (Haz esto SIEMPRE antes de cerrar)", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**GUARDAR:**")
            st.code(json.dumps(st.session_state.puntos_alumnos), language="json")
            st.caption("⚠️ Copia el código antes de salir.")
        
        with c2:
            st.markdown("**CARGAR:**")
            codigo_carga = st.text_input("Pega código aquí:")
            if st.button("🔄 Recuperar"):
                try:
                    st.session_state.puntos_alumnos = json.loads(codigo_carga)
                    st.success("¡Recuperado!")
                    st.rerun()
                except: st.error("Código inválido.")

    st.markdown("---")
    cols = st.columns(3)
    idx = 0
    for nombre, estrellas in st.session_state.puntos_alumnos.items():
        with cols[idx % 3]:
            st.subheader(f"👤 {nombre}")
            st.markdown(f"### {'⭐' * estrellas}")
            b1, b2 = st.columns(2)
            if b1.button("➕", key=f"mas_{nombre}"):
                st.session_state.puntos_alumnos[nombre] += 1
                st.rerun()
            if b2.button("➖", key=f"menos_{nombre}"):
                if st.session_state.puntos_alumnos[nombre] > 0:
                    st.session_state.puntos_alumnos[nombre] -= 1
                    st.rerun()
            st.markdown("---")
        idx += 1

# MODO 3: ASAMBLEA
elif modo == "📝 Asamblea y Lista":
    st.title("📝 Control de Asamblea")
    
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

# MODO 4: CUENTACUENTOS
elif modo == "📖 Cuentacuentos":
    st.title("📖 La Hora del Cuento")
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
