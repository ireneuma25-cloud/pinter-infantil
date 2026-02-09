import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io
import os
import base64
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Pinter Edu", page_icon="logo2.png", layout="wide")

# ⚠️ CAMBIA ESTO SI TU EXCEL SE LLAMA DIFERENTE
HOJA_NOMBRE = "Base de Datos Pinter" 

# --- 2. CONEXIÓN CON GOOGLE SHEETS (LA MEMORIA) ---
def guardar_en_drive(herramienta, texto_entrada, texto_salida):
    try:
        # Usamos los secretos que configuraste
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        # Abrimos la hoja
        sheet = client.open(HOJA_NOMBRE).sheet1
        
        # Si la hoja está vacía, ponemos encabezados
        if not sheet.get_all_values():
            sheet.append_row(["FECHA", "HERRAMIENTA", "ENTRADA (Lo que escribiste)", "SALIDA (Lo que creó la IA)"])
            
        # Guardamos la fila nueva
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
        sheet.append_row([fecha, herramienta, texto_entrada, texto_salida])
        return True
    except Exception as e:
        return f"Error: {e}"

# --- 3. FUNCIÓN MÁGICA: IMAGEN ---
def imagen_segura(ruta_imagen, ancho_css, clase_extra=""):
    if os.path.exists(ruta_imagen):
        with open(ruta_imagen, "rb") as img_file:
            b64_string = base64.b64encode(img_file.read()).decode()
        html = f"""
            <img src="data:image/png;base64,{b64_string}" class="{clase_extra}"
            style="width:{ancho_css}; pointer-events: none; user-select: none; -webkit-user-drag: none; display: block; margin: auto;">
        """
        st.markdown(html, unsafe_allow_html=True)

# --- 4. CSS PROFESIONAL ---
st.markdown("""
<style>
    html, body, [class*="css"] { font-family: 'Times New Roman', serif; }
    img { pointer-events: none !important; }
    [data-testid="StyledFullScreenButton"] { display: none !important; }
    
    @media only screen and (max-width: 768px) {
        .logo-esquina { display: none !important; }
        h1 { text-align: center; }
    }
    .stTextArea textarea { font-size: 16px !important; line-height: 1.5 !important; }
</style>
""", unsafe_allow_html=True)

# --- 5. BARRA LATERAL ---
with st.sidebar:
    imagen_segura("logo1.png", "85%") 
    st.write("") 
    tema = st.radio("Apariencia:", ["Claro", "Oscuro"], horizontal=True)
    st.markdown("<hr style='margin-top: -5px; margin-bottom: 20px; border: 0; border-top: 1px solid #aaaaaa;'>", unsafe_allow_html=True)

if tema == "Claro":
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

# --- 6. CONEXIÓN IA ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-flash-latest')
except Exception as e:
    st.error(f"Error de conexión IA: {e}")

# --- 7. MENÚ ---
with st.sidebar:
    modo = st.radio("Herramientas Docentes:", [
        "Traductor Pedagógico (LOMLOE)", 
        "Cuentos Terapéuticos",
        "Diseñador ABN & Retos",
        "Chat Asistente General"
    ])
    st.markdown("<hr style='margin-top: -5px; margin-bottom: 20px; border: 0; border-top: 1px solid #aaaaaa;'>", unsafe_allow_html=True)
    if st.button("Descargar Sesión"):
        st.info("Función en mantenimiento")

# --- 8. HEADER ---
def crear_encabezado(titulo):
    c_txt, c_img = st.columns([0.85, 0.15])
    with c_txt:
        st.markdown(f"<h1 style='border-bottom: 2px solid #F4D03F; padding-bottom: 10px;'>{titulo}</h1>", unsafe_allow_html=True)
    with c_img:
        imagen_segura("logo.png", "100%", "logo-esquina")

# --- 9. LÓGICA DE HERRAMIENTAS ---

# === TRADUCTOR ===
if modo == "Traductor Pedagógico (LOMLOE)":
    crear_encabezado("Traductor a Lenguaje Técnico")
    st.info("Transforma observaciones cotidianas en informes profesionales.")
    
    c1, c2 = st.columns(2)
    with c1:
        observacion = st.text_area("Observación:", placeholder="Ej: Hoy Juanito...", height=150)
        contexto = st.text_input("Contexto:", placeholder="Ej: 4 años...")
        
        if st.button("Generar Informe"):
            if observacion:
                prompt = f"Actúa como experta. Traduce: '{observacion}' (Contexto: {contexto}) a lenguaje técnico pedagógico."
                with st.spinner("Redactando..."):
                    try:
                        res = model.generate_content(prompt)
                        st.session_state.traductor_res = res.text.replace("*", "").replace("#", "")
                        st.session_state.traductor_in = f"{observacion} | {contexto}"
                    except Exception as e: st.error(f"Error: {e}")
    
    with c2:
        st.subheader("Resultado:")
        if "traductor_res" in st.session_state:
            st.text_area("", value=st.session_state.traductor_res, height=250)
            
            # BOTÓN DE GUARDADO
            if st.button("💾 Guardar en Drive", key="btn_save_trad"):
                res = guardar_en_drive("Traductor", st.session_state.traductor_in, st.session_state.traductor_res)
                if res == True: st.success("¡Guardado en tu Excel!")
                else: st.error(f"No se pudo guardar: {res}")

