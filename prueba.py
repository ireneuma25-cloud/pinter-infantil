           import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io
import os
import base64
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import streamlit.components.v1 as components
import urllib.parse
import urllib.request
import time
from dotenv import load_dotenv
import hashlib
import re

load_dotenv()

def limpiar_texto_para_audio(texto):
    if not texto:
        return ""
    # Quitar cualquier etiqueta HTML
    t = re.sub(r"<[^>]+>", " ", texto)
    # Quitar comillas de cualquier tipo para que la voz no pronuncie 'comillas'
    for q in ['"', "'", "“", "”", "«", "»", "‘", "’", "`"]:
        t = t.replace(q, "")
    # Quitar símbolos de formato y markdown para que no diga 'asterisco' o 'almohadilla'
    for ch in ["*", "_", "#", "~", ">", "<", "[", "]", "{", "}", "\\", "/", "|", "^"]:
        t = t.replace(ch, " ")
    # Convertir guiones, rayas de diálogo o paréntesis en pausas naturales
    for d in ["—", "–", "-", "(", ")"]:
        t = t.replace(d, ", ")
    # Limpiar comas consecutivas y normalizar espacios
    t = re.sub(r",\s*,+", ",", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def generar_audio_base64(texto):
    texto_limpio = limpiar_texto_para_audio(texto)
    tts = gTTS(text=texto_limpio, lang='es')
    bio = io.BytesIO()
    tts.write_to_fp(bio)
    b64 = base64.b64encode(bio.getvalue()).decode()
    return f"data:audio/mp3;base64,{b64}"

def generar_svg_fallback(titulo_escena):
    titulo_limpio = (titulo_escena[:40] + '...') if len(titulo_escena) > 40 else titulo_escena
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 420" width="100%" height="100%">
      <defs>
        <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#FEF9E7"/>
          <stop offset="100%" stop-color="#FCF3CF"/>
        </linearGradient>
      </defs>
      <rect width="600" height="420" rx="16" fill="url(#bg)" stroke="#F4D03F" stroke-width="4"/>
      <circle cx="300" cy="170" r="65" fill="#FFFFFF" stroke="#F9E79F" stroke-width="3"/>
      <text x="300" y="195" font-family="'Times New Roman', Times, serif" font-size="52" text-anchor="middle" fill="#D4AC0D">&#9733;</text>
      <text x="300" y="280" font-family="'Times New Roman', Times, serif" font-size="20" font-weight="bold" text-anchor="middle" fill="#5D4037">{titulo_limpio}</text>
      <text x="300" y="315" font-family="'Times New Roman', Times, serif" font-size="14" text-anchor="middle" fill="#8D6E63">Lámina de Cuento Infantil</text>
    </svg>"""
    b64 = base64.b64encode(svg.encode('utf-8')).decode('utf-8')
    return f"data:image/svg+xml;base64,{b64}"

def generar_lamina_moraleja():
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 420" width="100%" height="100%">
      <defs>
        <linearGradient id="gradBg" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#FFFDF9"/>
          <stop offset="50%" stop-color="#FEF9E7"/>
          <stop offset="100%" stop-color="#FCF3CF"/>
        </linearGradient>
        <linearGradient id="gradGold" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#D4AC0D"/>
          <stop offset="50%" stop-color="#F4D03F"/>
          <stop offset="100%" stop-color="#B7950B"/>
        </linearGradient>
      </defs>
      
      <!-- Fondo y marco de cuento -->
      <rect width="600" height="420" rx="20" fill="url(#gradBg)" stroke="#F4D03F" stroke-width="4"/>
      <rect x="14" y="14" width="572" height="392" rx="14" fill="none" stroke="#F9E79F" stroke-width="2" stroke-dasharray="6 4"/>
      
      <!-- Estrellitas decorativas flotantes -->
      <g fill="#F39C12" opacity="0.85">
        <path d="M80 60 L83 68 L91 69 L85 75 L87 83 L80 79 L73 83 L75 75 L69 69 L77 68 Z"/>
        <path d="M520 70 L522 76 L528 77 L524 81 L525 87 L520 84 L515 87 L516 81 L512 77 L518 76 Z"/>
        <path d="M120 340 L122 346 L128 347 L124 351 L125 357 L120 354 L115 357 L116 351 L112 347 L118 346 Z"/>
        <path d="M480 330 L483 338 L491 339 L485 345 L487 353 L480 349 L473 353 L475 345 L469 339 L477 338 Z"/>
      </g>
      
      <!-- Resplandor central -->
      <circle cx="300" cy="180" r="70" fill="#FFFDF9" stroke="#F4D03F" stroke-width="3"/>
      
      <!-- Libro abierto magico -->
      <path d="M255 205 C272 197 288 199 300 206 C312 199 328 197 345 205 L345 155 C328 147 312 149 300 156 C288 149 272 147 255 155 Z" fill="#FFFFFF" stroke="#795548" stroke-width="2.5"/>
      <path d="M300 156 L300 206" stroke="#795548" stroke-width="2"/>
      <path d="M263 167 C273 163 283 165 292 169" stroke="#D7CCC8" stroke-width="1.5" fill="none"/>
      <path d="M263 177 C273 173 283 175 292 179" stroke="#D7CCC8" stroke-width="1.5" fill="none"/>
      <path d="M308 169 C317 165 327 163 337 167" stroke="#D7CCC8" stroke-width="1.5" fill="none"/>
      <path d="M308 179 C317 175 327 173 337 177" stroke="#D7CCC8" stroke-width="1.5" fill="none"/>
      
      <!-- Estrella dorada brillante sobre el libro -->
      <path d="M300 115 L305 130 L320 132 L308 143 L312 157 L300 149 L288 157 L292 143 L280 132 L295 130 Z" fill="url(#gradGold)" stroke="#B7950B" stroke-width="1.5"/>
      <circle cx="300" cy="137" r="4" fill="#FFFFFF"/>
      
      <!-- Cartela / Pancarta de Moraleja -->
      <rect x="160" y="260" width="280" height="46" rx="23" fill="url(#gradGold)" stroke="#B7950B" stroke-width="1.5"/>
      <text x="300" y="290" font-family="'Times New Roman', Times, serif" font-size="22" font-weight="bold" font-style="italic" text-anchor="middle" fill="#3E2723">Moraleja y Aprendizaje</text>
      
      <text x="300" y="340" font-family="'Times New Roman', Times, serif" font-size="16" text-anchor="middle" fill="#6D4C41" font-style="italic">Un mensaje para reflexionar y crecer juntos</text>
    </svg>"""
    b64 = base64.b64encode(svg.encode('utf-8')).decode('utf-8')
    return f"data:image/svg+xml;base64,{b64}"

def obtener_ilustracion_data_uri(prompt, titulo_fallback="Cuento Infantil", imagen_respaldo=None, api_key=None):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8'
    }
    key_a_usar = api_key or os.getenv("POLLINATIONS_API_KEY", "")
    prompt_cod = urllib.parse.quote(prompt)
    if key_a_usar:
        url = f"https://gen.pollinations.ai/image/{prompt_cod}?key={key_a_usar}"
    else:
        url = f"https://image.pollinations.ai/prompt/{prompt_cod}"
    
    for intento in range(3):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=22) as resp:
                if resp.status == 200:
                    data = resp.read()
                    if len(data) > 1000:
                        # Recortar marca de agua inferior (último 6%) limpiamente con PIL
                        try:
                            from PIL import Image
                            img = Image.open(io.BytesIO(data))
                            w, h = img.size
                            img_recortada = img.crop((0, 0, w, int(h * 0.94)))
                            buf = io.BytesIO()
                            img_recortada.save(buf, format="JPEG", quality=90)
                            b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
                            return f"data:image/jpeg;base64,{b64}"
                        except Exception:
                            b64 = base64.b64encode(data).decode('utf-8')
                            return f"data:image/jpeg;base64,{b64}"
        except urllib.error.HTTPError as e:
            if e.code in (402, 429, 503) and intento < 2:
                time.sleep(16)
            elif intento < 2:
                time.sleep(3)
        except Exception:
            if intento < 2:
                time.sleep(3)
            
    if imagen_respaldo:
        return imagen_respaldo
    return ""

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Pinter Edu", page_icon="images/logo2.png", layout="wide")

