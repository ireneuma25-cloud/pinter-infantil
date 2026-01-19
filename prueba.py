import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io
import random
import json

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Pinter Edu", page_icon="🧸", layout="wide")

# --- 2. GESTIÓN DEL TEMA (CLARO / OSCURO) ---
# Esto va al principio para aplicar los colores antes de pintar nada
with st.sidebar:
    st.title("🧸 Menú Pinter")
    
    # Selector de Tema
    tema = st.radio("Apariencia:", ["🌞 Claro", "🌙 Oscuro"], horizontal=True)
    st.markdown("---")

# Definimos los colores según el tema elegido
if tema == "🌞 Claro":
    # Colores TEMA CLARO (Original)
    color_fondo = "#FDFBF7"
    color_texto = "#4A4A4A"
    color_sidebar = "#F9F5EB"
    color_caja = "#FFFFFF"
    color_borde = "#F0F0F0"
    imagen_fondo = 'url("https://www.transparenttextures.com/patterns/cream-paper.png")'
else:
    # Colores TEMA OSCURO (Elegante)
    color_fondo = "#1A1C24"       # Gris oscuro azulado (mejor que negro puro)
    color_texto = "#E0E0E0"       # Blanco suave
    color_sidebar = "#262730"     # Gris un poco más claro para el menú
    color_caja = "#31333F"        # Fondo de las tarjetas y chats
    color_borde = "#414452"       # Bordes sutiles
    imagen_fondo = 'none'         # Sin textura de papel en modo oscuro

# Aplicamos el CSS Dinámico
estilo_css = f"""
<style>
    html, body, [class*="css"] {{ font-family: 'Times New Roman', Times, serif; color: {color_texto}; }}
    .stApp {{ 
        background-color: {color_fondo}; 
        background-image: {imagen_fondo}; 
    }}
    h1, h2, h3 {{ color: {color_texto} !important; border-bottom: 2px solid #F4D03F; padding-bottom:
