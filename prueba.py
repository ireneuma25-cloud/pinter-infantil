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
HOJA_NOMBRE = "Base de Datos Pinter" 

# --- 2. CONEXIÓN CON GOOGLE SHEETS ---
def conectar_google_sheets():
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sh = client.open(HOJA_NOMBRE)
        return sh
    except Exception as e:
        return None

def guardar_en_drive(usuario, herramienta, texto_entrada, texto_salida):
    try:
        sh = conectar_google_sheets()
        if sh is None: return "Error de conexión"
        sheet = sh.sheet1
        if not sheet.get_all_values():
            sheet.append_row(["FECHA", "USUARIO", "HERRAMIENTA", "ENTRADA", "SALIDA"])
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
        sheet.append_row([fecha, usuario, herramienta, texto_entrada, texto_salida])
        return True
    except Exception as e:
        if "200" in str(e): return True
        return f"Error: {e}"

def leer_historial_bruto(usuario_filtro=None):
    try:
        sh = conectar_google_sheets()
        if sh is None: return [], "No conectado"
        sheet = sh.sheet1
        
        # USAMOS EL MÉTODO "TANQUE" (Get All Values)
        todas_filas = sheet.get_all_values()
        
        if len(todas_filas) < 2: return [], sh.url # Si tiene menos de 2 filas, es que solo hay cabecera o nada
        
        # Procesamos manualmente para evitar errores de cabeceras
        datos_procesados = []
        
        # Empezamos en la fila 1 (saltando la 0 que son los títulos)
        for fila in todas_filas[1:]:
            # Rellenamos huecos si la fila está incompleta
            while len(fila) < 5: fila.append("")
            
            item = {
                "FECHA": fila[0],
                "USUARIO": fila[1],
                "HERRAMIENTA": fila[2],
                "ENTRADA": fila[3],
                "SALIDA": fila[4]
            }
            
            # Lógica de filtrado
            if usuario_filtro is None:
                datos_procesados.append(item) # Si es modo espía, entra todo
            else:
                # Comparamos nombres quitando mayúsculas y espacios
                if str(item["USUARIO"]).strip().lower() == str(usuario_filtro).strip().lower():
                    datos_procesados.append(item)
                    
        return datos_procesados, sh.url
    except Exception as e:
        st.error(f"Error técnico leyendo: {e}")
        return [], ""

# --- 3. IMAGEN Y CSS ---
def imagen_segura(ruta_imagen, ancho_css, clase_extra=""):
    if os.path.exists(ruta_imagen):
        with open(ruta_imagen, "rb") as img_file:
            b64_string = base64.b64encode(img_file.read()).decode()
        html = f"""<img src="data:image/png;base64,{b64_string}" class="{clase_extra}" style="width:{ancho_css}; pointer-events: none; display: block; margin: auto;">"""
        st.markdown(html, unsafe_allow_html=True)

st.markdown("""
<style>
    html, body, [class*="css"] { font-family: 'Times New Roman', serif; }
    img { pointer-events: none !important; }
    [data-testid="StyledFullScreenButton"] { display: none !important; }
    @media only screen and (max-width: 768px) { .logo-esquina { display: none !important; } h1 { text-align: center; } }
    .stTextArea textarea { font-size: 16px !important; }
</style>""", unsafe_allow_html=True)

# --- 4. BARRA LATERAL ---
with st.sidebar:
    imagen_segura("logo1.png", "85%") 
    st.write("") 
    st.info("👋 ¡Hola! Identifícate.")
    usuario_actual = st.text_input("Tu Nombre (Ej: Irene):")
    if not usuario_actual:
        st.warning("⚠️ Escribe tu nombre para empezar.")
        st.stop()
    st.success(f"Sesión de: {usuario_actual}")
    st.markdown("---")
    tema = st.radio("Apariencia:", ["Claro", "Oscuro"], horizontal=True)
    st.markdown("<hr style='margin-top: -5px; margin-bottom: 20px; border: 0; border-top: 1px solid #aaaaaa;'>", unsafe_allow_html=True)

if tema == "Claro":
    c_bg_app = "#FDFBF7"; c_text_main = "#4A4A4A"; c_sidebar = "#F9F5EB"; c_sidebar_text = "#4A4A4A" 
    c_caja_chat = "#FFFFFF"; c_input_bg = "#FFFFFF"; c_input_text = "#000000"; c_btn_bg = "#F0F0F0"; c_btn_text = "#000000"; c_border = "#DDDDDD"; img_fondo = 'url("https://www.transparenttextures.com/patterns/cream-paper.png")'
else:
    c_bg_app = "#3E2F28"; c_text_main = "#FFFFFF"; c_sidebar = "#4E3B32"; c_sidebar_text = "#FFFFFF" 
    c_caja_chat = "#5D473D"; c_input_bg = "#FFF8E7"; c_input_text = "#3E2F28"; c_btn_bg = "#F4D03F"; c_btn_text = "#1E1611"; c_border = "#F4D03F"; img_fondo = 'url("https://www.transparenttextures.com/patterns/black-linen.png")'