st.markdown("""
<style>
    /* Tipografía Times New Roman para textos, encabezados y formularios */
    html, body, .stApp, .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6, label, input, textarea, select, th, td {
        font-family: 'Times New Roman', Times, Baskerville, Georgia, serif !important;
    }

    /* Botones de acción regulares */
    .stButton > button, div[data-testid="stFormSubmitButton"] > button {
        font-family: 'Times New Roman', Times, Baskerville, Georgia, serif !important;
    }

    /* Proteger y restaurar la fuente de iconos del sistema (Material Symbols) */
    [data-testid="stIconMaterial"],
    [data-testid*="stSidebarCollapseButton"],
    [data-testid*="stSidebarCollapseButton"] *,
    [data-testid*="stSidebarCollapsedControl"],
    [data-testid*="stSidebarCollapsedControl"] *,
    [data-testid*="stHeader"] button *,
    [data-testid*="stToolbar"] *,
    .material-symbols-rounded,
    .material-symbols-outlined,
    [class*="material-symbols"] {
        font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', sans-serif !important;
        font-style: normal !important;
        font-weight: normal !important;
        text-transform: none !important;
        letter-spacing: normal !important;
        line-height: 1 !important;
    }

    /* Aplicar la raya amarilla a todos los títulos nativos h1 */
    h1 {
        border-bottom: 2px solid #F4D03F !important;
        padding-bottom: 10px !important;
        margin-top: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# TU ID (No lo toques, ya vimos que es el correcto)
HOJA_ID = "12Y57qDxRfNPpHLPUBbcGpb-T4FeHTTjlG9_RPBKeYT8"

# --- 2. CONEXIÓN ---
def conectar_google_sheets():
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds_json = os.getenv("GCP_SERVICE_ACCOUNT_JSON")
        if creds_json:
            creds_dict = json.loads(creds_json)
        else:
            return None
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sh = client.open_by_key(HOJA_ID)
        return sh
    except Exception as e:
        return None

def guardar_en_drive(usuario, herramienta, texto_entrada, texto_salida):
    try:
        sh = conectar_google_sheets()
        if sh is None: return "Error conexión"
        sheet = sh.sheet1
        if not sheet.get_all_values():
            sheet.append_row(["FECHA", "USUARIO", "HERRAMIENTA", "ENTRADA", "SALIDA"])
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
        sheet.append_row([fecha, usuario, herramienta, texto_entrada, texto_salida])
        return True
    except Exception as e:
        if "200" in str(e): return True
        return f"Error: {e}"

# --- FUNCIONES DEL DIARIO VIVO DEL AULA ---
def conectar_hoja_diario():
    try:
        sh = conectar_google_sheets()
        if sh is None: return None
        try:
            sheet_diario = sh.worksheet("Diario_Aula")
        except gspread.WorksheetNotFound:
            sheet_diario = sh.add_worksheet(title="Diario_Aula", rows="1000", cols="10")
            sheet_diario.append_row(["Fecha", "Docente", "Alumno", "Categoria", "Estado_Emocion", "Detalle", "Observacion_Original"])
        return sheet_diario
    except Exception:
        return None

def guardar_en_diario_aula(docente, registros, texto_original):
    try:
        sheet_diario = conectar_hoja_diario()
        if sheet_diario is None: return False
        valores = sheet_diario.get_all_values()
        if not valores:
            sheet_diario.append_row(["Fecha", "Docente", "Alumno", "Categoria", "Estado_Emocion", "Detalle", "Observacion_Original"])
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
        filas = []
        for reg in registros:
            filas.append([
                fecha,
                docente,
                reg.get("alumno", "Sin nombre").strip().capitalize(),
                reg.get("categoria", "General"),
                reg.get("estado", "Normal"),
                reg.get("detalle", ""),
                texto_original
            ])
        if filas:
            sheet_diario.append_rows(filas)
        return True
    except Exception as e:
        if "200" in str(e): return True
        return False

def leer_diario_aula(docente):
    try:
        sheet_diario = conectar_hoja_diario()
        if sheet_diario is None: return []
        datos = sheet_diario.get_all_values()
        if not datos or len(datos) <= 1: return []
        registros_docente = []
        for i, fila in enumerate(datos):
            if i == 0: continue
            if len(fila) >= 6:
                docente_en_fila = fila[1].strip()
                if docente.lower() in docente_en_fila.lower():
                    registros_docente.append({
                        "fecha": fila[0],
                        "docente": fila[1],
                        "alumno": fila[2].strip().capitalize(),
                        "categoria": fila[3],
                        "estado": fila[4],
                        "detalle": fila[5],
                        "observacion": fila[6] if len(fila) > 6 else ""
                    })
        return registros_docente
    except Exception:
        return []

# --- FUNCIONES DE ALUMNOS (CENSO Y MEMORIA DEL AULA) ---
CABECERAS_ALUMNOS = ["Docente", "Alumno", "Informe_Inicial", "Memoria_Evolutiva", "Ultima_Actualizacion", "Fecha_Alta"]

def conectar_hoja_alumnos():
    try:
        sh = conectar_google_sheets()
        if sh is None: return None
        try:
            sheet_alumnos = sh.worksheet("Alumnos_Aula")
        except gspread.WorksheetNotFound:
            sheet_alumnos = sh.add_worksheet(title="Alumnos_Aula", rows="1000", cols="8")
            sheet_alumnos.append_row(CABECERAS_ALUMNOS)
        return sheet_alumnos
    except Exception:
        return None

def guardar_alumnos_aula(docente, lista_alumnos):
    try:
        sheet = conectar_hoja_alumnos()
        if sheet is None: return False
        valores = sheet.get_all_values()
        if not valores:
            sheet.append_row(CABECERAS_ALUMNOS)
            valores = [CABECERAS_ALUMNOS]
        elif "Memoria_Evolutiva" not in valores[0]:
            # Migrar cabecera existente
            nuevas_filas = [CABECERAS_ALUMNOS]
            for f in valores[1:]:
                doc = f[0] if len(f) > 0 else ""
                alu = f[1] if len(f) > 1 else ""
                inf = f[2] if len(f) > 2 else ""
                fec = f[3] if len(f) > 3 else ""
                nuevas_filas.append([doc, alu, inf, "", "", fec])
            sheet.clear()
            sheet.update(nuevas_filas)
            valores = nuevas_filas
            
        fecha_alta = datetime.now().strftime("%d/%m/%Y")
        filas = []
        for item in lista_alumnos:
            nom = item.get("alumno", "").strip().capitalize()
            inf = item.get("informe", "").strip()
            mem = item.get("memoria_evolutiva", "").strip()
            if nom:
                filas.append([docente, nom, inf, mem, "", fecha_alta])
        if filas:
            sheet.append_rows(filas)
        return True
    except Exception as e:
        if "200" in str(e): return True
        return False

def leer_alumnos_aula(docente):
    try:
        sheet = conectar_hoja_alumnos()
        if sheet is None: return []
        valores = sheet.get_all_values()
        if not valores or len(valores) <= 1: return []
        
        headers = [h.strip() for h in valores[0]]
        idx_doc = headers.index("Docente") if "Docente" in headers else 0
        idx_alu = headers.index("Alumno") if "Alumno" in headers else 1
        idx_inf = headers.index("Informe_Inicial") if "Informe_Inicial" in headers else 2
        idx_mem = headers.index("Memoria_Evolutiva") if "Memoria_Evolutiva" in headers else -1
        idx_act = headers.index("Ultima_Actualizacion") if "Ultima_Actualizacion" in headers else -1
        idx_fec = headers.index("Fecha_Alta") if "Fecha_Alta" in headers else (3 if idx_mem == -1 else 5)
        
        alumnos_docente = []
        for i, fila in enumerate(valores):
            if i == 0: continue
            if len(fila) > max(idx_doc, idx_alu) and docente.lower() in fila[idx_doc].strip().lower():
                nom = fila[idx_alu].strip().capitalize()
                inf = fila[idx_inf].strip() if len(fila) > idx_inf else ""
                mem = fila[idx_mem].strip() if idx_mem != -1 and len(fila) > idx_mem else ""
                act = fila[idx_act].strip() if idx_act != -1 and len(fila) > idx_act else ""
                fec = fila[idx_fec].strip() if len(fila) > idx_fec else ""
                alumnos_docente.append({
                    "alumno": nom,
                    "informe": inf,
                    "memoria_evolutiva": mem,
                    "ultima_actualizacion": act,
                    "fecha": fec
                })
        return alumnos_docente
    except Exception:
        return []

def actualizar_informe_alumno(docente, nombre_alumno, nuevo_informe):
    try:
        sheet = conectar_hoja_alumnos()
        if sheet is None: return False
        valores = sheet.get_all_values()
        if not valores: return False
        
        headers = [h.strip() for h in valores[0]]
        idx_doc = headers.index("Docente") if "Docente" in headers else 0
        idx_alu = headers.index("Alumno") if "Alumno" in headers else 1
        idx_inf = headers.index("Informe_Inicial") if "Informe_Inicial" in headers else 2
        
        for idx, fila in enumerate(valores):
            if idx == 0: continue
            if len(fila) > max(idx_doc, idx_alu) and docente.lower() in fila[idx_doc].strip().lower() and nombre_alumno.lower() == fila[idx_alu].strip().lower():
                sheet.update_cell(idx + 1, idx_inf + 1, nuevo_informe.strip())
                return True
        return False
    except Exception as e:
        if "200" in str(e): return True
        return False

def coincide_alumno(nombre1, nombre2):
    if not nombre1 or not nombre2: return False
    n1 = nombre1.strip().lower()
    n2 = nombre2.strip().lower()
    if n1 == n2: return True
    p1 = n1.split()[0]
    p2 = n2.split()[0]
    if p1 == p2 and len(p1) >= 3: return True
    if n1 in n2 or n2 in n1: return True
    return False

def extraer_json_seguro(texto):
    if not texto: return {}
    t = texto.strip()
    if "```" in t:
        partes = t.split("```")
        for p in partes:
            p_limpio = p.strip()
            if p_limpio.startswith("json"):
                p_limpio = p_limpio[4:].strip()
            if p_limpio.startswith("{") and p_limpio.endswith("}"):
                try:
                    return json.loads(p_limpio)
                except Exception:
                    pass
    inicio = t.find("{")
    fin = t.rfind("}")
    if inicio != -1 and fin != -1 and fin > inicio:
        try:
            return json.loads(t[inicio:fin+1])
        except Exception:
            pass
    try:
        return json.loads(t)
    except Exception:
        return {}

def actualizar_memoria_evolutiva_alumnos(docente, dict_memorias):
    try:
        sheet = conectar_hoja_alumnos()
        if sheet is None: return False
        valores = sheet.get_all_values()
        if not valores: return False
        
        headers = [h.strip() for h in valores[0]]
        if "Memoria_Evolutiva" not in headers:
            nuevas_filas = [CABECERAS_ALUMNOS]
            for f in valores[1:]:
                doc = f[0] if len(f) > 0 else ""
                alu = f[1] if len(f) > 1 else ""
                inf = f[2] if len(f) > 2 else ""
                fec = f[3] if len(f) > 3 else ""
                nuevas_filas.append([doc, alu, inf, "", "", fec])
            sheet.clear()
            sheet.update(nuevas_filas)
            valores = nuevas_filas
            headers = CABECERAS_ALUMNOS
            
        idx_doc = headers.index("Docente")
        idx_alu = headers.index("Alumno")
        idx_mem = headers.index("Memoria_Evolutiva")
        idx_act = headers.index("Ultima_Actualizacion")
        
        fecha_act = datetime.now().strftime("%d/%m/%Y %H:%M")
        modificado = False
        
        for idx, fila in enumerate(valores):
            if idx == 0: continue
            if len(fila) > max(idx_doc, idx_alu) and docente.lower() in fila[idx_doc].strip().lower():
                nom_actual = fila[idx_alu].strip()
                for nom_target, nueva_mem in dict_memorias.items():
                    if coincide_alumno(nom_target, nom_actual):
                        while len(fila) < len(headers):
                            fila.append("")
                        fila[idx_mem] = nueva_mem.strip()
                        fila[idx_act] = fecha_act
                        modificado = True
                        break
                        
        if modificado:
            sheet.clear()
            sheet.update(valores)
            return True
        return True
    except Exception as e:
        if "200" in str(e): return True
        return False

def sintetizar_memoria_evolutiva(modelo_ia, dict_contextos, fecha_str):
    try:
        if not dict_contextos:
            return {}
            
        bloques = []
        for nom, ctx in dict_contextos.items():
            bloques.append(f"""
=== ALUMNO: {nom} ===
- Evaluación Inicial del Docente: {ctx.get('informe_inicial', 'Sin informe previo')}
- Memoria Pedagógica Evolutiva Previa: {ctx.get('memoria_previa', 'Sin memoria previa registrada')}
- Nuevas Evidencias y Observaciones de Hoy ({fecha_str}): {ctx.get('observaciones_hoy', 'Sin notas hoy')}
""")
        prompt_memoria = f"""
Actúa como Pinter, el búho pedagógico copiloto de Inteligencia Artificial para Educación Infantil, psicología evolutiva y evaluación formativa.

PRINCIPIO FUNDAMENTAL E INVIOLABLE:
Actúas exclusivamente como un COPILOTO pedagógico que detecta patrones temporales observables (tales como la ansiedad matemática, bloqueos de frustración o dinámicas de aislamiento/timidez), pero en NINGÚN caso formulas diagnósticos clínicos, psicopatológicos ni calificaciones formales o cuantitativas.
El juicio axiológico, la deliberación cualitativa y la decisión final evaluadora e interventora corresponden siempre y de manera indelegable al educador.
Tus textos son hipótesis y evidencias de apoyo para enriquecer la mirada reflexiva de la maestra o maestro.

Tu cometido es actualizar y enriquecer la **Memoria Pedagógica Evolutiva** de cada alumno listado a continuación.
Debes integrar lo observado hoy con el contexto histórico previo, COMPARANDO y detectando evolución:
- ¿Ha avanzado en aspectos que antes le resultaban difíciles (ej. tolerancia a la frustración, expresión verbal, resolución de conflictos, autonomía en rutinas)?
- ¿Se observan nuevos intereses, habilidades lógicas ABN, hábitos o expresiones emocionales?
- Conserva SIEMPRE los hitos y aprendizajes consolidados con anterioridad; no borres contexto valioso, sino condénsalo y actualízalo en una síntesis fluida, respetuosa y constructiva.

Alumnos a procesar:
{''.join(bloques)}

Para cada alumno, genera un texto pedagógico formal, descriptivo y no patologizante (máximo 150-200 palabras) estructurado de forma clara en:
- Desarrollo Socioemocional y Convivencia (autorregulación, interacción con iguales y adultos).
- Aprendizajes y Competencias de Aula (lógica ABN, comunicación, psicomotricidad y curiosidad).
- Focos de Apoyo y Recomendaciones de Acompañamiento vigentes (hipótesis de apoyo para consideración del docente).

IMPORTANTE: Como clave de cada alumno en el JSON devuelto, utiliza EXACTAMENTE su nombre tal como se indica arriba en su bloque correspondiente.

Responde ÚNICAMENTE con un JSON válido con la siguiente estructura (sin comillas de bloque ```json ni texto adicional):
{{
  "NombreAlumno": "Texto completo de la memoria evolutiva actualizada...",
  ...
}}
"""
        resp = modelo_ia.generate_content(prompt_memoria.strip()).text
        return extraer_json_seguro(resp)
    except Exception:
        return {}

# --- FUNCIONES DE ASISTENCIA DIARIA ---
def conectar_hoja_asistencia():
    try:
        sh = conectar_google_sheets()
        if sh is None: return None
        try:
            sheet_asist = sh.worksheet("Asistencia_Aula")
        except gspread.WorksheetNotFound:
            sheet_asist = sh.add_worksheet(title="Asistencia_Aula", rows="2000", cols="5")
            sheet_asist.append_row(["Fecha", "Docente", "Alumno", "Estado"])
        return sheet_asist
    except Exception:
        return None

def guardar_asistencia_diaria(docente, fecha_str, dict_asistencia):
    try:
        sheet = conectar_hoja_asistencia()
        if sheet is None: return False
        valores = sheet.get_all_values()
        if not valores:
            sheet.append_row(["Fecha", "Docente", "Alumno", "Estado"])
            valores = sheet.get_all_values()
        
        nuevas_filas = [valores[0]] if valores else [["Fecha", "Docente", "Alumno", "Estado"]]
        for f in valores[1:]:
            if len(f) >= 3:
                if f[0] == fecha_str and f[1].lower() == docente.lower():
                    continue
                nuevas_filas.append(f)
        
        for alumno, estado in dict_asistencia.items():
            nuevas_filas.append([fecha_str, docente, alumno.capitalize(), estado])
            
        sheet.clear()
        sheet.update(nuevas_filas)
        return True
    except Exception as e:
        if "200" in str(e): return True
        return False

def leer_asistencia_docente(docente):
    try:
        sheet = conectar_hoja_asistencia()
        if sheet is None: return []
        valores = sheet.get_all_values()
        if not valores or len(valores) <= 1: return []
        asistencias = []
        for i, fila in enumerate(valores):
            if i == 0: continue
            if len(fila) >= 4 and docente.lower() in fila[1].strip().lower():
                asistencias.append({
                    "fecha": fila[0].strip(),
                    "docente": fila[1].strip(),
                    "alumno": fila[2].strip().capitalize(),
                    "estado": fila[3].strip()
                })
        return asistencias
    except Exception:
        return []

# --- FINALIZAR CURSO ESCOLAR ---
def finalizar_curso_docente(docente):
    try:
        sh = conectar_google_sheets()
        if sh is None: return False
        
        # 1. Alumnos
        try:
            sh_al = sh.worksheet("Alumnos_Aula")
            vals = sh_al.get_all_values()
            if vals:
                filtrados = [v for i, v in enumerate(vals) if i == 0 or (len(v) >= 1 and docente.lower() not in v[0].lower())]
                sh_al.clear()
                if filtrados:
                    sh_al.update(filtrados)
        except Exception:
            pass
            
        # 2. Asistencia
        try:
            sh_as = sh.worksheet("Asistencia_Aula")
            vals = sh_as.get_all_values()
            if vals:
                filtrados = [v for i, v in enumerate(vals) if i == 0 or (len(v) >= 2 and docente.lower() not in v[1].lower())]
                sh_as.clear()
                if filtrados:
                    sh_as.update(filtrados)
        except Exception:
            pass
            
        # 3. Diario
        try:
            sh_di = sh.worksheet("Diario_Aula")
            vals = sh_di.get_all_values()
            if vals:
                filtrados = [v for i, v in enumerate(vals) if i == 0 or (len(v) >= 2 and docente.lower() not in v[1].lower())]
                sh_di.clear()
                if filtrados:
                    sh_di.update(filtrados)
        except Exception:
            pass
            
        return True
    except Exception:
        return False

# --- FUNCIONES DE AUTENTICACIÓN ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def obtener_usuarios():
    try:
        sh = conectar_google_sheets()
        if sh is None: return None
        try:
            sheet_usuarios = sh.worksheet("Usuarios")
        except gspread.WorksheetNotFound:
            return "NO_EXISTE"
        
        registros = sheet_usuarios.get_all_values()
        
        # Si la hoja está completamente vacía, el robot escribe las cabeceras automáticamente
        if not registros:
            sheet_usuarios.append_row(["Usuario", "Password"])
            return {} # No hay usuarios aún
            
        usuarios = {}
        for i, fila in enumerate(registros):
            if i == 0: continue # saltar la cabecera
            if len(fila) >= 2:
                usuarios[fila[0]] = fila[1]
        return usuarios
    except Exception as e:
        return None

def registrar_nuevo_usuario(usuario, password):
    try:
        sh = conectar_google_sheets()
        if sh is None: return False
        sheet_usuarios = sh.worksheet("Usuarios")
        
        # Si la hoja está vacía, añadimos las cabeceras primero
        if not sheet_usuarios.get_all_values():
            sheet_usuarios.append_row(["Usuario", "Password"])
            
        sheet_usuarios.append_row([usuario, hash_password(password)])
        return True
    except Exception:
        return False

# --- FUNCIÓN DE LECTURA DIAGNÓSTICA ---
def leer_todo_bruto():
    try:
        sh = conectar_google_sheets()
        if sh is None: return "Error de conexión", []
        sheet = sh.sheet1
        
        # LEEMOS TODO SIN PROCESAR
        datos_brutos = sheet.get_all_values()
        return "OK", datos_brutos
    except Exception as e:
        return f"Error leyendo: {e}", []

def borrar_registro_historial(indice_fila_0_based, fecha=None, usuario=None, herramienta=None):
    try:
        sh = conectar_google_sheets()
        if sh is None: return False
        sheet = sh.sheet1
        num_fila = indice_fila_0_based + 1
        
        vals = sheet.get_all_values()
        if 0 <= indice_fila_0_based < len(vals):
            fila_actual = vals[indice_fila_0_based]
            if not fecha or (len(fila_actual) >= 3 and fila_actual[0] == fecha and fila_actual[2] == herramienta):
                sheet.delete_rows(num_fila)
                return True
            
            for idx_real, f in enumerate(vals):
                if idx_real == 0: continue
                if len(f) >= 3 and f[0] == fecha and (usuario and usuario.lower() in f[1].lower()) and f[2] == herramienta:
                    sheet.delete_rows(idx_real + 1)
                    return True

        sheet.delete_rows(num_fila)
        return True
    except Exception as e:
        try:
            sh = conectar_google_sheets()
            sheet = sh.sheet1
            vals = sheet.get_all_values()
            fila_encontrada = None
            if 0 <= indice_fila_0_based < len(vals):
                fila_encontrada = indice_fila_0_based
            elif fecha:
                for idx_real, f in enumerate(vals):
                    if len(f) >= 3 and f[0] == fecha and f[2] == herramienta:
                        fila_encontrada = idx_real
                        break
            if fila_encontrada is not None:
                vals.pop(fila_encontrada)
                sheet.clear()
                if vals:
                    sheet.update(vals)
                return True
        except Exception:
            return False
        return False

# --- 3. IMAGEN Y CSS ---
def imagen_segura(ruta_imagen, ancho_css, clase_extra=""):
    if os.path.exists(ruta_imagen):
        with open(ruta_imagen, "rb") as img_file:
            b64_string = base64.b64encode(img_file.read()).decode()
        html = f"""<img src="data:image/png;base64,{b64_string}" class="{clase_extra}" style="width:{ancho_css}; pointer-events: none; display: block; margin: auto;">"""
        st.markdown(html, unsafe_allow_html=True)

st.markdown("""<style>html, body, [class*="css"] { font-family: 'Times New Roman', serif; } img { pointer-events: none !important; } [data-testid="StyledFullScreenButton"] { display: none !important; } @media only screen and (max-width: 768px) { .logo-esquina { display: none !important; } h1 { text-align: center; } } .stTextArea textarea { font-size: 16px !important; }</style>""", unsafe_allow_html=True)

# --- 4. BARRA LATERAL ---
with st.sidebar:
    imagen_segura("images/logo1.png", "85%") 
    st.write("") 
    # Placeholder para mantener el formulario de login arriba
    contenedor_login = st.empty()
    
    tema = st.radio("Apariencia:", ["Claro", "Oscuro"], horizontal=True)

if tema == "Claro":
    c_bg_app = "#FDFBF7"; c_text_main = "#4A4A4A"; c_sidebar = "#F9F5EB"; c_sidebar_text = "#4A4A4A" 
    c_caja_chat = "#FFFFFF"; c_input_bg = "#FFFFFF"; c_input_text = "#000000"; c_btn_bg = "#F0F0F0"; c_btn_text = "#000000"; c_border = "#DDDDDD"; img_fondo = 'url("https://www.transparenttextures.com/patterns/cream-paper.png")'
else:
    c_bg_app = "#3E2F28"; c_text_main = "#FFFFFF"; c_sidebar = "#4E3B32"; c_sidebar_text = "#FFFFFF" 
    c_caja_chat = "#5D473D"; c_input_bg = "#FFF8E7"; c_input_text = "#3E2F28"; c_btn_bg = "#F4D03F"; c_btn_text = "#1E1611"; c_border = "#F4D03F"; img_fondo = 'url("https://www.transparenttextures.com/patterns/black-linen.png")'

st.markdown(f"""<style>.stApp {{ background-color: {c_bg_app}; background-image: {img_fondo}; }} html, body, h1, h2, h3, p, label, div, .stMarkdown {{ color: {c_text_main} !important; }} section[data-testid="stSidebar"] {{ background-color: {c_sidebar}; border-right: 1px solid {c_border}; }} section[data-testid="stSidebar"] * {{ color: {c_sidebar_text} !important; }} .stTextInput input, .stTextArea textarea {{ background-color: {c_input_bg} !important; color: {c_input_text} !important; border: 2px solid {c_border} !important; }} .stButton > button {{ background-color: {c_btn_bg} !important; color: {c_btn_text} !important; border: 1px solid {c_text_main} !important; font-weight: bold !important; }} .stChatMessage {{ background-color: {c_caja_chat}; border: 1px solid {c_border}; }} .stInfo, .stSuccess {{ background-color: {c_caja_chat} !important; color: {c_text_main} !important; border: 1px solid {c_border}; }} .caja-sesion {{ background-color: {c_bg_app}; padding: 10px; border-radius: 8px; border: 2px solid {c_border}; color: {c_text_main}; text-align: center; margin-bottom: 10px; font-size: 16px; }}</style>""", unsafe_allow_html=True)

if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = None

with contenedor_login.container():
    if st.session_state.usuario_actual is None:
        tab_login, tab_registro = st.tabs(["Iniciar Sesión", "Registrarse"])
        
        with tab_login:
            st.info("Introduce tus credenciales para acceder.")
            log_usr = st.text_input("Usuario:", key="log_usr")
            log_pwd = st.text_input("Contraseña:", type="password", key="log_pwd")
            if st.button("Entrar", use_container_width=True):
                if not log_usr or not log_pwd:
                    st.error("Rellena ambos campos.")
                else:
                    usrs = obtener_usuarios()
                    if usrs == "NO_EXISTE":
                        st.error("Aún falta crear la pestaña 'Usuarios' en el Excel original.")
                    elif usrs is None:
                        st.error("Error de conexión con Google Sheets.")
                    else:
                        pwd_hash = hash_password(log_pwd)
                        if log_usr in usrs and usrs[log_usr] == pwd_hash:
                            st.session_state.usuario_actual = log_usr
                            st.rerun()
                        else:
                            st.error("Usuario o contraseña incorrectos.")
        
        with tab_registro:
            st.info("Crea una cuenta nueva.")
            reg_usr = st.text_input("Nuevo Usuario:", key="reg_usr")
            reg_pwd = st.text_input("Nueva Contraseña:", type="password", key="reg_pwd")
            if st.button("Registrar", use_container_width=True):
                if not reg_usr or not reg_pwd:
                    st.error("Rellena ambos campos.")
                else:
                    usrs = obtener_usuarios()
                    if usrs == "NO_EXISTE":
                        st.error("Aún falta crear la pestaña 'Usuarios' en el Excel original.")
                    elif usrs is None:
                        st.error("Error de conexión.")
                    elif reg_usr in usrs:
                        st.error("Ese usuario ya existe. Elige otro.")
                    else:
                        if registrar_nuevo_usuario(reg_usr, reg_pwd):
                            st.success("¡Registro completado! Ya puedes iniciar sesión en la otra pestaña.")
                        else:
                            st.error("No se pudo registrar. Inténtalo más tarde.")
        st.stop()
    else:
        st.markdown(f"<div class='caja-sesion'>Sesión de: <b>{st.session_state.usuario_actual}</b></div>", unsafe_allow_html=True)
        if st.button("Cerrar Sesión", use_container_width=True):
            st.session_state.usuario_actual = None
            st.rerun()
        
        usuario_actual = st.session_state.usuario_actual

class ModeloGeminiResiliente:
    """
    Envoltura de alta disponibilidad para Google Gemini.
    Alterna automáticamente entre modelos oficiales para asegurar disponibilidad
    ininterrumpida frente a límites de cuota (429) o saturación temporal.
    """
    def __init__(self):
        self.candidatos = [
            'gemini-3.8-flash',
            'gemini-flash-latest',
            'gemini-3.7-flash',
            'gemini-3.5-flash',
            'gemini-flash-lite-latest'
        ]
        self.idx_activo = 0

    def generate_content(self, prompt, **kwargs):
        ultimo_error = None
        for offset in range(len(self.candidatos)):
            idx = (self.idx_activo + offset) % len(self.candidatos)
            modelo_nombre = self.candidatos[idx]
            try:
                instancia = genai.GenerativeModel(modelo_nombre)
                resultado = instancia.generate_content(prompt, **kwargs)
                self.idx_activo = idx
                return resultado
            except Exception as e:
                err_str = str(e).lower()
                ultimo_error = e
                if any(k in err_str for k in ["429", "quota", "limit", "exhausted", "not found", "404", "503", "unavailable"]):
                    continue
                else:
                    raise e
        raise ultimo_error

try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = ModeloGeminiResiliente()
except Exception as e: st.error(f"Error IA: {e}")

with st.sidebar:
    st.markdown("---")
    
    # 3, 4 y 5. SECCIONES DE NAVEGACIÓN (En un solo Radio para mantener el estilo limpio original)
    opciones = [
        "Chat Asistente General", 
        "Diario Vivo del Aula",
        "Traductor Pedagógico (LOMLOE)", 
        "Cuentos Terapéuticos", 
        "Diseñador ABN & Retos", 
        "Ver MI Historial"
    ]
    
    if "modo" not in st.session_state or st.session_state.modo not in opciones:
        st.session_state.modo = "Chat Asistente General"
        
    idx_modo = opciones.index(st.session_state.modo)
    modo = st.radio("Herramientas Docentes:", opciones, index=idx_modo)
    st.session_state.modo = modo

import uuid

def crear_encabezado(titulo, id_unico):
    # Hack definitivo para evitar el bug de "título congelado" (React Reconciliation Bug)
    c = st.container()
    for _ in range(id_unico):
        c = c.container()
        
    with c:
        c_txt, c_img = st.columns([0.85, 0.15])
        with c_txt: 
            st.title(titulo)
        with c_img: 
            if os.path.exists("images/logo.png"):
                st.image("images/logo.png", use_container_width=True)

# -- CONTENIDO DE CADA HERRAMIENTA --
if modo == "Diario Vivo del Aula":
    st.empty()
    crear_encabezado("Diario Vivo del Aula", 6)
    st.caption(
        "**Principio de Supervisión Docente:** Pinter actúa exclusivamente como copiloto pedagógico para la detección de patrones temporales de aula. "
        "En ningún caso delega ni automatiza diagnósticos clínicos ni calificaciones formales. "
        "El juicio axiológico y la decisión final corresponden siempre de manera indelegable al educador."
    )
    
    alumnos_registrados = leer_alumnos_aula(usuario_actual)
    registros_historicos = leer_diario_aula(usuario_actual)
    asistencias_historico = leer_asistencia_docente(usuario_actual)
    
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    asistencias_hoy = {a["alumno"]: a["estado"] for a in asistencias_historico if a["fecha"] == fecha_hoy}
    
    # ALERTA PROACTIVA DE PINTER (Solo si hay alumnos registrados)
    if alumnos_registrados:
        alumnos_sin_notas = []
        fecha_actual = datetime.now()
        for al in alumnos_registrados:
            nom = al["alumno"]
            notas_este = [r for r in registros_historicos if r["alumno"].lower() == nom.lower()]
            if not notas_este:
                alumnos_sin_notas.append(nom)
            else:
                try:
                    ult_fecha_str = notas_este[-1]["fecha"]
                    ult_dt = datetime.strptime(ult_fecha_str.split()[0], "%d/%m/%Y")
                    if (fecha_actual - ult_dt).days >= 5:
                        alumnos_sin_notas.append(nom)
                except Exception:
                    pass
                    
        if alumnos_sin_notas:
            txt_nombres = ", ".join([f"**{n}**" for n in alumnos_sin_notas[:4]])
            st.warning(f"**Aviso de Pinter:** Hace tiempo que no tomas notas sobre {txt_nombres}. Conviene prestarles especial atención hoy en el aula.")

    tab_cuadritos, tab_asistencia, tab_vivencias, tab_radar, tab_gestion = st.tabs([
        "Fichas de Alumnos",
        "Asistencia Diaria",
        "Vivencias Significativas",
        "Radar del Aula y Alertas",
        "Gestión y Fin de Curso"
    ])
    
    # 1. CUADRITOS DE ALUMNOS (CARDS INTERACTIVAS)
    with tab_cuadritos:
        if not alumnos_registrados:
            st.info("**Bienvenida/o al nuevo curso escolar:** Aún no tienes alumnos registrados en este curso.")
            st.markdown("Ve a la pestaña **'Gestión y Fin de Curso'** para indicar el número de alumnos y sus informes iniciales.")
        else:
            st.markdown(f"### Aula ({len(alumnos_registrados)} alumnos)")
            st.caption("Haz clic en cualquier alumno para desplegar su informe individualizado y su histórico de observaciones.")
            
            num_cols = 3
            cols = st.columns(num_cols)
            for idx, al in enumerate(alumnos_registrados):
                with cols[idx % num_cols]:
                    with st.container(border=True):
                        st.markdown(f"#### {al['alumno']}")
                        
                        est_hoy = asistencias_hoy.get(al["alumno"], "Pendiente")
                        if est_hoy == "Presente":
                            st.success("Presente hoy")
                        elif est_hoy == "Ausente":
                            st.error("Ausente hoy")
                        elif est_hoy == "Justificada":
                            st.warning("Falta Justificada")
                        else:
                            st.info("Asistencia de hoy pendiente")
                            
                        with st.expander("Expediente y Memoria Pedagógica (Ver / Editar)"):
                            st.markdown("**Informe Inicial del Docente (Punto de partida):**")
                            inf_actual = al["informe"] if al["informe"] else ""
                            nuevo_inf = st.text_area(
                                "Editar informe inicial:", 
                                value=inf_actual, 
                                key=f"edit_inf_{al['alumno']}",
                                height=85,
                                label_visibility="collapsed",
                                placeholder="Punto de partida, intereses, personalidad y necesidades de acompañamiento..."
                            )
                            aviso_inf = st.session_state.pop(f"aviso_inf_{al['alumno']}", None)
                            if aviso_inf == "exito":
                                st.success("¡Informe inicial actualizado con éxito!")
                            elif aviso_inf == "error":
                                st.error("Error al actualizar en Google Sheets.")
                            if st.button("Guardar Cambios en Informe Inicial", key=f"btn_save_inf_{al['alumno']}", use_container_width=True):
                                exito_inf = False
                                with st.spinner("Actualizando informe en Google Drive..."):
                                    exito_inf = actualizar_informe_alumno(usuario_actual, al["alumno"], nuevo_inf)
                                st.session_state[f"aviso_inf_{al['alumno']}"] = "exito" if exito_inf else "error"
                                st.rerun()
                                        
                            st.markdown("---")
                            st.markdown("**Memoria Pedagógica Evolutiva (Pinter):**")
                            st.caption("Síntesis orientativa de patrones temporales para la deliberación pedagógica exclusiva del docente. No constituye diagnóstico clínico ni calificación formal.")
                            mem_actual = al.get("memoria_evolutiva", "").strip()
                            fec_act = al.get("ultima_actualizacion", "").strip()
                            if mem_actual:
                                if fec_act:
                                    st.caption(f"Última síntesis evolutiva: {fec_act}")
                                st.info(mem_actual)
                            else:
                                st.caption("Aún no se ha generado una memoria evolutiva para este alumno. Pinter la construirá automáticamente cuando registres vivencias diarias en el aula.")
                                
                            notas_al = [r for r in registros_historicos if coincide_alumno(r["alumno"], al["alumno"])]
                            asist_al = [a for a in asistencias_historico if coincide_alumno(a["alumno"], al["alumno"])]
                            total_faltas = len([a for a in asist_al if a["estado"] in ["Ausente", "Justificada"]])
                            
                            aviso_mem = st.session_state.pop(f"aviso_mem_{al['alumno']}", None)
                            if aviso_mem == "exito":
                                st.success("¡Memoria pedagógica sintetizada con éxito!")
                            elif aviso_mem == "error":
                                st.warning("No se pudo generar la memoria. Comprueba que existan datos u observaciones.")
                                
                            if st.button("Sintetizar Memoria con Pinter", key=f"btn_regen_mem_{al['alumno']}", use_container_width=True):
                                exito_mem = False
                                with st.spinner("Pinter está analizando el historial acumulado del alumno..."):
                                    notas_texto = "; ".join([f"[{r['fecha']}] {r['categoria']} ({r['estado']}): {r['detalle']}" for r in notas_al])
                                    nom_target = al['alumno']
                                    res_mem = sintetizar_memoria_evolutiva(
                                        model,
                                        {
                                            nom_target: {
                                                "informe_inicial": nuevo_inf if nuevo_inf else "Sin informe previo",
                                                "memoria_previa": mem_actual if mem_actual else "Sin memoria previa",
                                                "observaciones_hoy": notas_texto if notas_texto else "Sin observaciones registradas aún"
                                            }
                                        },
                                        fecha_hoy
                                    )
                                    mem_extraida = None
                                    if res_mem:
                                        if nom_target in res_mem:
                                            mem_extraida = res_mem[nom_target]
                                        else:
                                            for k, v in res_mem.items():
                                                if coincide_alumno(k, nom_target):
                                                    mem_extraida = v
                                                    break
                                            if not mem_extraida and len(res_mem) == 1:
                                                mem_extraida = list(res_mem.values())[0]
                                                
                                    if mem_extraida:
                                        actualizar_memoria_evolutiva_alumnos(usuario_actual, {nom_target: mem_extraida})
                                        exito_mem = True
                                        
                                st.session_state[f"aviso_mem_{al['alumno']}"] = "exito" if exito_mem else "error"
                                st.rerun()
                                        
                            st.divider()
                            st.caption(f"Observaciones del curso: **{len(notas_al)}** | Faltas acumuladas: **{total_faltas}**")
                            if notas_al:
                                ult = notas_al[-1]
                                st.caption(f"Última vivencia ({ult['fecha']}): {ult['detalle']}")
                                
                            if st.button("Redactar Informe LOMLOE con Contexto Completo", key=f"btn_lomloe_card_{al['alumno']}", type="primary", use_container_width=True):
                                detalles_texto = "; ".join([f"[{r['fecha']}] {r['categoria']} ({r['estado']}): {r['detalle']}" for r in notas_al[-12:]])
                                informe_base = nuevo_inf if nuevo_inf else 'Sin informe previo'
                                memoria_base = mem_actual if mem_actual else 'Memoria en proceso de recopilación'
                                
                                texto_expediente = f"""
EXPEDIENTE INTEGRAL DEL ALUMNO PARA EVALUACIÓN FORMATIVA LOMLOE:
- Nombre: {al['alumno']}
- Evaluación Inicial del Docente (Punto de partida): {informe_base}
- Memoria Pedagógica Evolutiva (Pinter): {memoria_base}
- Estadísticas de Asistencia: {len(asist_al) - total_faltas} asistencias registradas, {total_faltas} ausencias.
- Registro Cronológico de Evidencias y Vivencias Significativas Recientes: {detalles_texto if detalles_texto else 'Sin incidencias adicionales registradas.'}
""".strip()
                                st.session_state.precarga_traductor_obs = texto_expediente
                                st.session_state.precarga_traductor_ctx = f"Evaluación continua, longitudinal y formativa LOMLOE de {al['alumno']}"
                                st.session_state.modo = "Traductor Pedagógico (LOMLOE)"
                                st.rerun()
                                
                            c_card_c, c_card_a = st.columns(2)
                            with c_card_c:
                                if st.button("Crear Cuento Terapéutico", key=f"btn_cuento_card_{al['alumno']}", use_container_width=True):
                                    prob_alumno = f"Acompañamiento socioemocional y confianza para {al['alumno']}"
                                    if mem_actual:
                                        prob_alumno = f"Apoyo para {al['alumno']}: {mem_actual[:120]}"
                                    elif notas_al:
                                        prob_alumno = f"Situación a acompañar para {al['alumno']}: {notas_al[-1]['detalle'][:120]}"
                                    inte_alumno = "Animales del bosque, trenes o aventuras divertidas"
                                    if nuevo_inf:
                                        inte_alumno = f"Intereses del alumno: {nuevo_inf[:100]}"
                                    st.session_state.precarga_cuento_prob = prob_alumno
                                    st.session_state.precarga_cuento_inte = inte_alumno
                                    st.session_state.modo = "Cuentos Terapéuticos"
                                    st.rerun()
                            with c_card_a:
                                if st.button("Diseñar Reto ABN", key=f"btn_abn_card_{al['alumno']}", use_container_width=True):
                                    st.session_state.precarga_abn_obj = f"Reforzar el razonamiento lógico-matemático y conteo manipulativo adaptado a {al['alumno']}"
                                    st.session_state.precarga_abn_mat = "Policubos, tapones y bandejas de clasificación"
                                    st.session_state.modo = "Diseñador ABN & Retos"
                                    st.rerun()

        # 2. ASISTENCIA DIARIA PERSISTENTE
        with tab_asistencia:
            st.markdown(f"### Pase de Asistencia — {fecha_hoy}")
            st.markdown("Marca la asistencia del grupo de hoy. Quedará registrada y acumulada día a día en tu Google Drive.")
            
            if st.session_state.pop("aviso_asistencia_guardada", False):
                st.success("¡Asistencia de hoy registrada con éxito en Google Drive!")
            
            dict_nueva_asistencia = {}
            for al in alumnos_registrados:
                c_nom, c_est = st.columns([0.4, 0.6])
                with c_nom:
                    st.markdown(f"**{al['alumno']}**")
                with c_est:
                    estado_previo = asistencias_hoy.get(al["alumno"], "Presente")
                    idx_previo = 0
                    if estado_previo == "Ausente": idx_previo = 1
                    elif estado_previo == "Justificada": idx_previo = 2
                    
                    sel_estado = st.radio(
                        f"Estado {al['alumno']}",
                        ["Presente", "Ausente", "Justificada"],
                        index=idx_previo,
                        horizontal=True,
                        key=f"asist_rad_{al['alumno']}",
                        label_visibility="collapsed"
                    )
                    dict_nueva_asistencia[al["alumno"]] = sel_estado
                    
            if st.button("Guardar Asistencia de Hoy", type="primary", use_container_width=True):
                exito_asist = False
                with st.spinner("Guardando registro de asistencia..."):
                    exito_asist = guardar_asistencia_diaria(usuario_actual, fecha_hoy, dict_nueva_asistencia)
                if exito_asist:
                    st.session_state.aviso_asistencia_guardada = True
                    st.rerun()
                else:
                    st.error("Error al guardar asistencia en Google Sheets.")
                        
            st.markdown("---")
            st.markdown("#### Historial de Ausencias del Curso:")
            conteo_faltas = {}
            for a in asistencias_historico:
                if a["estado"] in ["Ausente", "Justificada"]:
                    conteo_faltas[a["alumno"]] = conteo_faltas.get(a["alumno"], 0) + 1
                    
            if not conteo_faltas:
                st.info("¡Asistencia impecable! Aún no se registran ausencias en el aula.")
            else:
                for al_f, cant in conteo_faltas.items():
                    st.caption(f"• **{al_f}**: {cant} falta(s) acumulada(s)")

        # 3. VIVENCIAS SIGNIFICATIVAS (DIARIO COGNITIVO)
        with tab_vivencias:
            st.markdown("### Evaluación Continua y Observación de Aula")
            st.markdown(
                "Cuéntale a Pinter con tus propias palabras qué ha ocurrido hoy en clase con tus peques. "
                "Pinter detectará automáticamente a los alumnos de tu lista oficial, sus emociones, logros y conflictos."
            )
            
            if st.session_state.pop("aviso_diario_guardado", False):
                st.success("¡Registros guardados con éxito en el Diario Vivo y memoria pedagógica actualizada por Pinter!")
                
            if st.session_state.pop("limpiar_input_diario", False):
                st.session_state["input_diario_dia"] = ""
            
            ejemplo_placeholder = (
                "Ejemplo: Pinter, hoy ha faltado Hugo. Sofía ha tenido un momento de frustración con las construcciones matemáticas "
                "porque se le caían las torres, pero Lucas se ha sentado a su lado, la ha ayudado y ha compartido sus piezas con mucha empatía. "
                "Mateo ha participado con muchísima ilusión en la asamblea."
            )
            
            texto_diario = st.text_area(
                "¿Qué ha sucedido hoy en clase?", 
                height=130, 
                placeholder=ejemplo_placeholder,
                key="input_diario_dia"
            )
            
            if st.button("Analizar el día con Pinter", key="btn_analizar_diario", use_container_width=True):
                if not texto_diario.strip():
                    st.warning("Escribe primero lo ocurrido hoy en el aula para que Pinter pueda ayudarte.")
                else:
                    datos_extraidos = None
                    with st.spinner("Pinter está escuchando con atención, extrayendo las vivencias y organizando a tus peques..."):
                        prompt_diario = f"""
Actúa como Pinter, el copiloto pedagógico de Inteligencia Artificial para el docente de Educación Infantil.

PRINCIPIO FUNDAMENTAL E INDELEGABLE:
Actúas como un COPILOTO pedagógico que detecta patrones temporales observables de aula (tales como la ansiedad matemática, fluctuaciones emocionales o dinámicas de aislamiento/timidez), pero en NINGÚN caso formulas diagnósticos clínicos ni calificaciones formales.
Tus observaciones y sugerencias constituyen hipótesis de apoyo orientativas para el aula; el juicio axiológico y la decisión final evaluadora e interventora corresponden siempre y de manera indelegable al educador.

Analiza la siguiente observación informal del docente sobre su jornada escolar:
'{texto_diario}'

Tu tarea es extraer a cada alumno mencionado y devolver estrictamente un JSON válido con esta estructura:
{{
  "resumen_pinter": "Un mensaje cálido y motivador en 1-2 frases resumiendo el clima emocional y los hitos del aula.",
  "registros": [
    {{
      "alumno": "Nombre del alumno (solo el nombre de pila)",
      "categoria": "Asistencia" | "Emocional" | "Social/Valores" | "Cognitivo/Académico",
      "estado": "Ausente" | "Frustración" | "Alegría/Logro" | "Empatía/Cooperación" | "Conflicto" | "Timidez" | "Progreso",
      "detalle": "Explicación concisa y pedagógica (máximo 15 palabras) del patrón o conducta observable, sin emitir diagnósticos clínicos.",
      "alerta_intervencion": true o false (true si detectas un patrón de dificultad reiterada para consideración del educador),
      "sugerencia": "Breve sugerencia práctica lúdica o de mediación (ej: cuento sobre paciencia, juego ABN con material manipulativo, etc.)"
    }}
  ]
}}

Responde ÚNICAMENTE con el bloque JSON crudo (sin ```json ni texto introductorio).
"""
                        try:
                            resp_gemini = model.generate_content(prompt_diario.strip()).text
                            json_limpio = resp_gemini.strip()
                            if json_limpio.startswith("```"):
                                json_limpio = json_limpio.split("\n", 1)[1]
                            if json_limpio.endswith("```"):
                                json_limpio = json_limpio.rsplit("```", 1)[0]
                            datos_extraidos = json.loads(json_limpio.strip())
                        except Exception as e:
                            st.error(f"Hubo un problema al interpretar la observación: {e}")
                            
                    if datos_extraidos:
                        st.session_state.diario_resultado_temp = datos_extraidos
                        st.session_state.diario_texto_temp = texto_diario
                        st.rerun()
                            
            if "diario_resultado_temp" in st.session_state and st.session_state.diario_resultado_temp:
                res_datos = st.session_state.diario_resultado_temp
                st.markdown("---")
                st.info(f"**Pinter dice:** {res_datos.get('resumen_pinter', 'Observaciones analizadas correctamente.')}")
                
                st.markdown("#### Registros identificados por alumno:")
                regs = res_datos.get("registros", [])
                if not regs:
                    st.warning("Pinter no ha podido identificar nombres concretos de alumnos. Asegúrate de incluir los nombres (ej: Sofía, Hugo, Lucas).")
                else:
                    for idx, r in enumerate(regs):
                        alumno_nom = r.get("alumno", "Peque")
                        cat = r.get("categoria", "General")
                        est = r.get("estado", "Observación")
                        det = r.get("detalle", "")
                        sug = r.get("sugerencia", "")
                        alerta = r.get("alerta_intervencion", False)
                        alerta_txt = " [Alerta]" if alerta else ""
                            
                        with st.expander(f"**{alumno_nom}** — *{cat}* ({est}){alerta_txt}", expanded=True):
                            st.markdown(f"**Detalle pedagógico:** {det}")
                            if sug:
                                st.caption(f"*Sugerencia de Pinter:* {sug}")
                                
                    st.write("")
                    col_btn_guardar, col_btn_descartar = st.columns([0.7, 0.3])
                    with col_btn_guardar:
                        btn_guardar_diario = st.button("Confirmar y Guardar en el Diario Vivo", type="primary", use_container_width=True, key="btn_confirmar_diario")
                    with col_btn_descartar:
                        btn_descartar = st.button("Descartar", use_container_width=True, key="btn_descartar_diario")
                        
                    if btn_descartar:
                        st.session_state.pop("diario_resultado_temp", None)
                        st.session_state.pop("diario_texto_temp", None)
                        st.rerun()
                        
                    if btn_guardar_diario:
                        exito_guardar = False
                        with st.spinner("Guardando registros y actualizando la memoria evolutiva con Pinter..."):
                            exito_guardar = guardar_en_diario_aula(
                                usuario_actual, 
                                regs, 
                                st.session_state.get("diario_texto_temp", "")
                            )
                            if exito_guardar:
                                dict_ctx = {}
                                for r in regs:
                                    nom_r = r.get("alumno", "").strip()
                                    if not nom_r or nom_r.lower() in ["sin nombre", "peque"]:
                                        continue
                                    al_oficial = next((a for a in alumnos_registrados if coincide_alumno(nom_r, a["alumno"])), None)
                                    if al_oficial:
                                        nom_canonico = al_oficial["alumno"]
                                        if nom_canonico not in dict_ctx:
                                            inf_ini = al_oficial.get("informe") or "Sin informe inicial previo."
                                            mem_prev = al_oficial.get("memoria_evolutiva") or "Sin memoria previa registrada."
                                            dict_ctx[nom_canonico] = {
                                                "informe_inicial": inf_ini,
                                                "memoria_previa": mem_prev,
                                                "observaciones_hoy_lista": []
                                            }
                                        dict_ctx[nom_canonico]["observaciones_hoy_lista"].append(
                                            f"[{r.get('categoria', 'General')}] ({r.get('estado', 'Observación')}): {r.get('detalle', '')}"
                                        )
                                    else:
                                        nom_cap = nom_r.capitalize()
                                        if nom_cap not in dict_ctx:
                                            dict_ctx[nom_cap] = {
                                                "informe_inicial": "Sin informe previo.",
                                                "memoria_previa": "Sin memoria previa registrada.",
                                                "observaciones_hoy_lista": []
                                            }
                                        dict_ctx[nom_cap]["observaciones_hoy_lista"].append(
                                            f"[{r.get('categoria', 'General')}] ({r.get('estado', 'Observación')}): {r.get('detalle', '')}"
                                        )
                                        
                                if dict_ctx:
                                    dict_para_sintesis = {}
                                    for nom_k, datos_k in dict_ctx.items():
                                        dict_para_sintesis[nom_k] = {
                                            "informe_inicial": datos_k["informe_inicial"],
                                            "memoria_previa": datos_k["memoria_previa"],
                                            "observaciones_hoy": "; ".join(datos_k["observaciones_hoy_lista"])
                                        }
                                    res_mem = sintetizar_memoria_evolutiva(model, dict_para_sintesis, fecha_hoy)
                                    if res_mem:
                                        actualizar_memoria_evolutiva_alumnos(usuario_actual, res_mem)

                        if exito_guardar:
                            st.session_state.aviso_diario_guardado = True
                            st.session_state.limpiar_input_diario = True
                            st.session_state.pop("diario_resultado_temp", None)
                            st.session_state.pop("diario_texto_temp", None)
                            st.rerun()
                        else:
                            st.error("No se pudo conectar con Google Sheets. Revisa la conexión.")

        # 4. RADAR DEL AULA & ALERTAS
        with tab_radar:
            st.markdown("### Radar de Bienestar y Alertas Pedagógicas")
            st.caption(
                "Herramienta copiloto de detección de patrones temporales: apoya la mirada formativa del docente identificando recurrencias observables. "
                "En ningún caso emite diagnósticos clínicos ni calificaciones. La valoración axiológica y la decisión corresponden de forma indelegable al educador."
            )
            if not registros_historicos:
                st.info("Aún no tienes vivencias guardadas en el Diario Vivo. Ve a la pestaña **'Vivencias Significativas'** para registrar tu primera jornada.")
            else:
                total_obs = len(registros_historicos)
                alumnos_con_notas = sorted(list(set(r["alumno"] for r in registros_historicos if r.get("alumno"))))
                
                c_kpi1, c_kpi2, c_kpi3 = st.columns(3)
                c_kpi1.metric("Observaciones registradas", total_obs)
                c_kpi2.metric("Alumnos con seguimiento", len(alumnos_con_notas))
                c_kpi3.metric("Última actualización", registros_historicos[-1]["fecha"])
                
                st.markdown("---")
                st.markdown("#### Alertas Pedagógicas Proactivas:")
                
                alumnos_frustracion = {}
                for reg in registros_historicos:
                    al = reg["alumno"]
                    est = reg["estado"].lower()
                    if "frustra" in est or "conflicto" in est or "rabiet" in est or "triste" in est or "bloqueo" in est:
                        alumnos_frustracion[al] = alumnos_frustracion.get(al, 0) + 1
                        
                hay_alertas = False
                for al, veces in alumnos_frustracion.items():
                    if veces >= 1:
                        hay_alertas = True
                        st.warning(
                            f"**Patrón temporal detectado:** **{al}** acumula **{veces} registro(s)** recientes con observaciones de frustración, bloqueo o dificultad. Orientación pedagógica sugerida para valoración del docente:"
                        )
                        c_act1, c_act2 = st.columns(2)
                        with c_act1:
                            if st.button(f"Crear Cuento Terapéutico para {al}", key=f"btn_cuento_rad_{al}"):
                                st.session_state.precarga_cuento_prob = f"Manejo de la frustración, paciencia y calma para {al}"
                                st.session_state.precarga_cuento_inte = "Animales del bosque y superpoderes"
                                st.session_state.modo = "Cuentos Terapéuticos"
                                st.rerun()
                        with c_act2:
                            if st.button(f"Diseñar Reto ABN de Apoyo para {al}", key=f"btn_abn_rad_{al}"):
                                st.session_state.precarga_abn_obj = f"Reforzar la confianza y motivación matemática mediante manipulación lúdica (apoyo para {al})"
                                st.session_state.precarga_abn_mat = "Bandejas, tapones y pegatinas de colores"
                                st.session_state.modo = "Diseñador ABN & Retos"
                                st.rerun()
                                
                if not hay_alertas:
                    st.success("El clima del aula es favorable. No se detectan patrones de alerta o frustración reiterada en este momento.")
                    
                st.markdown("---")
                st.markdown("#### Histórico de Clima Emocional Reciente:")
                ultimos = registros_historicos[-6:]
                for u in reversed(ultimos):
                    st.caption(f"**{u['fecha']}** | **{u['alumno']}** ({u['categoria']}) : {u['detalle']}")

        # 5. GESTIÓN & FIN DE CURSO
        with tab_gestion:
            st.markdown("### Gestión del Alumnado y Fin de Curso")
            
            if st.session_state.pop("aviso_fin_curso", False):
                st.success("¡Curso escolar finalizado con éxito! El aula se ha reiniciado y está lista para el nuevo grupo.")
            if st.session_state.pop("aviso_aula_creada", False):
                st.success("¡Aula configurada con éxito! Ya tienes a tus peques registrados.")
            alumno_anadido = st.session_state.pop("aviso_alumno_anadido", None)
            if alumno_anadido:
                st.success(f"¡{alumno_anadido} añadido al aula con éxito!")
                
            if not alumnos_registrados:
                st.info("**Configuración del Nuevo Curso Escolar**")
                st.markdown(
                    "Indica cuántos alumnos tienes en clase y escribe el nombre y el informe individualizado inicial "
                    "de cada uno (su punto de partida formativo, gustos, necesidades de acompañamiento o personalidad). "
                    "Esta información quedará guardada de forma 100% permanente durante todo el curso escolar."
                )
                
                num_alumnos = st.number_input("Número de alumnos en el aula:", min_value=1, max_value=40, value=6, step=1)
                
                with st.form("form_inicio_curso"):
                    nuevos_alumnos = []
                    for i in range(int(num_alumnos)):
                        st.markdown(f"**Peque #{i+1}**")
                        col_n, col_inf = st.columns([0.35, 0.65])
                        with col_n:
                            n_al = st.text_input(f"Nombre Alumno #{i+1}", key=f"nom_ini_{i}", placeholder="Ej: Sofía Gómez")
                        with col_inf:
                            i_al = st.text_area(f"Informe inicial individualizado #{i+1}", key=f"inf_ini_{i}", height=70, placeholder="Ej: Muy cariñosa y atenta. Muestra algo de frustración si no le salen los bloques. Le apasionan los dinosaurios.")
                        nuevos_alumnos.append({"alumno": n_al, "informe": i_al})
                        
                    btn_guardar_curso = st.form_submit_button("Guardar Alumnado y Comenzar Curso Escolar", type="primary", use_container_width=True)
                    if btn_guardar_curso:
                        validos = [a for a in nuevos_alumnos if a["alumno"].strip()]
                        if not validos:
                            st.error("Por favor, introduce al menos el nombre de un alumno para comenzar.")
                        else:
                            exito_curso = False
                            with st.spinner("Creando el aula en Google Drive..."):
                                exito_curso = guardar_alumnos_aula(usuario_actual, validos)
                            if exito_curso:
                                st.session_state.aviso_aula_creada = True
                                st.rerun()
                            else:
                                st.error("Error al conectar con Google Sheets. Revisa la conexión.")
            else:
                st.markdown("#### Matricular nuevo alumno a mitad de curso:")
                with st.form("form_alta_individual"):
                    col_n1, col_inf1 = st.columns([0.35, 0.65])
                    with col_n1:
                        nom_nuevo = st.text_input("Nombre del nuevo alumno:", placeholder="Ej: Mateo Ruiz")
                    with col_inf1:
                        inf_nuevo = st.text_area("Informe individualizado inicial:", height=70, placeholder="Ej: Recién llegado del centro X. Le gusta pintar y jugar con arena.")
                    if st.form_submit_button("Añadir Alumno al Aula"):
                        if not nom_nuevo.strip():
                            st.error("Introduce el nombre del alumno.")
                        else:
                            exito_nuevo = False
                            with st.spinner("Guardando nuevo alumno en Google Drive..."):
                                exito_nuevo = guardar_alumnos_aula(usuario_actual, [{"alumno": nom_nuevo, "informe": inf_nuevo}])
                            if exito_nuevo:
                                st.session_state.aviso_alumno_anadido = nom_nuevo
                                st.rerun()
                            else:
                                st.error("Error al guardar alumno.")
                                
                st.divider()
                st.markdown("#### Cierre de Periodo Lectivo: Finalizar Curso Escolar")
                st.markdown(
                    "Cuando termine el curso escolar en junio, puedes pulsar este botón para **cerrar y reiniciar el aula**. "
                    "Esto borrará los alumnos, asistencias y notas de este curso para que puedas configurar el aula del año que viene desde cero."
                )
                
                check_fin = st.checkbox("Confirmo que el curso escolar ha finalizado y deseo reiniciar los datos del aula para el próximo año.", key="check_fin_curso")
                if st.button("Finalizar Curso Escolar y Reiniciar Aula", type="primary", disabled=not check_fin):
                    exito_fin = False
                    with st.spinner("Finalizando curso y reseteando aula en Google Drive..."):
                        exito_fin = finalizar_curso_docente(usuario_actual)
                    if exito_fin:
                        for k in ["diario_resultado_temp", "diario_texto_temp", "input_diario_dia"]:
                            st.session_state.pop(k, None)
                        st.session_state.aviso_fin_curso = True
                        st.rerun()
                    else:
                        st.error("Error al resetear los datos del curso en Google Sheets.")

elif modo == "Traductor Pedagógico (LOMLOE)":
    st.empty() # Limpiar residuos previos
    crear_encabezado("Traductor Pedagógico", 1)
    st.caption(
        "**Borrador Curricular Asistido:** Pinter actúa exclusivamente como copiloto estructurando evidencias pedagógicas para facilitar tu labor. "
        "En ningún caso automatiza diagnósticos clínicos ni calificaciones formales. El juicio axiológico y la evaluación final corresponden de forma indelegable al educador."
    )
    c1, c2 = st.columns(2)
    with c1:
        if "precarga_traductor_obs" in st.session_state:
            st.session_state.input_traductor_obs = st.session_state.pop("precarga_traductor_obs")
        if "precarga_traductor_ctx" in st.session_state:
            st.session_state.input_traductor_ctx = st.session_state.pop("precarga_traductor_ctx")
            
        if "input_traductor_obs" not in st.session_state:
            st.session_state.input_traductor_obs = ""
        if "input_traductor_ctx" not in st.session_state:
            st.session_state.input_traductor_ctx = ""
            
        obs = st.text_area("Observación / Expediente del Alumno:", key="input_traductor_obs", height=200)
        ctx = st.text_input("Contexto:", key="input_traductor_ctx")
        if st.button("Generar"):
            with st.spinner("Redactando informe curricular oficial (LOMLOE + DUA)..."):
                prompt_traductor = f"""
Actúa como un/a maestro/a experto/a en Educación Infantil y normativa LOMLOE, ejerciendo como copiloto de apoyo a la redacción pedagógica.

PRINCIPIO FUNDAMENTAL E INDELEGABLE:
Este informe es un borrador curricular y formativo estructurado para asistir al educador. En ningún caso automatiza diagnósticos clínicos, etiquetas patologizantes ni calificaciones numéricas o sumativas.
El juicio axiológico, la deliberación cualitativa y la decisión evaluadora final corresponden siempre y de manera indelegable al educador.

A partir de la información u observación pedagógica del docente:
'{obs}'
y el contexto de evaluación: '{ctx}', genera un informe técnico curricular exhaustivo y formal desglosado estrictamente en 3 bloques (usa Markdown):

### 1. Doble Redacción del Informe
* **Versión Familias:** Redacta un texto con tono empático, claro, constructivo y cercano, adecuado para un boletín de notas o tutoría, que sintetice los logros, la trayectoria emocional y la evolución del alumno sin juicios estigmatizantes ni calificaciones sumativas.
* **Versión Acta/Inspección:** Redacta la misma información con un registro formal, técnico, objetivo y pedagógico, apto para el expediente curricular oficial del centro educativo.

### 2. Vinculación LOMLOE Automática
Identifica y lista con precisión los elementos curriculares de Educación Infantil asociados a los aprendizajes y conductas observadas:
* **Competencias Específicas:** (Enuméralas con su descripción curricular)
* **Criterios de Evaluación:** (Enuméralos con su vinculación formativa)
* **Saberes Básicos:** (Enuméralos correspondientes a las áreas curriculares de Infantil)

### 3. Propuesta de Intervención (DUA)
Añade dos (2) orientaciones metodológicas prácticas basadas en el Diseño Universal para el Aprendizaje (DUA) para reforzar o intervenir pedagógicamente en el aula según las necesidades y focos de apoyo detectados, formuladas como sugerencias para consideración del docente.

Responde ÚNICAMENTE con los bloques solicitados, sin introducciones ni despedidas conversacionales.
"""
                res = model.generate_content(prompt_traductor.strip()).text
                st.session_state.trad_res, st.session_state.trad_in = res, f"{obs} | {ctx}"
    with c2:
        if "trad_res" in st.session_state:
            st.write(st.session_state.trad_res)
            if st.button("Guardar"):
                if guardar_en_drive(usuario_actual, "Traductor", st.session_state.trad_in, st.session_state.trad_res): st.success("¡Guardado!")

elif modo == "Cuentos Terapéuticos":
    st.empty()
    crear_encabezado("Cuentos Terapéuticos", 2)
    c1, c2 = st.columns([0.34, 0.66])
    with c1:
        if "precarga_cuento_prob" in st.session_state:
            st.session_state.input_cuento_prob = st.session_state.pop("precarga_cuento_prob")
        if "precarga_cuento_inte" in st.session_state:
            st.session_state.input_cuento_inte = st.session_state.pop("precarga_cuento_inte")
            
        if "input_cuento_prob" not in st.session_state:
            st.session_state.input_cuento_prob = ""
        if "input_cuento_inte" not in st.session_state:
            st.session_state.input_cuento_inte = ""
            
        prob = st.text_input("Problema o situación:", key="input_cuento_prob", placeholder="Ej: Gestión de la frustración, compartir juguetes...")
        inte = st.text_input("Interés motivador del peque:", key="input_cuento_inte", placeholder="Ej: Animales del bosque, trenes, dinosaurios...")
        
        c_edad, c_estilo = st.columns([0.35, 0.65])
        with c_edad:
            edad = st.select_slider("Edad", ["3", "4", "5"])
        with c_estilo:
            estilo_elegido = st.selectbox(
                "Estilo de Ilustración:",
                [
                    "Acuarela y Álbum Infantil",
                    "Dibujo Pastel y Crayón",
                    "Modelado Tierno en Plastilina"
                ]
            )

        if estilo_elegido == "Dibujo Pastel y Crayón":
            guia_estilo = "sweet children book illustration, soft pencil and pastel crayon textures, warm friendly characters, clean rounded shapes, minimalist cozy background, picture book art"
        elif estilo_elegido == "Modelado Tierno en Plastilina":
            guia_estilo = "cute soft claymation storybook illustration, smooth rounded plasticine textures, gentle studio lighting, charming stop-motion picture book style, clean background"
        else: # Acuarela y Álbum Infantil (Recomendado)
            guia_estilo = "charming children storybook watercolor illustration, warm pastel colors, soft gentle brushstrokes, clean rounded anatomy, clear distinct paws and hands, simple cozy background, picture book art"

        if edad == "3":
            num_pags_historia = 3
            guia_edad = """
- PÚBLICO: Educación Infantil de 3 años.
- LONGITUD Y RITMO: Cuento muy breve y tierno. Cada página debe tener EXACTAMENTE 2 a 3 frases cortas y sencillas (máximo 25 a 35 palabras por página).
- LENGUAJE: Muy claro, dulce, con onomatopeyas o gestos amables, evitando cualquier complejidad sintáctica.
- ESTRUCTURA (EXACTAMENTE 3 PÁGINAS):
  * Portada: Presenta el título y al protagonista.
  * Página 1 (Inicio): Presenta al personaje y su juego o momento cotidiano favorito.
  * Página 2 (El Reto): Pequeño tropiezo o reto cotidiano abordado con suavidad.
  * Página 3 (La Solución): Resolución feliz y aprendizaje positivo.
  * Moraleja: Frase breve de cierre pedagógico.
"""
        elif edad == "4":
            num_pags_historia = 4
            guia_edad = """
- PÚBLICO: Educación Infantil de 4 años.
- LONGITUD Y RITMO: Cuento de desarrollo intermedio. Cada página debe tener entre 3 y 4 frases fluidas (alrededor de 35 a 45 palabras por página).
- LENGUAJE: Descriptivo, expresivo, introduciendo pequeñas emociones y diálogos cercanos.
- ESTRUCTURA (EXACTAMENTE 4 PÁGINAS):
  * Portada: Presenta el título y al protagonista.
  * Página 1 (Inicio y Rutina): El personaje en su actividad cotidiana o entorno.
  * Página 2 (El Reto o Conflicto): Surge la dificultad, duda o frustración.
  * Página 3 (La Ayuda o Estrategia): El personaje intenta una nueva idea, pide ayuda o reflexiona.
  * Página 4 (El Éxito y Alegría): Solución cooperativa y celebración del avance.
  * Moraleja: Enseñanza pedagógica con reflexión para el aula.
"""
        else: # "5"
            num_pags_historia = 5
            guia_edad = """
- PÚBLICO: Educación Infantil de 5 años.
- LONGITUD Y RITMO: Cuento más desarrollado y completo. Cada página debe tener entre 4 y 5 frases bien estructuradas (alrededor de 50 a 65 palabras por página).
- LENGUAJE: Narrativa rica con matices, causa-efecto, empatía y mayor diálogo reflexivo.
- ESTRUCTURA (EXACTAMENTE 5 PÁGINAS):
  * Portada: Presenta el título y al protagonista.
  * Página 1 (Presentación y Contexto): Inicio de una pequeña aventura o proyecto del día.
  * Página 2 (El Conflicto o Gran Reto): La situación que pone a prueba la paciencia o la convivencia.
  * Página 3 (El Intento y Diálogo): El personaje habla con sus compañeros o busca alternativas.
  * Página 4 (La Cooperación y Superación): Colaboración, comprensión empática y acción positiva.
  * Página 5 (La Celebración y Madurez): Cierre satisfactorio, satisfacción por lo aprendido y bienestar.
  * Moraleja: Reflexión pedagógica enriquecedora para debate en asamblea escolar.
"""

        if st.button("Crear Libro Mágico", use_container_width=True):
            if not prob.strip() or not inte.strip():
                st.warning("Escribe primero el problema o situación y el interés del alumno.")
            else:
                with st.spinner("Pinter está escribiendo el cuento y coordinando la ilustración de sus láminas..."):
                    prompt_estricto = f"""
Escribe un cuento terapéutico y pedagógico para Educación Infantil ({edad} años).
Problema o situación a abordar: {prob}.
Interés o elemento motivador del peque: {inte}.

PAUTAS ESPECÍFICAS SEGÚN LA EDAD ({edad} AÑOS):
{guia_edad}

REGLAS DE COHERENCIA VISUAL TOTAL (EL TEXTO Y LA ILUSTRACIÓN DEBEN COINCIDIR EXACTAMENTE):
1. CONSISTENCIA DEL PROTAGONISTA:
   - Define el protagonista en inglés con rasgos simples, redondeados y tiernos (ej: "a sweet fluffy little orange fox with soft round ears and a tiny emerald green backpack").
   - Utiliza exactamente la MISMA descripción base del protagonista en TODOS los prompts de imagen.

2. COINCIDENCIA EXACTA CON OBJETOS Y PERSONAJES DEL TEXTO (CRUCIAL):
   - Cada 'imagen_prompt' DEBE ilustrar con total fidelidad lo que narra el 'texto' de esa página:
     * Si el texto menciona un OBJETO concreto (ej. un avión rojo, una pelota azul, bloques de madera, un libro de estrellas), el prompt DEBE situar ese objeto exacto en las PRIMERAS PALABRAS (ej: "...holding and playing with a bright red toy airplane...").
     * Si el texto menciona que está con OTRO PERSONAJE (ej. su mamá, su papá, un amigo conejito, la maestra), el prompt DEBE incluir explícitamente a ese acompañante junto al protagonista (ej: "...sitting lovingly beside its gentle mother fox...", "...sharing toys with a cute fluffy white bunny friend...").
     * Si el texto habla de una emoción (ej. llorando, sonriendo con orgullo, asombrado), el prompt DEBE indicar esa expresión facial exacta (ej: "...curious wide eyes...", "...joyful proud smiling face...").

3. ESTRUCTURA DIRECTA DE CADA 'imagen_prompt':
   - Comienza siempre por la acción e interacción clave: [Protagonista] + [Interacción directa con el objeto clave o personaje acompañante del texto] + [Entorno acogedor simple] + , {guia_estilo}
   - Mantén cada escena limpia, con un único foco de atención claro para que el generador no omita los objetos ni a los acompañantes.
   - PROHIBIDO usar palabras como "3d", "pixar", "cgi", "render", "photorealistic" o "symmetrical face".

Devuelve ÚNICAMENTE un objeto JSON válido con esta estructura exacta y en español (salvo los imagen_prompt que van en inglés):
{{
  "titulo": "El título del cuento",
  "portada_prompt": "Prompt in english for the cover with protagonist, clean simple background, {guia_estilo}",
  "paginas": [
    {{"subtitulo": "Subtítulo de la escena", "texto": "Texto narrativo adaptado a {edad} años...", "imagen_prompt": "Prompt in english showing EXACTLY the key objects and companions mentioned in this page text, {guia_estilo}"}}
  ],
  "moraleja": "La moraleja pedagógica para reflexionar en el aula."
}}
Solo devuelve el JSON crudo, sin comillas triples markdown ni texto adicional.
"""
                    try:
                        res = model.generate_content(prompt_estricto).text

                        res_clean = res.strip().removeprefix("```json").removesuffix("```").strip()
                        cuento_data = json.loads(res_clean)
                        
                        paginas_js = []
                        estado_progreso = st.empty()
                        barra_progreso = st.progress(0.05)
                        
                        pags_cuento = cuento_data["paginas"][:num_pags_historia]
                        total_laminas = 1 + len(pags_cuento) + 1
                        
                        # 1. Portada
                        estado_progreso.markdown(f"*Ilustrando portada del cuento... (Lámina 1/{total_laminas})*")
                        img_portada = obtener_ilustracion_data_uri(cuento_data["portada_prompt"], cuento_data["titulo"])
                        barra_progreso.progress(1.0 / total_laminas)
                        paginas_js.append({
                            "tipo": "portada",
                            "titulo": cuento_data["titulo"],
                            "etiqueta": "Portada",
                            "imagen": img_portada or "",
                            "audio": generar_audio_base64(cuento_data["titulo"])
                        })
                        
                        ultima_imagen_valida = img_portada if (img_portada and not img_portada.startswith("data:image/svg")) else None
                        
                        # 2. Páginas del cuento adaptadas a la edad
                        for idx_p, p in enumerate(pags_cuento):
                            num_pag = idx_p + 1
                            subtit = p.get("subtitulo", f"Página {num_pag}")
                            prog = (num_pag + 1) / total_laminas
                            
                            estado_progreso.markdown(f"*Ilustrando lámina {num_pag + 1}/{total_laminas}: {subtit}...*")
                            time.sleep(22)
                                
                            img_pag = obtener_ilustracion_data_uri(
                                p["imagen_prompt"], 
                                f"Página {num_pag}", 
                                imagen_respaldo=ultima_imagen_valida
                            )
                            if img_pag and not img_pag.startswith("data:image/svg"):
                                ultima_imagen_valida = img_pag
                                # Si la portada no tenía foto real, le asignamos esta foto del protagonista
                                if not paginas_js[0]["imagen"] or paginas_js[0]["imagen"].startswith("data:image/svg"):
                                    paginas_js[0]["imagen"] = img_pag
                                
                            barra_progreso.progress(min(prog, 0.94))
                            
                            paginas_js.append({
                                "tipo": "pagina",
                                "subtitulo": subtit,
                                "numero": num_pag,
                                "etiqueta": f"Página {num_pag}",
                                "texto": p["texto"],
                                "imagen": img_pag or ultima_imagen_valida or "",
                                "audio": generar_audio_base64(p["texto"])
                            })
                            
                        # Asegurar que la portada tenga foto real si alguna lámina la obtuvo
                        if (not paginas_js[0]["imagen"] or paginas_js[0]["imagen"].startswith("data:image/svg")) and ultima_imagen_valida:
                            paginas_js[0]["imagen"] = ultima_imagen_valida

                        # 3. Moraleja con lámina predeterminada fija
                        estado_progreso.markdown(f"*Componiendo lámina predeterminada de moraleja pedagógica... (Lámina {total_laminas}/{total_laminas})*")
                        img_mor = generar_lamina_moraleja()
                        barra_progreso.progress(1.0)
                        paginas_js.append({
                            "tipo": "moraleja",
                            "titulo": "Moraleja y Aprendizaje",
                            "etiqueta": "Reflexión Pedagógica",
                            "texto": cuento_data["moraleja"],
                            "imagen": img_mor,
                            "audio": generar_audio_base64("Moraleja y Aprendizaje. " + cuento_data["moraleja"])
                        })
                        
                        estado_progreso.empty()
                        barra_progreso.empty()
                        
                        st.session_state.cuento_js_data = paginas_js
                        st.session_state.cuento_in = f"{prob} | {inte}"
                        st.session_state.cuento_res = json.dumps(cuento_data, ensure_ascii=False)
                    except Exception as e:
                        st.error(f"Error generando el cuento: {e}. Vuelve a intentarlo.")

    with c2:
        if "cuento_js_data" in st.session_state:
            html_code = f"""
            <!DOCTYPE html>
            <html>
            <head>
              <meta charset="utf-8">
              <style>
                * {{
                    font-family: 'Times New Roman', Times, Baskerville, Georgia, serif !important;
                    box-sizing: border-box;
                }}
                body {{
                    font-family: 'Times New Roman', Times, Baskerville, Georgia, serif !important;
                    background-color: transparent;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    margin: 0;
                    padding: 4px;
                }}
                .book-container {{
                    background: #FFFEFA;
                    border-radius: 16px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                    width: 100%;
                    max-width: 680px;
                    padding: 16px 20px;
                    text-align: center;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: space-between;
                    border: 3px solid #F4D03F;
                    min-height: 520px;
                }}
                .etiqueta-pagina {{
                    font-size: 14px;
                    color: #795548;
                    font-style: italic;
                    margin-bottom: 5px;
                }}
                .imagen-container {{
                    height: 250px;
                    max-height: 250px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    margin-bottom: 10px;
                    width: 100%;
                    overflow: hidden;
                    border-radius: 12px;
                    background: #FAF9F6;
                }}
                .imagen-container img {{
                    width: 100%;
                    height: 250px;
                    max-height: 250px;
                    object-fit: contain;
                    border-radius: 12px;
                    box-shadow: 0 4px 10px rgba(0,0,0,0.08);
                    display: block;
                }}
                .texto-container {{
                    font-size: 18px;
                    color: #33261D;
                    min-height: 52px;
                    max-height: 100px;
                    overflow-y: auto;
                    margin-bottom: 10px;
                    line-height: 1.45;
                    padding: 0 10px;
                    text-align: center;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
                .titulo {{
                    font-size: 25px;
                    font-weight: bold;
                    color: #3E2F28;
                    margin-bottom: 6px;
                    border-bottom: 2px solid #F4D03F;
                    padding-bottom: 4px;
                }}
                .subtitulo {{
                    font-size: 19px;
                    font-weight: bold;
                    color: #5D4037;
                    margin-bottom: 5px;
                    font-style: italic;
                }}
                .controles {{
                    display: flex;
                    justify-content: space-between;
                    width: 100%;
                    margin-top: 8px;
                    gap: 10px;
                }}
                button {{
                    flex: 1;
                    background-color: #F4D03F;
                    border: none;
                    padding: 10px 14px;
                    font-size: 16px;
                    border-radius: 8px;
                    cursor: pointer;
                    color: #1E1611;
                    font-weight: bold;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.18);
                    transition: transform 0.1s, opacity 0.3s;
                }}
                button:active {{ transform: scale(0.96); }}
                button:disabled {{ background-color: #e0e0e0; cursor: not-allowed; opacity: 0.6; box-shadow: none; }}
                .play-btn {{ background-color: #4CAF50; color: white; }}
              </style>
            </head>
            <body>
                <div class="book-container">
                    <div id="book-content" style="width: 100%;"></div>
                    <audio id="audio-player"></audio>
                    <div class="controles">
                        <button id="btn-prev" onclick="cambiarPagina(-1)">Anterior</button>
                        <button id="btn-play" class="play-btn" onclick="togglePlay()">Reproducir</button>
                        <button id="btn-next" onclick="cambiarPagina(1)">Siguiente</button>
                    </div>
                </div>

                <script>
                    const paginas = {json.dumps(st.session_state.cuento_js_data)};
                    let indiceActual = 0;
                    let reproduciendo = false;
                    
                    const contentDiv = document.getElementById("book-content");
                    const audioPlayer = document.getElementById("audio-player");
                    const btnPrev = document.getElementById("btn-prev");
                    const btnNext = document.getElementById("btn-next");
                    const btnPlay = document.getElementById("btn-play");

                    function renderizarPagina() {{
                        const pag = paginas[indiceActual];
                        let html = "";
                        
                        let fotoSrc = pag.imagen;
                        if (!fotoSrc || fotoSrc.startsWith("data:image/svg")) {{
                            const fotoReal = paginas.find(p => p.imagen && !p.imagen.startsWith("data:image/svg"));
                            if (fotoReal) {{
                                fotoSrc = fotoReal.imagen;
                            }}
                        }}
                        
                        const imgHtml = `
                            <div class="imagen-container">
                                <img id="img-${{indiceActual}}" src="${{fotoSrc}}" alt="Ilustración">
                            </div>`;
                        
                        const etiqHtml = `<div class="etiqueta-pagina">${{pag.etiqueta || ''}} (${{indiceActual + 1}} de ${{paginas.length}})</div>`;
                        
                        if (pag.tipo === "portada") {{
                            html = `${{etiqHtml}}<div class="titulo">${{pag.titulo}}</div>${{imgHtml}}`;
                        }} else if (pag.tipo === "pagina") {{
                            const subHtml = pag.subtitulo ? `<div class="subtitulo">${{pag.subtitulo}}</div>` : '';
                            html = `${{etiqHtml}}${{subHtml}}${{imgHtml}}<div class="texto-container">${{pag.texto}}</div>`;
                        }} else if (pag.tipo === "moraleja") {{
                            html = `${{etiqHtml}}<div class="titulo">${{pag.titulo}}</div>${{imgHtml}}<div class="texto-container"><strong>${{pag.texto}}</strong></div>`;
                        }}
                        
                        contentDiv.innerHTML = html;
                        audioPlayer.src = pag.audio;
                        
                        btnPrev.disabled = indiceActual === 0;
                        btnNext.disabled = indiceActual === paginas.length - 1;
                        
                        if (reproduciendo) {{
                            audioPlayer.play();
                        }}
                    }}

                    function cambiarPagina(delta) {{
                        indiceActual += delta;
                        if (indiceActual < 0) indiceActual = 0;
                        if (indiceActual >= paginas.length) indiceActual = paginas.length - 1;
                        renderizarPagina();
                    }}

                    function togglePlay() {{
                        if (reproduciendo) {{
                            audioPlayer.pause();
                            reproduciendo = false;
                            btnPlay.innerText = "Reproducir";
                        }} else {{
                            audioPlayer.play();
                            reproduciendo = true;
                            btnPlay.innerText = "Pausar";
                        }}
                    }}

                    audioPlayer.onended = function() {{
                        if (indiceActual < paginas.length - 1) {{
                            cambiarPagina(1);
                        }} else {{
                            reproduciendo = false;
                            btnPlay.innerText = "Reproducir de nuevo";
                        }}
                    }};

                    renderizarPagina();
                </script>
            </body>
            </html>
            """
            components.html(html_code, height=800)
            
            if st.button("Guardar en Historial", use_container_width=True):
                # Guardamos el JSON como string en el drive
                if guardar_en_drive(usuario_actual, "Cuentos", st.session_state.cuento_in, st.session_state.cuento_res):
                    st.success("¡Libro guardado!")

elif modo == "Diseñador ABN & Retos":
    st.empty()
    crear_encabezado("Diseñador ABN & Retos", 3)
    c1, c2 = st.columns(2)
    with c1:
        if "precarga_abn_obj" in st.session_state:
            st.session_state.input_abn_obj = st.session_state.pop("precarga_abn_obj")
        if "precarga_abn_mat" in st.session_state:
            st.session_state.input_abn_mat = st.session_state.pop("precarga_abn_mat")
            
        if "input_abn_obj" not in st.session_state:
            st.session_state.input_abn_obj = ""
        if "input_abn_mat" not in st.session_state:
            st.session_state.input_abn_mat = ""
            
        obj = st.text_input("Objetivo:", key="input_abn_obj")
        mat = st.text_input("Materiales:", key="input_abn_mat")
        if st.button("Diseñar"):
            with st.spinner("Diseñando ficha de programación ABN..."):
                prompt_abn = f"""
Actúa como un maestro experto en el método matemático ABN para Educación Infantil.
A partir del Objetivo: '{obj}' y los Materiales disponibles: '{mat}', diseña una ficha de programación de aula lista para imprimir, estructurada estrictamente en los siguientes bloques en Markdown:

### 1. Ficha Técnica
* **Fase Matemática:** (Ej: conteo, descomposición, reparto, complementarios del 10, etc.)
* **Organización Espacial:** (Ej: gran grupo, rincones, parejas)
* **Tiempo Estimado:** (Ej: 15-20 minutos)

### 2. Desarrollo de la Actividad (3 Niveles DUA)
Explica cómo llevar a cabo la actividad adaptada a tres ritmos de aprendizaje:
* **Nivel Apoyo:** (Manipulación guiada paso a paso para alumnado que necesita más ayuda).
* **Nivel Estándar:** (Ejecución autónoma esperada para la mayoría del grupo).
* **Nivel Reto:** (Variante de mayor abstracción o dificultad para alumnado avanzado).

### 3. Rúbrica de Observación Rápida
Proporciona 3 indicadores clave y observables para evaluar en directo durante la actividad, categorizados en:
* **Conseguido:** (Descripción de lo que hace el alumno)
* **En proceso:** (Descripción de lo que hace el alumno)
* **No iniciado:** (Descripción de lo que hace el alumno)

Responde directamente con los bloques, sin saludos ni introducciones.
"""
                res = model.generate_content(prompt_abn.strip()).text
                st.session_state.abn_res, st.session_state.abn_in = res, f"{obj} | {mat}"
    with c2:
        if "abn_res" in st.session_state:
            st.write(st.session_state.abn_res)
            if st.button("Guardar"):
                if guardar_en_drive(usuario_actual, "ABN", st.session_state.abn_in, st.session_state.abn_res): st.success("¡Guardado!")

elif modo == "Chat Asistente General":
    st.empty()
    crear_encabezado("Asistente", 4)
    if "chat" not in st.session_state: st.session_state.chat = []
    for m in st.session_state.chat: st.chat_message(m["role"]).write(m["content"])
    if p := st.chat_input("Duda..."):
        st.session_state.chat.append({"role":"user","content":p}); st.chat_message("user").write(p)
        r = model.generate_content(f"Eres maestra experta. {p}").text
        st.session_state.chat.append({"role":"assistant","content":r}); st.chat_message("assistant").write(r)
        guardar_en_drive(usuario_actual, "Chat", p, r)

# --- HISTORIAL PERSONAL ---
elif modo == "Ver MI Historial":
    st.empty()
    usuario_formateado = st.session_state.usuario_actual if "usuario_actual" in st.session_state and st.session_state.usuario_actual else "Usuario"
    crear_encabezado(f"Biblioteca de {usuario_formateado}", 5)
    if st.button("Actualizar"): st.rerun()

    if st.session_state.pop("aviso_registro_eliminado", False):
        st.success("Registro eliminado de la biblioteca con éxito.")

    st.info("Aquí puedes revisar todas las actividades y cuentos que has generado y guardado previamente.")
    
    estado, datos = leer_todo_bruto()
    
    if estado != "OK":
        st.error("Ha ocurrido un error al conectar con el historial. Inténtalo más tarde.")
    else:
        encontrados = 0
        
        # BUCLE PARA FILTRAR Y MOSTRAR SOLO LOS DATOS DEL USUARIO ACTUAL
        for i, fila in enumerate(datos):
            # Saltamos la primera fila si es título
            if i == 0: continue
            
            # Verificamos que la fila tenga suficientes datos
            if len(fila) >= 5:
                # Fila[0] = Fecha, Fila[1] = Usuario, Fila[2] = Herramienta, Fila[3] = Entrada, Fila[4] = Salida
                nombre_en_excel = fila[1] 
                
                # Comprobamos si el nombre coincide (ignorando mayúsculas/minúsculas)
                if usuario_actual.lower() in str(nombre_en_excel).lower():
                    encontrados += 1
                    with st.expander(f"Fecha: {fila[0]} | Herramienta: {fila[2]}"):
                        st.markdown(f"**Lo que pediste:** {fila[3]}")
                        st.markdown("---")
                        st.markdown(f"**Resultado:**\n\n{fila[4]}")
                        st.write("")
                        col_esp, col_del = st.columns([0.7, 0.3])
                        with col_del:
                            if st.button("Eliminar Registro", key=f"btn_del_hist_{i}", use_container_width=True):
                                st.session_state[f"confirmar_borrado_{i}"] = True
                        
                        if st.session_state.get(f"confirmar_borrado_{i}", False):
                            st.warning("¿Deseas eliminar este registro de tu biblioteca de forma permanente?")
                            c_si, c_no = st.columns(2)
                            with c_si:
                                if st.button("Confirmar eliminación", key=f"btn_si_del_{i}", type="primary", use_container_width=True):
                                    with st.spinner("Eliminando registro..."):
                                        exito = borrar_registro_historial(i, fecha=fila[0], usuario=nombre_en_excel, herramienta=fila[2])
                                    if exito:
                                        st.session_state.pop(f"confirmar_borrado_{i}", None)
                                        st.session_state.aviso_registro_eliminado = True
                                        st.rerun()
                                    else:
                                        st.error("No se pudo eliminar el registro. Inténtalo más tarde.")
                            with c_no:
                                if st.button("Cancelar", key=f"btn_no_del_{i}", use_container_width=True):
                                    st.session_state.pop(f"confirmar_borrado_{i}", None)
                                    st.rerun()
        
        if encontrados == 0:
            st.warning(f"Aún no hay ningún registro guardado para el nombre '{usuario_actual}'. ¡Anímate a generar y guardar algo con las herramientas!")