# === CUENTOS ===
elif modo == "Cuentos Terapéuticos":
    crear_encabezado("Cuentos de Neuroeducación")
    st.info("Historias para gestionar emociones.")
    
    col_input, col_out = st.columns([1, 1])
    with col_input:
        problema = st.text_input("Problema:", placeholder="Ej: Celos, miedos...")
        interes = st.text_input("Interés:", placeholder="Ej: Dinosaurios...")
        edad = st.select_slider("Edad:", options=["3 años", "4 años", "5 años"], value="4 años")
        
        if st.button("Escribir Cuento"):
            if problema and interes:
                prompt = f"Escribe cuento infantil ({edad}). Objetivo: {problema}. Interés: {interes}. SIN NOTAS, SOLO HISTORIA."
                with st.spinner("Creando..."):
                    try:
                        res = model.generate_content(prompt)
                        texto_limpio = res.text.replace("*", "").replace("#", "").replace("_", "")
                        st.session_state.cuento_res = texto_limpio
                        st.session_state.cuento_in = f"{problema} | {interes} | {edad}"
                        
                        tts = gTTS(text=texto_limpio, lang='es')
                        bio = io.BytesIO()
                        tts.write_to_fp(bio)
                        st.session_state.cuento_audio = bio
                    except Exception as e: st.error(f"Error: {e}")
    
    with col_out:
        if "cuento_res" in st.session_state:
            st.subheader("Escuchar:")
            if "cuento_audio" in st.session_state:
                st.audio(st.session_state.cuento_audio, format='audio/mp3')
            st.subheader("Leer:")
            st.write(st.session_state.cuento_res)
            
            # BOTÓN DE GUARDADO
            if st.button("💾 Guardar en Drive", key="btn_save_cuento"):
                res = guardar_en_drive("Cuentos", st.session_state.cuento_in, st.session_state.cuento_res)
                if res == True: st.success("¡Guardado en tu Excel!")
                else: st.error(f"No se pudo guardar: {res}")

# === ABN ===
elif modo == "Diseñador ABN & Retos":
    crear_encabezado("Diseñador ABN")
    st.info("Actividades de matemáticas manipulativas.")
    
    c1, c2 = st.columns(2)
    with c1:
        objetivo = st.text_input("Objetivo:", placeholder="Ej: Conteo...")
        materiales = st.text_input("Materiales:", placeholder="Ej: Piñas...")
        
        if st.button("Diseñar Actividad"):
            if objetivo:
                prompt = f"Diseña actividad ABN. Objetivo: {objetivo}. Materiales: {materiales}."
                with st.spinner("Pensando..."):
                    try:
                        res = model.generate_content(prompt)
                        st.session_state.abn_res = res.text.replace("*", "").replace("#", "")
                        st.session_state.abn_in = f"{objetivo} | {materiales}"
                    except Exception as e: st.error(f"Error: {e}")

    with c2:
        if "abn_res" in st.session_state:
            st.markdown(st.session_state.abn_res)
            
            # BOTÓN DE GUARDADO
            if st.button("💾 Guardar en Drive", key="btn_save_abn"):
                res = guardar_en_drive("ABN", st.session_state.abn_in, st.session_state.abn_res)
                if res == True: st.success("¡Guardado en tu Excel!")
                else: st.error(f"No se pudo guardar: {res}")

# === CHAT ===
elif modo == "Chat Asistente General":
    crear_encabezado("Asistente Pedagógico")
    if "chat_general" not in st.session_state: st.session_state.chat_general = []
    
    for m in st.session_state.chat_general:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if pregunta := st.chat_input("Dudas..."):
        st.session_state.chat_general.append({"role": "user", "content": pregunta})
        with st.chat_message("user"): st.markdown(pregunta)
        with st.chat_message("assistant"):
            caja = st.empty()
            try:
                res = model.generate_content(f"Actúa como maestra experta. {pregunta}")
                caja.markdown(res.text)
                st.session_state.chat_general.append({"role": "assistant", "content": res.text})
                
                # Intentamos guardar el chat también (opcional)
                guardar_en_drive("Chat General", pregunta, res.text)
                
            except Exception as e: caja.error(f"Error: {e}")
