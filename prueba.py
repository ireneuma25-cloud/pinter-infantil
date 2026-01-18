import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io
import random  # <--- NUEVO: Para hacer sorteos

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
    /* Estilo para los nombres de la lista */
    .stCheckbox { background-color: #FFF; padding: 10px; border-radius: 8px; border: 1px solid #EEE; margin-bottom: 5px; }
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
    # AÑADIMOS LA NUEVA OPCIÓN AQUÍ:
    modo = st.radio("Elige opción:", ["📝 Asamblea y Lista", "👩‍🏫 Asistente de Aula", "📖 Cuentacuentos"])
    st.markdown("---")
    
    if st.button("💾 Descargar Chat"):
        texto = ""
        if "chat_general" in st.session_state:
            for m in st.session_state.chat_general:
                texto += f"{m['role']}: {m['content']}\n"
        elif "chat_cuentos" in st.session_state:
            for m in st.session_state.chat_cuentos:
                texto += f"{m['role']}: {m['content']}\n"
        
        if texto:
            st.download_button("📥 Bajar archivo", texto, "pinter.txt")

# --- 5. LÓGICA PRINCIPAL ---

# ==========================================
# NUEVO MODO: ASAMBLEA Y LISTA
# ==========================================
if modo == "📝 Asamblea y Lista":
    st.title("📝 Control de Asamblea")
    
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("📋 Configurar Clase")
        # Lista por defecto (puedes cambiarla en la web)
        default_alumnos = "Lucas, Sofía, Mateo, Valentina, Hugo, Martín, Lucía, Leo"
        texto_alumnos = st.text_area("Escribe los nombres (separados por comas):", value=default_alumnos, height=150)
        
        # Convertimos el texto en una lista real
        lista_bruta = texto_alumnos.split(",")
        lista_limpia = [nombre.strip() for nombre in lista_bruta if nombre.strip() != ""]

    with col2:
        st.subheader("✅ ¿Quién ha venido hoy?")
        
        # Aquí guardamos quién está presente
        presentes = []
        
        # Creamos columnas para que los nombres no salgan en una fila eterna
        cols_lista = st.columns(3)
        
        for i, alumno in enumerate(lista_limpia):
            # Usamos matemáticas para repartir los nombres en 3 columnas
            col_actual = cols_lista[i % 3]
            if col_actual.checkbox(f"👤 {alumno}", value=True, key=alumno):
                presentes.append(alumno)
        
        st.info(f"Asistencia: **{len(presentes)}** de {len(lista_limpia)} alumnos.")

    st.markdown("---")
    st.subheader("🎡 La Ruleta Mágica")
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        if st.button("🌟 Elegir ENCARGADO"):
            if presentes:
                elegido = random.choice(presentes)
                st.balloons() # ¡Efecto de globos!
                st.success(f"## ¡El encargado es: {elegido}! 👑")
            else:
                st.warning("¡No hay nadie en clase!")

    with c2:
        if st.button("🗣️ Pregunta sorpresa"):
            if presentes:
                elegido = random.choice(presentes)
                st.info(f"## ¿Qué opina: {elegido}? 🎤")

    with c3:
        if st.button("🧹 Equipo de limpieza"):
            if len(presentes) >= 2:
                equipo = random.sample(presentes, 2)
                st.warning(f"## Ayudan hoy: {equipo[0]} y {equipo[1]} 🧽")
            else:
                st.error("Faltan alumnos para hacer equipo.")

# ==========================================
# MODO ASISTENTE (Igual que antes)
# ==========================================
elif modo == "👩‍🏫 Asistente de Aula":
    st.title("👩‍🏫 Asistente General")
    
    if "chat_general" not in st.session_state: st.session_state.chat_general = []
    
    for m in st.session_state.chat_general:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if pregunta := st.chat_input("Escribe aquí tu consulta..."):
        st.session_state.chat_general.append({"role": "user", "content": pregunta})
        with st.chat_message("user"): st.markdown(pregunta)
        
        with st.chat_message("assistant"):
            caja = st.empty()
            try:
                res = model.generate_content(pregunta)
                caja.markdown(res.text)
                st.session_state.chat_general.append({"role": "assistant", "content": res.text})
            except Exception as e:
                caja.error(f"Error: {e}")

# ==========================================
# MODO CUENTACUENTOS (Igual que antes)
# ==========================================
elif modo == "📖 Cuentacuentos":
    st.title("📖 La Hora del Cuento")
    
    if "chat_cuentos" not in st.session_state: st.session_state.chat_cuentos = []

    for m in st.session_state.chat_cuentos:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if tema := st.chat_input("¿De qué quieres el cuento?"):
        st.session_state.chat_cuentos.append({"role": "user", "content": tema})
        with st.chat_message("user"): st.markdown(tema)
        
        with st.chat_message("assistant"):
            caja = st.empty()
            caja.write("✨ Escribiendo historia...")
            try:
                prompt = f"Cuento infantil corto sobre: {tema}."
                res = model.generate_content(prompt)
                
                caja.markdown(res.text)
                st.session_state.chat_cuentos.append({"role": "assistant", "content": res.text})
                
                # Audio
                texto_limpio = res.text.replace("*", "").replace("#", "")
                tts = gTTS(text=texto_limpio, lang='es')
                audio_bytes = io.BytesIO()
                tts.write_to_fp(audio_bytes)
                st.audio(audio_bytes, format='audio/mp3')
            except Exception as e:
                caja.error(f"Error: {e}")
