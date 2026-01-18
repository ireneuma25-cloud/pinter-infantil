import streamlit as st
import google.generativeai as genai

st.title("🕵️‍♀️ Detector de Modelos")

try:
    # Configuramos la clave
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    st.write("Conectando con Google... ⏳")
    
    # Pedimos la lista de modelos disponibles
    lista_modelos = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            lista_modelos.append(m.name)
            
    st.success("¡Conexión exitosa! ✅")
    st.write("Estos son los modelos exactos que tu clave permite usar:")
    st.code(lista_modelos)
    
except Exception as e:
    st.error("❌ Error de conexión:")
    st.write(e)
