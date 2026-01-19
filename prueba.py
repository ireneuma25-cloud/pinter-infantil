import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io
import random
import json
import os 

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Pinter Edu", page_icon="🧸", layout="wide")

# --- 2. CSS "MODO FANTASMA" (SOLUCIÓN DEFINITIVA) ---
st.markdown("""
<style>
    /* 1. ESTO ES LA CLAVE: 
       Hacemos que el contenedor entero de la imagen sea invisible al ratón.
       Si el ratón no lo "toca", el botón de ampliar nunca sale. */
    [data-testid="stImage"] {
        pointer-events: none !important;
    }

    /* 2. Por si acaso, ocultamos cualquier botón dentro de ese contenedor */
    [data-testid="stImage"] button {
        display: none !important;
        opacity: 0 !important;
    }
    
    /* 3. Quitamos bordes y sombras al pasar el ratón */
    [data-testid="stImage"]:hover {
        box-shadow: none !important;
    }
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
    tema = st.radio("Apariencia:", ["🌞 Claro", "🐻 Chocolate"], horizontal=True)
    st.markdown("---")

# Lógica de Colores (DISEÑO ALTO CONTRASTE)
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

# Inyectamos el CSS de diseño
st.markdown(f"""
<style>
    html, body, [class*="css"] {{ font-family: 'Times New Roman', serif; color: {c_text_main}; }}
    .stApp {{ background-color: {c_bg_app}; background-image: {img_fondo}; }}
    section[data-testid="stSidebar"] {{ background-color: {c_sidebar}; border-right: 1px solid {c_border}; }}
    section[data-testid="stSidebar"] .stRadio label, section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] div, section[data-testid="stSidebar"] h1 {{ color: {c_sidebar_text} !important; }}
    button[kind="header"], span[data-testid="stArrow"] {{ color: {c_sidebar_text} !important; }}
    h1, h2, h3, h4 {{ color: {c_text_main} !important; border-bottom: 2px solid #F4D03F; }}
    label, p, .stMarkdown {{ color: {c_text_main} !important; }}
    input[type="text"], textarea, .stTextArea textarea, .stTextInput input {{ background-color: {c_input_bg} !important; color: {c_input_text} !important; border: 2px solid {c_border} !important; }}
    ::placeholder {{ color: {c_placeholder} !important; opacity: 1 !important; }}
    .stButton > button {{ background-color: {c_btn_bg} !important; color: {c_btn_text} !important; border: 1px solid {c_text_main} !important; font-weight: bold !important; }}
    .stButton > button:hover {{ filter: brightness(115%); transform: scale(1.02); }}
    .stChatMessage {{ background-color: {c_caja_chat}; border: 1px solid {c_border}; border-radius: 12px; }}
    .stMetric, .stCheckbox {{ background-color: {c_caja_chat}; color: {c_text_main}; padding: 10px; border-radius: 10px; border: 1px solid {c_border}; }}
