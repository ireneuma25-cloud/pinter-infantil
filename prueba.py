import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io
import random
import json # <--- Necesario para guardar los datos

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
    
    /* Estilo Medallero */
    .stMetric { background-color: #FFF; padding: 10px; border-radius: 10px; border: 1px solid #DDD; text-align: center; }
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
    st.title("🧸 Menú Pinter")
    modo = st.radio("Elige opción:", ["⭐ Medallero Semanal", "📝 Asamblea y Lista", "👩‍🏫 Asistente de Aula", "📖 Cuentacuentos"])
    st.markdown("---")
    
    if st.button("💾 Descargar Chat"):
        texto = ""
        if "chat_general" in st.session_state:
            for m in st.session_state.chat_general:
                texto += f"{m['role']}: {m['content']}\n"
        
        if texto:
            st.download_button("📥 Bajar archivo", texto, "pinter.txt")

# --- 5. LÓGICA PRINCIPAL ---

# ==========================================
# MODO: MEDALLERO (NUEVO)
# ==========================================
if modo == "⭐ Medallero Semanal":
    st.title("⭐ Medallero de la Clase")
    st.info("Usa este panel para premiar el buen comportamiento.")

    # 1. Configuración de alumnos para el medallero
    if "puntos_alumnos" not in st.session_state:
        # Iniciamos con 0 puntos
        nombres = ["Lucas", "Sofía", "Mateo", "Valentina", "Hugo", "Martín"]
        st.session_state.puntos_alumnos = {nombre: 0 for nombre in nombres}

    # 2. Sistema de Guardado / Cargado (EL TRUCO)
    with st.expander("💾 GUARDAR / CARGAR PUNTOS (Haz esto el viernes)", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Para GUARDAR:**")
            # Convertimos los puntos a texto
            codigo_guardado = json.dumps(st.session_state.puntos_alumnos)
            st.code(codigo_guardado, language="json")
            st.caption("Copia este código y guárdalo en tus notas.")
        
        with c2:
            st.markdown("**Para CARGAR:**")
            codigo_carga = st.text_input("Pega aquí el código guardado:")
            if st.button("🔄 Recuperar Puntos"):
                try:
                    st.session_state.puntos_alumnos = json.loads(codigo_carga)
                    st.success("¡Puntos recuperados!")
                    st.rerun()
                except:
                    st.error("El código no es válido.")

    st.markdown("---")

    # 3. Panel de Estrellas
    cols = st.columns(3)
    idx = 0
    
    for nombre, estrellas in st.session_state.puntos_alumnos.items():
        with cols[idx % 3]:
            st.subheader(f"👤 {nombre}")
            
            # Mostramos las estrellas visualmente
            st.markdown(f"### {'⭐' * estrellas}")
            if estrellas == 0:
                st.caption("Sin estrellas aún")
            
            # Botones
            b1, b2 = st.columns(2)
            if b1.button(f"➕", key=f"mas_{nombre}"):
                st.session_state.puntos_alumnos[nombre] += 1
                st.rerun()
            
            if b2.button(f"➖", key=f"menos_{nombre}"):
                if st.session_state.puntos_alumnos[nombre] > 0:
                    st.session_state.puntos_alumnos[nombre] -= 1
                    st.rerun()
            
            st.markdown("---")
        idx += 1

# ==========================================
# MODO: ASAMBLEA
# ==========================================
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

# ==========================================
# MODO: ASISTENTE
# ==========================================
elif modo == "👩‍🏫 Asistente de Aula":
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

# ==========================================
# MODO: CUENTACUENTOS
# ==========================================
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