st.markdown(f"""<style>.stApp {{ background-color: {c_bg_app}; background-image: {img_fondo}; }} html, body, h1, h2, h3, p, label, div, .stMarkdown {{ color: {c_text_main} !important; }} section[data-testid="stSidebar"] {{ background-color: {c_sidebar}; border-right: 1px solid {c_border}; }} section[data-testid="stSidebar"] * {{ color: {c_sidebar_text} !important; }} .stTextInput input, .stTextArea textarea {{ background-color: {c_input_bg} !important; color: {c_input_text} !important; border: 2px solid {c_border} !important; }} .stButton > button {{ background-color: {c_btn_bg} !important; color: {c_btn_text} !important; border: 1px solid {c_text_main} !important; font-weight: bold !important; }} .stChatMessage {{ background-color: {c_caja_chat}; border: 1px solid {c_border}; }} .stInfo, .stSuccess {{ background-color: {c_caja_chat} !important; color: {c_text_main} !important; border: 1px solid {c_border}; }}</style>""", unsafe_allow_html=True)

# --- 5. LÓGICA ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-flash-latest')
except Exception as e: st.error(f"Error IA: {e}")

with st.sidebar:
    modo = st.radio("Herramientas Docentes:", ["Traductor Pedagógico (LOMLOE)", "Cuentos Terapéuticos", "Diseñador ABN & Retos", "Chat Asistente General", "📂 Ver MI Historial"])

def crear_encabezado(titulo):
    c_txt, c_img = st.columns([0.85, 0.15])
    with c_txt: st.markdown(f"<h1 style='border-bottom: 2px solid #F4D03F; padding-bottom: 10px;'>{titulo}</h1>", unsafe_allow_html=True)
    with c_img: imagen_segura("logo.png", "100%", "logo-esquina")

# --- HERRAMIENTAS ---
if modo == "Traductor Pedagógico (LOMLOE)":
    crear_encabezado("Traductor Pedagógico")
    c1, c2 = st.columns(2)
    with c1:
        obs = st.text_area("Observación:", height=150)
        ctx = st.text_input("Contexto:")
        if st.button("Generar"):
            res = model.generate_content(f"Traduce: '{obs}' ({ctx}) a lenguaje técnico pedagógico.")
            st.session_state.trad_res, st.session_state.trad_in = res.text, f"{obs} | {ctx}"
    with c2:
        if "trad_res" in st.session_state:
            st.write(st.session_state.trad_res)
            if st.button("💾 Guardar"):
                if guardar_en_drive(usuario_actual, "Traductor", st.session_state.trad_in, st.session_state.trad_res): st.success("¡Guardado!")

elif modo == "Cuentos Terapéuticos":
    crear_encabezado("Cuentos")
    c1, c2 = st.columns(2)
    with c1:
        prob = st.text_input("Problema:"); inte = st.text_input("Interés:"); edad = st.select_slider("Edad", ["3", "4", "5"])
        if st.button("Crear"):
            res = model.generate_content(f"Cuento infantil {edad}. Objetivo: {prob}. Interés: {inte}.")
            st.session_state.cuento_res, st.session_state.cuento_in = res.text, f"{prob} | {inte}"
    with c2:
        if "cuento_res" in st.session_state:
            st.write(st.session_state.cuento_res)
            if st.button("💾 Guardar"):
                if guardar_en_drive(usuario_actual, "Cuentos", st.session_state.cuento_in, st.session_state.cuento_res): st.success("¡Guardado!")

elif modo == "Diseñador ABN & Retos":
    crear_encabezado("ABN")
    c1, c2 = st.columns(2)
    with c1:
        obj = st.text_input("Objetivo:"); mat = st.text_input("Materiales:")
        if st.button("Diseñar"):
            res = model.generate_content(f"Actividad ABN. Objetivo: {obj}. Materiales: {mat}.")
            st.session_state.abn_res, st.session_state.abn_in = res.text, f"{obj} | {mat}"
    with c2:
        if "abn_res" in st.session_state:
            st.write(st.session_state.abn_res)
            if st.button("💾 Guardar"):
                if guardar_en_drive(usuario_actual, "ABN", st.session_state.abn_in, st.session_state.abn_res): st.success("¡Guardado!")

elif modo == "Chat Asistente General":
    crear_encabezado("Asistente")
    if "chat" not in st.session_state: st.session_state.chat = []
    for m in st.session_state.chat: st.chat_message(m["role"]).write(m["content"])
    if p := st.chat_input("Duda..."):
        st.session_state.chat.append({"role":"user","content":p}); st.chat_message("user").write(p)
        r = model.generate_content(f"Eres maestra experta. {p}").text
        st.session_state.chat.append({"role":"assistant","content":r}); st.chat_message("assistant").write(r)
        guardar_en_drive(usuario_actual, "Chat", p, r)

# --- VISOR ---
elif modo == "📂 Ver MI Historial":
    crear_encabezado(f"Biblioteca de {usuario_actual}")
    ver_todo = st.checkbox("🕵️‍♀️ No veo mis cosas (Mostrar TODO el Excel)")
    
    if st.button("🔄 Actualizar"): st.rerun()
    
    filtro = None if ver_todo else usuario_actual
    items, url_excel = leer_historial_bruto(filtro)
    
    # ENLACE DE DIAGNÓSTICO
    if url_excel:
        st.caption(f"🔗 [Haga clic aquí para comprobar que es el mismo Excel que tiene abierto]({url_excel})")

    if items:
        for i in reversed(items):
            quien = f"👤 {i['USUARIO']} | " if ver_todo else ""
            with st.expander(f"{quien}📅 {i['FECHA']} | {i['HERRAMIENTA']} | {str(i['ENTRADA'])[:30]}..."):
                st.write(f"**Entrada:** {i['ENTRADA']}")
                st.markdown("---")
                st.write(i['SALIDA'])
    else:
        st.warning("⚠️ No se ha encontrado nada en la lectura.")
