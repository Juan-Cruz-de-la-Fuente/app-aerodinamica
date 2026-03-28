import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import re
import io
from datetime import datetime
import pyvista as pv
import tempfile
import os
import base64
from scipy.spatial import Delaunay
from typing import Dict
import os
import zipfile
import random
import pyvista as pv
from scipy.interpolate import griddata
import auth  # Import the new authentication module
import json
import imageio
from PIL import Image


def rotate_points(x, y, z, angle_x, angle_y, angle_z):
    """Rotates 3D points around X, Y, Z axes (angles in degrees)."""
    # Convert to radians
    rad_x = np.radians(angle_x)
    rad_y = np.radians(angle_y)
    rad_z = np.radians(angle_z)
    
    # Rotation Matrices
    rx = np.array([
        [1, 0, 0],
        [0, np.cos(rad_x), -np.sin(rad_x)],
        [0, np.sin(rad_x), np.cos(rad_x)]
    ])
    
    ry = np.array([
        [np.cos(rad_y), 0, np.sin(rad_y)],
        [0, 1, 0],
        [-np.sin(rad_y), 0, np.cos(rad_y)]
    ])
    
    rz = np.array([
        [np.cos(rad_z), -np.sin(rad_z), 0],
        [np.sin(rad_z), np.cos(rad_z), 0],
        [0, 0, 1]
    ])
    
    # Combined rotation: R = Rz * Ry * Rx
    R = rz @ (ry @ rx)
    
    # Arrange points as (3, N)
    points = np.vstack([x, y, z])
    
    # Rotate
    rotated_points = R @ points
    
    return rotated_points[0,:], rotated_points[1,:], rotated_points[2,:]

# Configuración de la página
st.set_page_config(
    page_title="Laboratorio de Aerodinámica y Fluidos - UTN HAEDO",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- INITIALIZATION ---
if 'seccion_actual' not in st.session_state:
    st.session_state.seccion_actual = 'inicio'
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None

# --- SHADCN-INSPIRED CLEAN THEME & HORIZONTAL NAV ---
st.markdown("""
<style>
    /* IMPORTS */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;600&display=swap');

    /* GLOBAL RESET */
    html {
        scroll-behavior: smooth !important;
    }
    
    .stApp {
        background-color: #000000;
        font-family: 'Inter', sans-serif;
        color: #ffffff;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Orbitron', sans-serif;
        font-weight: 700;
        text-transform: uppercase;
        color: #ffffff;
        letter-spacing: 2px;
    }

    /* HIDE STREAMLIT ELEMENT S */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* REMOVE SIDEBAR MARGIN IF PRESENT (Though we aren't using st.sidebar anymore) */
    
    /* CUSTOM BUTTONS (SpaceX Style) */
    .stButton > button {
        background-color: transparent !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.6) !important;
        border-radius: 0px !important; /* Sharp edges */
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.3s ease;
        padding: 0.5rem 1rem;
        font-family: 'Orbitron', sans-serif;
        width: 100%;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }

    .stButton > button:hover {
        background-color: #ffffff !important;
        color: #000000 !important;
        border-color: #ffffff !important;
        box-shadow: 0 0 15px rgba(255, 255, 255, 0.5);
    }
    
    /* NAV BUTTON SPECIFIC (Optional, if we want to differentiate) */
    div[data-testid="column"] .stButton > button {
        font-size: 0.9rem;
    }

    /* INPUT FIELDS */
    .stTextInput > div > div > input, .stNumberInput > div > div > input, .stSelectbox > div > div > div {
        background-color: #111111 !important;
        color: white !important;
        border: 1px solid #333 !important;
        border-radius: 0px !important;
    }
    
    /* CARDS & CONTAINERS */
    div.section-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 2rem;
        transition: transform 0.3s ease;
        margin-bottom: 2rem; /* Spacing for rows */
    }
    
    div.section-card:hover {
        border-color: #ffffff;
        transform: translateY(-5px);
    }

    /* SCROLLBAR */
    ::-webkit-scrollbar {
        width: 8px;
        background: #000;
    }
    ::-webkit-scrollbar-thumb {
        background: #333;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #fff;
    }
    
    /* TABS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: #000;
        border-radius: 0px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: #888;
        border-radius: 0;
        text-transform: uppercase;
        font-family: 'Orbitron', sans-serif;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #fff;
        border-bottom: 2px solid #fff;
    }
    
    /* TEXT MANUAL STYLE */
    .manual-text {
        font-family: 'Inter', sans-serif;
        line-height: 1.6;
        color: #e0e0e0;
        font-size: 1rem;
        text-align: justify;
    }
    .manual-header {
        font-family: 'Orbitron', sans-serif;
        color: #4ade80; /* Green accent for manual headers */
        margin-top: 1.5rem;
    }

</style>
""", unsafe_allow_html=True)



def rotate_points(x, y, z, angle_x, angle_y, angle_z):
    """
    Rota puntos 3D alrededor de los ejes X, Y, Z.
    Ángulos en grados.
    """
    # Convertir a radianes
    rad_x = np.radians(angle_x)
    rad_y = np.radians(angle_y)
    rad_z = np.radians(angle_z)
    
    # Matrices de rotación
    Rx = np.array([
        [1, 0, 0],
        [0, np.cos(rad_x), -np.sin(rad_x)],
        [0, np.sin(rad_x), np.cos(rad_x)]
    ])
    
    Ry = np.array([
        [np.cos(rad_y), 0, np.sin(rad_y)],
        [0, 1, 0],
        [-np.sin(rad_y), 0, np.cos(rad_y)]
    ])
    
    Rz = np.array([
        [np.cos(rad_z), -np.sin(rad_z), 0],
        [np.sin(rad_z), np.cos(rad_z), 0],
        [0, 0, 1]
    ])
    
    # Matriz de rotación combinada R = Rz * Ry * Rx
    R = Rz @ Ry @ Rx
    
    # Apilar puntos
    points = np.vstack([x, y, z])
    
    # Rotar
    rotated_points = R @ points
    
    return rotated_points[0], rotated_points[1], rotated_points[2]


def render_navbar():
    # --- HORIZONTAL NAVIGATION BAR ---
    if st.session_state.get('logged_in'):
        with st.container():
            # Layout principal
            c_sl, c1, c2, c3, c4, c5, c6, c_sr = st.columns([0.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 0.5])
            
            with c1:
                t1 = "primary" if st.session_state.seccion_actual == 'inicio' else "secondary"
                if st.button("🚀 INICIO", use_container_width=True, type=t1):
                    st.session_state.seccion_actual = 'inicio'
                    st.rerun()
            
            with c2:
                # Dropdown for Ensayo Estela
                is_estela = st.session_state.seccion_actual in ['betz_2d', 'vis_2d_nueva', 'betz_3d', 'betz_4d']
                if is_estela:
                    st.markdown("""<style>
                    div[data-testid='stPopover'] {
                        height: 100% !important;
                        margin: 0 !important;
                        display: flex !important;
                    }
                    div[data-testid='stPopover'] > div {
                        height: 100% !important;
                        width: 100% !important;
                    }
                    div[data-testid='stPopover'] > div > button, div[data-testid='stPopover'] > button {
                        background-color: transparent !important;
                        color: var(--primary-color) !important;
                        border: 1px solid var(--primary-color) !important;
                        border-radius: 0px !important;
                        text-transform: uppercase !important;
                        letter-spacing: 1px !important;
                        transition: all 0.3s ease !important;
                        padding: 0.5rem 1rem !important;
                        font-family: 'Orbitron', sans-serif !important;
                        width: 100% !important;
                        height: 100% !important;
                        display: flex !important;
                        justify-content: center !important;
                        align-items: center !important;
                    }
                    div[data-testid='stPopover'] > div > button:hover, div[data-testid='stPopover'] > button:hover {
                        background-color: #ffffff !important;
                        color: #000000 !important;
                        border-color: #ffffff !important;
                        box-shadow: 0 0 15px rgba(255, 255, 255, 0.5) !important;
                    }
                    </style>""", unsafe_allow_html=True)
                else:
                    st.markdown("""<style>
                    div[data-testid='stPopover'] {
                        height: 100% !important;
                        margin: 0 !important;
                        display: flex !important;
                    }
                    div[data-testid='stPopover'] > div {
                        height: 100% !important;
                        width: 100% !important;
                    }
                    div[data-testid='stPopover'] > div > button, div[data-testid='stPopover'] > button {
                        background-color: transparent !important;
                        color: #ffffff !important;
                        border: 1px solid rgba(255, 255, 255, 0.6) !important;
                        border-radius: 0px !important;
                        text-transform: uppercase !important;
                        letter-spacing: 1px !important;
                        transition: all 0.3s ease !important;
                        padding: 0.5rem 1rem !important;
                        font-family: 'Orbitron', sans-serif !important;
                        width: 100% !important;
                        height: 100% !important;
                        display: flex !important;
                        justify-content: center !important;
                        align-items: center !important;
                    }
                    div[data-testid='stPopover'] > div > button:hover, div[data-testid='stPopover'] > button:hover {
                        background-color: #ffffff !important;
                        color: #000000 !important;
                        border-color: #ffffff !important;
                        box-shadow: 0 0 15px rgba(255, 255, 255, 0.5) !important;
                    }
                    </style>""", unsafe_allow_html=True)
                
                with st.popover("🌌 ENSAYO ESTELA", use_container_width=True):
                    st.markdown("<style>div[data-testid='stPopoverBody'] button { font-size: 0.85rem !important; padding: 0.2rem 0.5rem !important; }</style>", unsafe_allow_html=True)
                    if st.button("📈 Vis. Estela 1D", use_container_width=True, type="primary" if st.session_state.seccion_actual == 'betz_2d' else "secondary"):
                        st.session_state.seccion_actual = 'betz_2d'
                        st.rerun()
                    if st.button("📈 Vis. Estela 2D", use_container_width=True, type="primary" if st.session_state.seccion_actual == 'vis_2d_nueva' else "secondary"):
                        st.session_state.seccion_actual = 'vis_2d_nueva'
                        st.rerun()
                    if st.button("🌪️ Vis. Estela 3D", use_container_width=True, type="primary" if st.session_state.seccion_actual == 'betz_3d' else "secondary"):
                        st.session_state.seccion_actual = 'betz_3d'
                        st.rerun()
                    if st.button("🌌 Vis. Estela 4D", use_container_width=True, type="primary" if st.session_state.seccion_actual == 'betz_4d' else "secondary"):
                        st.session_state.seccion_actual = 'betz_4d'
                        st.rerun()
                    if st.button("🔧 Herramientas", use_container_width=True, type="primary" if st.session_state.seccion_actual == 'herramientas' else "secondary"):
                        st.session_state.seccion_actual = 'herramientas'
                        st.rerun()

            with c3:
                t3 = "primary" if st.session_state.seccion_actual == 'ensayo_betz' else "secondary"
                if st.button("🧪 ENSAYO DE BETZ", use_container_width=True, type=t3):
                     st.session_state.seccion_actual = 'ensayo_betz'
                     st.rerun()

            with c4:
                t4 = "primary" if st.session_state.seccion_actual == 'modelos' else "secondary"
                if st.button("📦 MODELOS", use_container_width=True, type=t4):
                     st.session_state.seccion_actual = 'modelos'
                     st.rerun()

            with c5:
                t5 = "primary" if st.session_state.seccion_actual == 'configuracion' else "secondary"
                if st.button("⚙️ CONFIG", use_container_width=True, type=t5):
                    st.session_state.seccion_actual = 'configuracion'
                    st.rerun()

            with c6:
                if st.button(f"👤 PERFIL / SALIR", use_container_width=True):
                    st.session_state.logged_in = False
                    st.session_state.username = None
                    st.rerun()

            st.markdown("<hr style='border-top: 1px solid #333; margin-top: 10px;'>", unsafe_allow_html=True)

# Render Nav ONLY if NOT on Inicio page (on Inicio it comes after Hero)
if st.session_state.get('logged_in') and st.session_state.seccion_actual != 'inicio':
    render_navbar()


# --- AUTHENTICATION CHECK ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None

def login_page():
    # Login Hero Image
    st.markdown("""
    <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; min-height: 80vh;">
        <div style="width: 100%; max-width: 450px; margin-bottom: 20px;">
            <img src="https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop" 
                 style="width: 100%; border-radius: 0px; border: 1px solid #333; opacity: 0.9;">
        </div>
        <div class="stCard" style="width: 100%; max-width: 450px; padding: 2.5rem; border: 1px solid var(--border); background-color: var(--card);">
            <div style="display: flex; justify-content: center; margin-bottom: 1.5rem;">
               <h1 style="font-size: 2rem; margin: 0; color: #fafafa;">BETZ APP</h1>
            </div>
            <p style="text-align: center; color: var(--muted-foreground); margin-bottom: 2rem;">Sistema de Procesamiento de Datos de Túnel de Viento</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.markdown("### 🔐 Iniciar Sesión")
        username = st.text_input("Usuario", placeholder="admin", key="login_user")
        password = st.text_input("Contraseña", type="password", placeholder="••••", key="login_pass")
        
        st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)
        
        if st.button("Iniciar Sesión", type="primary", use_container_width=True):
             # VALIDACIÓN 100% DESDE LA BASE DE DATOS DRIVE
            if auth.verify_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                # Inicializar estructura de carpetas en Drive para este usuario
                try:
                    import drive_api as _dapi
                    _dapi.init_user_folders(username)
                except Exception as _e:
                    pass  # No bloquear el login si Drive falla
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
        
        st.info("💡 Contacte al administrador para obtener credenciales de acceso.")

if not st.session_state.logged_in:
    login_page()
    st.stop()  # Stop execution here if not logged in

# Inicializar estado de la sesión (resto de inicializaciones)
if 'seccion_actual' not in st.session_state:
    st.session_state.seccion_actual = 'inicio'
if 'archivos_cargados' not in st.session_state:
    st.session_state.archivos_cargados = []
if 'datos_procesados' not in st.session_state:
    st.session_state.datos_procesados = {}
if 'configuracion_inicial' not in st.session_state:
    st.session_state.configuracion_inicial = {}
if 'sub_archivos_generados' not in st.session_state:
    st.session_state.sub_archivos_generados = {}
if 'datos_3d_filtrados' not in st.session_state:
    st.session_state.datos_3d_filtrados = {}
if 'sub_archivos_3d' not in st.session_state:
    st.session_state.sub_archivos_3d = {}
if 'configuracion_3d' not in st.session_state:
    st.session_state.configuracion_3d = {}
if 'sub_archivos_3d_generados' not in st.session_state:
    st.session_state.sub_archivos_3d_generados = {}
if 'diferencias_guardadas' not in st.session_state:
    st.session_state.diferencias_guardadas = {}



def extraer_tiempo_y_coordenadas_YZ(nombre_archivo):
    """
    Extraer tiempo y coordenadas para el sistema estandarizado Y-Z.
    
    Mapeo:
    - Archivo 'X' -> Traverser -> App 'Pos_Y_Traverser'
    - Archivo 'Y' -> Altura Base -> App 'Pos_Z_Base' (Si existe, sino 0)
    - Tiempo -> App 'Tiempo_s'
    """
    tiempo = None
    y_traverser = None 
    z_base = None

    # Normalizar nombre sin extensión
    nombre = os.path.basename(str(nombre_archivo))
    nombre_sin_ext = re.sub(r'\.\w+$', '', nombre)

    # 1) Intentar extraer tiempo
    partes = nombre_sin_ext.split('_')
    if partes and partes[-1].isdigit():
        try:
            tiempo = int(partes[-1])
        except:
            tiempo = None

    if tiempo is None:
        tiempo_match = re.search(r"[Tt](\d+)\s*[sS]?$", nombre_sin_ext)
        if tiempo_match:
            tiempo = int(tiempo_match.group(1))

    # 2) Extraer X del archivo (que es nuestra Pos_Y_Traverser)
    x_match = re.search(r"[Xx][_\-=]?(-?\d+)", nombre_sin_ext)
    if x_match:
        try:
            y_traverser = int(x_match.group(1))
        except:
            pass
    
    # Fallback X
    if y_traverser is None:
        m = re.search(r"[Xx]\s*(\d+)", nombre_sin_ext)
        if m:
            y_traverser = int(m.group(1))

    # 3) Extraer Y del archivo (que es nuestra Pos_Z_Base)
    y_match = re.search(r"[Yy][_\-=]?(-?\d+)", nombre_sin_ext)
    if y_match:
        try:
            z_base = int(y_match.group(1))
        except:
            pass
            
    # Fallback Y
    if z_base is None:
        m = re.search(r"[Yy]\s*(\d+)", nombre_sin_ext)
        if m:
            z_base = int(m.group(1))

    return tiempo, y_traverser, z_base

def normalizar_nombre_sensor(sensor_text):
    """Normaliza una entrada de cabecera de sensor a 'Presion-Sensor N' (N entero global).
       Acepta formatos como:
         - 'Presion-Sensor_0_1' -> 'Presion-Sensor 1'
         - 'Presion-Sensor_1_12' -> 'Presion-Sensor 24'
         - 'Presion-Sensor 5' -> 'Presion-Sensor 5'
       Devuelve None si no puede normalizar.
    """
    if pd.isna(sensor_text):
        return None
    s = str(sensor_text).strip()
    if not s:
        return None

    # Caso 'Presion-Sensor_offset_index' (ej 'Presion-Sensor_1_3')
    m = re.search(r'(?i)presion[-_ ]*sensor[_\-]?(\d+)[_\-](\d+)', s)
    if m:
        offset = int(m.group(1))
        idx = int(m.group(2))
        sensor_global = offset * 12 + idx
        return f"Presion-Sensor {sensor_global}"

    # Caso 'Presion-Sensor 12' o 'Presion-Sensor_12'
    m2 = re.search(r'(?i)presion[-_ ]*sensor[_\-\s]*(\d+)', s)
    if m2:
        sensor_global = int(m2.group(1))
        return f"Presion-Sensor {sensor_global}"

    # Caso donde venga solo un número al final
    nums = re.findall(r'(\d+)', s)
    if nums:
        # si hay dos números, considerar que puede ser offset,index
        if len(nums) >= 2:
            offset = int(nums[-2])
            idx = int(nums[-1])
            if 0 <= offset <= 9 and 1 <= idx <= 12:
                sensor_global = offset * 12 + idx
                return f"Presion-Sensor {sensor_global}"
        # si hay uno solo, usarlo como número de sensor
        sensor_global = int(nums[-1])
        return f"Presion-Sensor {sensor_global}"

    # Si no se reconoce, devolver la cadena original (por si acaso)
    return s


def obtener_numero_sensor_desde_columna(col_name):
    """Devuelve el número entero del sensor si el nombre de columna tiene 'Presion-Sensor N' (o similar), sino None."""
    if pd.isna(col_name):
        return None
    s = str(col_name)
    m = re.search(r'(?i)presion[-_ ]*sensor[_\-\s]*(\d+)', s)
    if m:
        return int(m.group(1))
    # si no coincide, intentar extraer último número
    nums = re.findall(r'(\d+)', s)
    if nums:
        return int(nums[-1])
    return None


def calcular_altura_absoluta_z(sensor_num, z_base_ref, posicion_inicial, distancia_entre_tomas, n_sensores, orden="asc"):
    """
    Calcula la altura absoluta Z de un sensor dado, basándose en una altura de referencia (Z Base).
    """
    if sensor_num is None:
        return None
    
    toma_index = int(sensor_num)  # ahora global: 1..21

    # Nota: la lógica original sumaba (toma_index - 1) * distancia a la referencia.
    # Asumimos que z_base_ref es la altura del primer sensor (o del 12, segun contexto, pero aqui parece ser base).
    # Sin embargo, el parametro 'posicion_inicial' se llama 'distancia_toma_12' en config.
    # Si z_base_ref es la lectura del 'y_traverser' (que era Z), entonces:
    
    if orden == "asc":
        z_total = z_base_ref + (toma_index - 1) * distancia_entre_tomas
    else:
        z_total = z_base_ref + (n_sensores - toma_index) * distancia_entre_tomas

    return z_total

def extraer_nombre_base_archivo(nombre_archivo):
    """Extraer nombre base del archivo (sin extensión y sin 'incertidumbre_')"""
    nombre_base = nombre_archivo.replace('.csv', '').replace('incertidumbre_', '').replace('_', ' ')
    # Capitalizar primera letra de cada palabra
    return ' '.join(word.capitalize() for word in nombre_base.split())

def procesar_promedios(archivo_csv, orden="asc"):
    """Procesar archivo de incertidumbre y detectar automáticamente la cantidad de sensores."""
    try:
        df_raw = pd.read_csv(archivo_csv, sep=";", header=None, dtype=str)  # leer como texto para robustez

        # Buscar la palabra "importante" para determinar dónde terminar
        index_final = df_raw[df_raw.apply(lambda row: row.astype(str).str.contains("importante", case=False).any(), axis=1)].index
        if not index_final.empty:
            df_raw = df_raw.iloc[:index_final[0]]

        resultados = []

        # Procesar bloques de 10 filas (misma lógica base)
        for i in range(0, df_raw.shape[0], 10):
            bloque = df_raw.iloc[i:i+10]
            if bloque.empty or len(bloque) < 3:
                continue

            archivo = bloque.iloc[0, 0]
            raw_sensores = bloque.iloc[0, 1:].tolist()
            muestras = bloque.iloc[1, 1] if 1 < bloque.shape[1] else None

            # Normalizar: si la cabecera vino entera en una sola celda separada por ';'
            sensores_lista = []
            for entry in raw_sensores:
                if pd.isna(entry):
                    continue
                s = str(entry).strip()
                if ';' in s:
                    partes = [p.strip() for p in s.split(';') if p.strip()]
                    sensores_lista.extend(partes)
                else:
                    sensores_lista.append(s)

            # Lo mismo para valores: si hay una celda con ;, expandir
            valores_lista = []
            for entry in bloque.iloc[2, 1:].tolist(): # Asumimos que los valores están en la fila 2 (índice 2)
                if pd.isna(entry):
                    continue
                s = str(entry).strip()
                if ';' in s:
                    partes = [p.strip() for p in s.split(';')]
                    valores_lista.extend(partes)
                else:
                    valores_lista.append(s)

            # Si por alguna razón no se alinean en longitud, ajustar
            n = max(len(sensores_lista), len(valores_lista))
            sensores_lista = (sensores_lista + [None] * n)[:n]
            valores_lista = (valores_lista + [None] * n)[:n]

            fila = {
                "Archivo": archivo,
                "Numero de muestras": muestras,
            }

            # Mapear cada sensor raw -> nombre normalizado y poner su valor
            for sensor_raw, valor_raw in zip(sensores_lista, valores_lista):
                nombre_sensor_norm = normalizar_nombre_sensor(sensor_raw)
                if nombre_sensor_norm is None:
                    continue
                # limpiar y convertir valor (coma -> punto)
                valor = valor_raw
                if isinstance(valor, str):
                    valor = valor.replace(',', '.').strip()
                try:
                    valor_num = float(valor) if (valor is not None and str(valor) != '') else np.nan
                except:
                    valor_num = np.nan

                fila[nombre_sensor_norm] = valor_num

            resultados.append(fila)

        df_resultado = pd.DataFrame(resultados)

        # Extraer tiempo y coordenadas desde nombre de archivo (columna "Archivo")
        if "Archivo" in df_resultado.columns:
            coordenadas_tiempo = df_resultado["Archivo"].apply(extraer_tiempo_y_coordenadas_YZ)
            df_resultado["Tiempo_s"] = [coord[0] for coord in coordenadas_tiempo]
            df_resultado["Pos_Y_Traverser"] = [coord[1] for coord in coordenadas_tiempo]
            df_resultado["Pos_Z_Base"] = [coord[2] for coord in coordenadas_tiempo]
        else:
            df_resultado["Tiempo_s"] = None
            df_resultado["Pos_Y_Traverser"] = None
            df_resultado["Pos_Z_Base"] = None

        # 🔎 Detectar cantidad de sensores automáticamente
        sensores_cols = [c for c in df_resultado.columns if re.search(r'Presion[-_ ]*Sensor', str(c), re.IGNORECASE)]
        if sensores_cols:
            n_sensores = max([obtener_numero_sensor_desde_columna(c) for c in sensores_cols if obtener_numero_sensor_desde_columna(c) is not None], default=0)
        else:
            n_sensores = 0

        # Guardar en atributos del DataFrame para usar después
        df_resultado.attrs["n_sensores"] = n_sensores

        return df_resultado

    except Exception as e:
        st.error(f"Error al procesar archivo: {str(e)}")
        return None



def crear_archivos_individuales_por_tiempo_y_posicion(df_resultado, nombre_archivo_fuente):
    """
    Crea sub-archivos usando las coordenadas estandarizadas.
    """
    sub_archivos = {}
    nombre_base = extraer_nombre_base_archivo(nombre_archivo_fuente)
    nombre_original = os.path.splitext(os.path.basename(nombre_archivo_fuente))[0]

    # Iterar sobre Pos_Y_Traverser (antes X_coord)
    y_vals = df_resultado["Pos_Y_Traverser"].dropna().unique()
    for y_valor in sorted(y_vals):
        df_y = df_resultado[df_resultado["Pos_Y_Traverser"] == y_valor]

        # Iterar sobre Tiempo_s (antes Tiempo (s))
        t_vals = df_y["Tiempo_s"].dropna().unique()
        for tiempo in sorted(t_vals):
            df_yt = df_y[df_y["Tiempo_s"] == tiempo]

            clave_sub_archivo = f"{nombre_original}_Y{y_valor}_T{tiempo}s"
            
            # Contar posiciones Z únicas
            num_z = len(df_yt['Pos_Z_Base'].unique()) if 'Pos_Z_Base' in df_yt.columns else 1

            sub_archivos[clave_sub_archivo] = {
                'archivo_fuente': nombre_base,
                'archivo_origen': nombre_original,
                'tiempo': tiempo,
                'pos_y_traverser': y_valor,
                'datos': df_yt,
                'nombre_archivo': f"{nombre_original}_Y{y_valor}_T{tiempo}s.csv",
                'num_posiciones_z': num_z
            }

    return sub_archivos

def calcular_posiciones_sensores(distancia_toma_12, distancia_entre_tomas, n_sensores, orden="asc"):
    """
    Calcula las posiciones físicas de todos los sensores en función de:
    - distancia_toma_12: posición de la toma física número 12 (en mm)
    - distancia_entre_tomas: separación entre sensores consecutivos (en mm)
    - n_sensores: cantidad total de sensores detectados en el archivo
    - orden: "asc" o "des" (según cómo están montados los sensores)
    Devuelve un diccionario con la posición y número físico de cada sensor.
    """
    posiciones = {}
    for sensor_num in range(1, n_sensores + 1):
        if orden == "asc":
            y_position = (sensor_num - 1) * distancia_entre_tomas
        else:
            y_position = (n_sensores - sensor_num) * distancia_entre_tomas


        posiciones[f"Presion-Sensor {sensor_num}"] = {
            'x': 0,
            'y': y_position,
            'sensor_fisico': sensor_num
        }
    return posiciones


def crear_grafico_betz_concatenado(sub_archivos_seleccionados, posiciones_sensores, configuracion):
    fig = go.Figure()

    posicion_inicial = configuracion['distancia_toma_12']
    distancia_entre_tomas = configuracion['distancia_entre_tomas']
    orden = configuracion.get('orden', 'asc')
    colores_por_tiempo = {10: '#08596C', 20: '#E74C3C', 30: '#F39C12', 40: '#27AE60', 50: '#8E44AD', 60: '#3498DB'}

    datos_agrupados = {}
    for clave, sub_archivo in sub_archivos_seleccionados.items():
        grupo = (sub_archivo['archivo_fuente'], sub_archivo['tiempo'])
        datos_agrupados.setdefault(grupo, []).append(sub_archivo)

    for grupo, sub_archivos_del_grupo in datos_agrupados.items():
        archivo_fuente, tiempo = grupo
        color = colores_por_tiempo.get(tiempo, '#333333')

        z_grupo, presion_grupo = [], []

        for sub_archivo in sub_archivos_del_grupo:
            datos_tiempo = sub_archivo['datos']
            sensor_cols = [c for c in datos_tiempo.columns if re.search(r'(?i)presion[-_ ]*sensor', str(c))]

            for _, fila in datos_tiempo.iterrows():
                y_traverser = fila.get('Pos_Y_Traverser', 0) if pd.notna(fila.get('Pos_Y_Traverser', np.nan)) else 0
                z_base_ref = fila.get('Pos_Z_Base', 0) if pd.notna(fila.get('Pos_Z_Base', np.nan)) else 0

                for col in sensor_cols:
                    sensor_num = obtener_numero_sensor_desde_columna(col)
                    if sensor_num is None:
                        continue
                    # Usamos z_base_ref como referencia
                    z_total = calcular_altura_absoluta_z(sensor_num, z_base_ref, posicion_inicial, distancia_entre_tomas, configuracion.get('n_sensores', len(sensor_cols)), orden)
                    presion = fila.get(col, None)
                    if pd.isna(presion):
                        continue
                    try:
                        presion = float(str(presion).replace(',', '.'))
                        presion_grupo.append(presion)
                        z_grupo.append(z_total)
                    except ValueError:
                        continue


def extraer_datos_para_grafico(sub_archivo, configuracion):
    """Extraer datos de presión y altura de un sub-archivo para gráficos (múltiples posiciones).
       Ahora soporta sensores numerados dinámicamente.
    """
    datos_tiempo = sub_archivo['datos']
    distancia_entre_tomas = configuracion['distancia_entre_tomas']
    posicion_inicial = configuracion.get('distancia_toma_12', 0)
    orden = configuracion.get('orden', 'asc')

    z_datos, presion_datos = [], []

    sensor_cols = [c for c in datos_tiempo.columns if re.search(r'(?i)presion[-_ ]*sensor', str(c))]
    n_sensores = max([obtener_numero_sensor_desde_columna(c) for c in sensor_cols], default=0)

    for _, fila in datos_tiempo.iterrows():
        # Antes X_coord era Y. Ahora Pos_Y_Traverser es Y explícito.
        y_traverser = fila.get('Pos_Y_Traverser', 0)
        z_base_ref = fila.get('Pos_Z_Base', 0)

        for col in sensor_cols:
            sensor_num = obtener_numero_sensor_desde_columna(col)
            if sensor_num is None:
                continue
            z_total = calcular_altura_absoluta_z(sensor_num, z_base_ref, posicion_inicial, distancia_entre_tomas, n_sensores, orden)
            presion = fila.get(col, None)
            if pd.isna(presion):
                continue
            try:
                presion_val = float(str(presion).replace(',', '.'))
                z_datos.append(z_total)
                presion_datos.append(presion_val)
            except (ValueError, TypeError):
                continue

    # Ordenar y devolver
    if z_datos and presion_datos:
        # Ordenar por altura (z_datos)
        datos_ordenados = sorted(zip(z_datos, presion_datos))
        z_ordenado, presion_ordenada = zip(*datos_ordenados)
        return list(z_ordenado), list(presion_ordenada)

    # 🔑 SIEMPRE devolver dos listas
    return [], []


def calcular_area_bajo_curva(z_datos, presion_datos):
    """Calcular área bajo la curva usando regla del trapecio"""
    if len(z_datos) < 2 or len(presion_datos) < 2:
        return 0
    
    area = 0
    for i in range(len(z_datos) - 1):
        # Regla del trapecio
        h = z_datos[i + 1] - z_datos[i]
        area += h * (presion_datos[i] + presion_datos[i + 1]) / 2
    
    return abs(area)

def crear_superficie_diferencia_delaunay_3d(datos_a, datos_b, nombre_a, nombre_b, configuracion_3d, mostrar_puntos=True):
    """
    Crea una superficie 3D de diferencias con Delaunay y mejoras visuales.
    """
    try:
        posicion_inicial = configuracion_3d['distancia_toma_12']
        distancia_entre_tomas = configuracion_3d['distancia_entre_tomas']
        orden = configuracion_3d['orden']

        def extraer_puntos(datos):
            puntos = {}
            sensor_cols = [c for c in datos.columns if re.search(r'(?i)presion[-_ ]*sensor', str(c))]
            for _, fila in datos.iterrows():
                y_traverser = fila.get('Pos_Y_Traverser', None) 
                z_base_ref = fila.get('Pos_Z_Base', None)
                if pd.isna(y_traverser) or pd.isna(z_base_ref):
                    continue

                for col in sensor_cols:
                    sensor_num = obtener_numero_sensor_desde_columna(col)
                    if sensor_num is None:
                        continue
                    altura_sensor_real = calcular_altura_absoluta_z(
                        sensor_num, z_base_ref, posicion_inicial, distancia_entre_tomas, orden
                    )
                    presion = fila.get(col, None)
                    if pd.isna(presion) or presion is None:
                        continue
                    try:
                        if isinstance(presion, str):
                            presion = float(presion.replace(',', '.'))
                        puntos[(y_traverser, altura_sensor_real)] = float(presion)
                    except (ValueError, TypeError):
                        continue
            return puntos

        puntos_a = extraer_puntos(datos_a)
        puntos_b = extraer_puntos(datos_b)

        puntos_comunes = set(puntos_a.keys()) & set(puntos_b.keys())
        if len(puntos_comunes) < 4:
            st.error("No hay suficientes puntos comunes para generar la resta de superficies.")
            return None

        puntos_y, puntos_z_altura, puntos_z_diff = [], [], []
        for (y, z) in puntos_comunes:
            diff = puntos_a[(y, z)] - puntos_b[(y, z)]
            puntos_y.append(y)
            puntos_z_altura.append(z)
            puntos_z_diff.append(diff)

        puntos_2d = np.vstack([puntos_y, puntos_z_altura]).T
        tri = Delaunay(puntos_2d)

        fig = go.Figure()

        # Superficie
        fig.add_trace(go.Mesh3d(
            x=puntos_y,
            y=puntos_z_altura,
            z=puntos_z_diff,
            i=tri.simplices[:, 0],
            j=tri.simplices[:, 1],
            k=tri.simplices[:, 2],
            intensity=puntos_z_diff,
            colorscale='Turbo',
            colorbar_title='Δ Presión [Pa]',
            name=f"Diferencia {nombre_a} - {nombre_b}",
            lighting=dict(ambient=0.5, diffuse=0.8, specular=0.5, roughness=0.5, fresnel=0.2),
            lightposition=dict(x=100, y=200, z=100),
            hovertemplate='<b>Δ Presión</b>: %{intensity:.3f} Pa<br>Pos Y: %{x:.1f} mm<br>Altura Z: %{y:.1f} mm<extra></extra>'
        ))

        # Wireframe
        wire_y, wire_z, wire_presion = [], [], []
        for simplex in tri.simplices:
            for idx_pair in [(0,1), (1,2), (2,0)]:
                for idx in idx_pair:
                    wire_y.append(puntos_y[simplex[idx]])
                    wire_z.append(puntos_z_altura[simplex[idx]])
                    wire_presion.append(puntos_z_diff[simplex[idx]])
                wire_y.append(None)
                wire_z.append(None)
                wire_presion.append(None)

        fig.add_trace(go.Scatter3d(
            x=wire_y,
            y=wire_z,
            z=wire_presion,
            mode='lines',
            line=dict(color='black', width=1),
            name='Malla',
            hoverinfo='skip'
        ))

        # Puntos medidos
        if mostrar_puntos:
            fig.add_trace(go.Scatter3d(
                x=puntos_y,
                y=puntos_z_altura,
                z=puntos_z_diff,
                mode='markers',
                marker=dict(size=3, color='red'),
                name='Puntos medidos',
                hovertemplate='<b>Punto medido</b><br>Δ Presión: %{z:.3f} Pa<br>Pos Y: %{x:.1f} mm<br>Altura Z: %{y:.1f} mm<extra></extra>'
            ))

        fig.update_layout(
            title=f"Diferencia de Superficies 3D Mejorada - {nombre_a} - {nombre_b}",
            scene=dict(
                xaxis_title="Posición Y Traverser [mm]",
                yaxis_title="Altura Física Z [mm]",
                zaxis_title="Δ Presión [Pa]",
                aspectmode='data',
                aspectratio=dict(x=1, y=1, z=0.3),
                camera=dict(eye=dict(x=1.6, y=1.6, z=0.9))
            ),
            width=1600,
            height=900,
            margin=dict(l=0, r=0, b=0, t=50)
        )

        return fig

    except Exception as e:
        st.error(f"Error creando la superficie de diferencia 3D mejorada: {str(e)}")
        return None




def crear_superficie_diferencia(datos_a, datos_b, nombre_a, nombre_b):
    """
    Resta dos superficies 3D: para cada (X,Y) común calcula la media de
    todas las columnas 'Presion-Sensor N' presentes en esa fila y resta.
    """
    coords_a = set(tuple(row) for row in datos_a[['Pos_Y_Traverser', 'Pos_Z_Base']].dropna().to_numpy())
    coords_b = set(tuple(row) for row in datos_b[['Pos_Y_Traverser', 'Pos_Z_Base']].dropna().to_numpy())
    coords_comunes = sorted(list(coords_a & coords_b))

    if len(coords_comunes) < 4:
        st.warning("No hay suficientes puntos comunes para generar una superficie.")
        return None

    X_final, Y_final, Z_final = [], [], []

    for y_trav, z_base in coords_comunes:
        fila_a = datos_a[(datos_a['Pos_Y_Traverser'] == y_trav) & (datos_a['Pos_Z_Base'] == z_base)]
        fila_b = datos_b[(datos_b['Pos_Y_Traverser'] == y_trav) & (datos_b['Pos_Z_Base'] == z_base)]

        if fila_a.empty or fila_b.empty:
            continue

        # detectar columnas de sensores en cada fila y promediar
        cols_a = [c for c in fila_a.columns if re.search(r'(?i)presion[-_ ]*sensor', str(c))]
        cols_b = [c for c in fila_b.columns if re.search(r'(?i)presion[-_ ]*sensor', str(c))]

        presiones_a = []
        for c in cols_a:
            try:
                val = fila_a.iloc[0][c]
                if isinstance(val, str):
                    val = float(val.replace(',', '.'))
                presiones_a.append(float(val))
            except:
                continue

        presiones_b = []
        for c in cols_b:
            try:
                val = fila_b.iloc[0][c]
                if isinstance(val, str):
                    val = float(val.replace(',', '.'))
                presiones_b.append(float(val))
            except:
                continue

        if presiones_a and presiones_b:
            diferencia = np.mean(presiones_a) - np.mean(presiones_b)
            X_final.append(y_trav)
            Y_final.append(z_base)
            Z_final.append(diferencia)

    if len(X_final) < 4:
        st.warning("No se pudieron generar suficientes puntos de diferencia para la superficie.")
        return None

    # Crear la malla
    X_unique = sorted(list(set(X_final)))
    Y_unique = sorted(list(set(Y_final)))
    Z_matrix = np.full((len(Y_unique), len(X_unique)), np.nan)

    for x, y, z in zip(X_final, Y_final, Z_final):
        iy = Y_unique.index(y)
        ix = X_unique.index(x)
        Z_matrix[iy, ix] = z

    X_mesh, Y_mesh = np.meshgrid(X_unique, Y_unique)

    fig = go.Figure()
    fig.add_trace(go.Surface(
        x=X_mesh, y=Y_mesh, z=Z_matrix,
        colorscale='RdBu_r',
        colorbar=dict(title="Diferencia de Presión [Pa]"),
        hovertemplate='<b>Diferencia de Presión</b><br>X: %{x:.1f} mm, Y: %{y:.1f} mm<br>Diferencia: %{z:.3f} Pa<extra></extra>'
    ))

    fig.update_layout(
        title=f"Diferencia de Superficies: {nombre_a} vs {nombre_b}",
        scene=dict(
            xaxis_title="Posición X [mm]",
            yaxis_title="Posición Y [mm]",
            zaxis_title="Diferencia de Presión [Pa]"
        ),
        font=dict(color="black")
    )
    fig.update_layout(width=1600, height=900, margin=dict(l=0, r=0, t=50, b=0))
    return fig

    
def crear_grafico_diferencia_areas(sub_archivo_a, sub_archivo_b, configuracion):
    """Crear gráfico mostrando la diferencia como UNA sola área"""
    
    # Extraer datos de ambos sub-archivos
    z_a, presion_a = extraer_datos_para_grafico(sub_archivo_a, configuracion)
    z_b, presion_b = extraer_datos_para_grafico(sub_archivo_b, configuracion)
    
    if not z_a or not z_b or not presion_a or not presion_b:
        return None, 0
    
    # Crear gráfico
    fig = go.Figure()
    
    # Agregar líneas de referencia (más tenues)
    fig.add_trace(go.Scatter(
        x=presion_a, y=z_a,
        mode='lines',
        name=f"{sub_archivo_a['archivo_fuente']} T{sub_archivo_a['tiempo']}s",
        line=dict(color='#08596C', width=2, dash='dot'),
        opacity=0.6,
        hovertemplate='<b>%{fullData.name}</b><br>' +
                    'Presión: %{x:.3f} Pa<br>' +
                    'Altura: %{y:.1f} mm<br>' +
                    '<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=presion_b, y=z_b,
        mode='lines',
        name=f"{sub_archivo_b['archivo_fuente']} T{sub_archivo_b['tiempo']}s",
        line=dict(color='#E74C3C', width=2, dash='dot'),
        opacity=0.6,
        hovertemplate='<b>%{fullData.name}</b><br>' +
                    'Presión: %{x:.3f} Pa<br>' +
                    'Altura: %{y:.1f} mm<br>' +
                    '<extra></extra>'
    ))
    
    # Calcular diferencia punto a punto (interpolando si es necesario)
    # Usar el rango de alturas común
    z_min = max(min(z_a), min(z_b))
    z_max = min(max(z_a), max(z_b))
    
    # Crear puntos interpolados
    z_interp = np.linspace(z_min, z_max, 50)
    
    # Interpolar presiones
    presion_a_interp = np.interp(z_interp, z_a, presion_a)
    presion_b_interp = np.interp(z_b, presion_b)
    
    # Calcular diferencia
    diferencia_presion = presion_a_interp - presion_b_interp
    
    # Crear área de diferencia ÚNICA
    # Determinar color basado en si la diferencia es mayormente positiva o negativa
    diferencia_promedio = np.mean(diferencia_presion)
    color_diferencia = '#27AE60' if diferencia_promedio >= 0 else '#E67E22'  # Verde si A>B, naranja si B>A
    
    # Crear área desde cero hasta la diferencia
    x_area = [0] + list(diferencia_presion) + [0]
    y_area = [z_interp[0]] + list(z_interp) + [z_interp[-1]]
    
    fig.add_trace(go.Scatter(
        x=x_area, y=y_area,
        fill='toself',
        fillcolor=f'rgba({int(color_diferencia[1:3], 16)}, {int(color_diferencia[3:5], 16)}, {int(color_diferencia[5:7], 16)}, 0.4)',
        line=dict(color=color_diferencia, width=3),
        name=f'Diferencia: {sub_archivo_a["archivo_fuente"]} - {sub_archivo_b["archivo_fuente"]}',
        hovertemplate='<b>Diferencia</b><br>' +
                    'Diferencia: %{x:.3f} Pa<br>' +
                    'Altura: %{y:.1f} mm<br>' +
                    '<extra></extra>'
    ))
    
    # Calcular área total de diferencia
    area_diferencia = np.trapz(np.abs(diferencia_presion), z_interp)
    
    # Layout CON LEYENDA MEJORADA
    fig.update_layout(
        title=f"Diferencia de Perfiles: {sub_archivo_a['archivo_fuente']} - {sub_archivo_b['archivo_fuente']}",
        xaxis_title="Presión / Diferencia de Presión [Pa]",
        yaxis_title="Altura z [mm]",
        height=700, width=1000,  # Más ancho para leyenda
        showlegend=True,  # FORZAR LEYENDA VISIBLE
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial", size=12),
        title_font=dict(size=16, color="#FFFFFF"),
        xaxis=dict(
            showgrid=True,
            gridcolor="#000005",
            zeroline=True,
            zerolinecolor='white',
            zerolinewidth=2,
            scaleanchor="y",      # AGREGADO: Configuración solicitada
            scaleratio=4          # AGREGADO: Configuración solicitada
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#080000",
            zeroline=True,
            zerolinecolor='white',
            zerolinewidth=2
        ),
        legend=dict(
            bgcolor='rgba(255,255,255,0.95)',
            bordercolor='#08596C',
            borderwidth=2,
            x=1.02,
            y=1,
            font=dict(size=12, color='black')  # AGREGAR COLOR NEGRO
        )
    )
    fig.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',   # Fondo transparente
    paper_bgcolor='rgba(0,0,0,0)',  # Fondo transparente
    font=dict(color='white'),       # Texto en blanco
    xaxis_title="Presión Total [Pa]",
    yaxis_title="Altura Z [mm]",
    height=900,
    width=1600
    )
    return fig, area_diferencia

def mostrar_configuracion_sensores(section_key):
    """Muestra los widgets de configuración de sensores y guarda el estado."""
    st.markdown("### 📍 Configuración de Sensores y Geometría")

    config_key = f'configuracion_{section_key}'
    if config_key not in st.session_state:
        st.session_state[config_key] = {}

    # Orden de sensores
    orden_sensores = st.selectbox(
        "Orden de lectura de sensores:", ["asc", "des"],
        format_func=lambda x: "Ascendente (sensor 1 abajo, 12 arriba)" if x == "asc" else "Descendente (sensor 12 abajo, 1 arriba)",
        help="Define cómo se leen los datos de los sensores en relación a su posición física.",
        key=f'orden_sensores_{section_key}'
    )
    
    st.info("🔍 **Pregunta:** ¿Qué sensor corresponde a la toma número 12 (la que se encuentra cerca del piso)?")
    sensor_referencia = st.selectbox(
        "Sensor de referencia (toma 12):", [f"Sensor {i}" for i in range(1, 13)],
        index=11, help="Seleccione el sensor que corresponde a la toma física número 12.",
        key=f'sensor_ref_{section_key}'
    )
    
    distancia_toma_12 = st.number_input(
        "Distancia de la toma 12 a la posición X=0, Y=0 del traverser [mm]:",
        value=-120.0, step=1.0, format="%.1f",
        help="Distancia en mm desde el punto de referencia del traverser.",
        key=f'dist_toma_{section_key}'
    )
    
    distancia_entre_tomas = st.number_input(
        "Distancia entre tomas [mm]:", value=10.0, step=0.01, format="%.2f",
        help="Distancia física entre tomas consecutivas según el plano técnico.",
        key=f'dist_entre_{section_key}'
    )
    
    if st.button(f"💾 Guardar Configuración", type="primary", key=f'save_config_{section_key}'):
        st.session_state[config_key] = {
            'orden': orden_sensores,
            'sensor_referencia': sensor_referencia,
            'distancia_toma_12': distancia_toma_12,
            'distancia_entre_tomas': distancia_entre_tomas
        }
        st.success(f"✅ Configuración para la sección {section_key.upper()} guardada.")
        st.rerun()

    return st.session_state.get(config_key, {})

def crear_superficie_delaunay_3d(datos_completos, configuracion_3d, nombre_archivo, mostrar_puntos=True):
    """
    Crea una superficie 3D continua con Delaunay y mejoras visuales.
    Ahora permite activar/desactivar la visualización de puntos medidos.
    """
    try:
        posicion_inicial = configuracion_3d['distancia_toma_12']
        distancia_entre_tomas = configuracion_3d['distancia_entre_tomas']
        orden = configuracion_3d['orden']

        puntos_y, puntos_z_altura, presiones_z = [], [], []  # Cambio de nombres: x->y, y->z

        # Detectar columnas de sensores
        sensor_cols = [c for c in datos_completos.columns if re.search(r'(?i)presion[-_ ]*sensor', str(c))]

        for _, fila in datos_completos.iterrows():
            y_traverser = fila.get('Pos_Y_Traverser', None) 
            z_base_ref = fila.get('Pos_Z_Base', None)
            if pd.isna(y_traverser) or pd.isna(z_base_ref):
                continue

            for col in sensor_cols:
                sensor_num = obtener_numero_sensor_desde_columna(col)
                if sensor_num is None:
                    continue
                altura_sensor_real = calcular_altura_absoluta_z(
                    sensor_num, z_base_ref, posicion_inicial, distancia_entre_tomas, orden
                )
                presion = fila.get(col, None)
                if pd.isna(presion) or presion is None:
                    continue
                try:
                    if isinstance(presion, str):
                        presion = float(presion.replace(',', '.'))
                    presion_val = float(presion)
                    puntos_y.append(y_traverser)  # Ahora es Y explicitamente
                    puntos_z_altura.append(altura_sensor_real)  # Ahora es Z explicitamente
                    presiones_z.append(presion_val)
                except (ValueError, TypeError):
                    continue

        if len(puntos_y) < 4:
            st.error("No hay suficientes datos válidos para generar una superficie.")
            return None

        # Triangulación Delaunay
        puntos_2d = np.vstack([puntos_y, puntos_z_altura]).T
        tri = Delaunay(puntos_2d)

        fig = go.Figure()

        # Superficie principal
        fig.add_trace(go.Mesh3d(
            x=puntos_y,  # Ahora Y en eje X del gráfico
            y=puntos_z_altura,  # Ahora Z en eje Y del gráfico
            z=presiones_z,
            i=tri.simplices[:, 0],
            j=tri.simplices[:, 1],
            k=tri.simplices[:, 2],
            intensity=presiones_z,
            colorscale='Turbo',
            colorbar_title='Presión [Pa]',
            name='Superficie de presión',
            lighting=dict(ambient=0.5, diffuse=0.8, specular=0.5, roughness=0.5, fresnel=0.2),
            lightposition=dict(x=100, y=200, z=100),
            hovertemplate='<b>Presión</b>: %{intensity:.3f} Pa<br>Pos Y: %{x:.1f} mm<br>Altura Z: %{y:.1f} mm<extra></extra>'
        ))

        # Wireframe
        wire_y, wire_z, wire_presion = [], [], []
        for simplex in tri.simplices:
            for idx_pair in [(0,1), (1,2), (2,0)]:
                for idx in idx_pair:
                    wire_y.append(puntos_y[simplex[idx]])
                    wire_z.append(puntos_z_altura[simplex[idx]])
                    wire_presion.append(presiones_z[simplex[idx]])
                wire_y.append(None)
                wire_z.append(None)
                wire_presion.append(None)

        fig.add_trace(go.Scatter3d(
            x=wire_y,
            y=wire_z,
            z=wire_presion,
            mode='lines',
            line=dict(color='black', width=1),
            name='Malla',
            hoverinfo='skip'
        ))

        # Puntos medidos (si mostrar_puntos=True)
        if mostrar_puntos:
            fig.add_trace(go.Scatter3d(
                x=puntos_y,
                y=puntos_z_altura,
                z=presiones_z,
                mode='markers',
                marker=dict(size=3, color='red'),
                name='Puntos medidos',
                hovertemplate='<b>Punto medido</b><br>Presión: %{z:.3f} Pa<br>Pos Y: %{x:.1f} mm<br>Altura Z: %{y:.1f} mm<extra></extra>'
            ))

        fig.update_layout(
            title=f"Superficie de Presión 3D Mejorada - {nombre_archivo}",
            scene=dict(
                xaxis_title="Posición Y Traverser [mm]",  # Cambio de etiquetas
                yaxis_title="Altura Física Z [mm]",  # Cambio de etiquetas
                zaxis_title="Presión [Pa]",
                aspectmode='data',  # Configuración manual para escala 1:1
                aspectratio=dict(x=1, y=1, z=1),  # Relación 1:1 entre Y y Z
            ),
            width=1600,
            height=900,
            margin=dict(l=0, r=0, b=0, t=50)
        )

        return fig

    except Exception as e:
        st.error(f"Error creando la superficie de malla 3D mejorada: {str(e)}")
        return None

def unir_archivos_incertidumbre(archivos_lista, nombre_salida):
    """Une múltiples archivos de incertidumbre en uno solo"""
    try:
        contenido_unido = []
        puntos_sobrepuestos = []
        coordenadas_vistas = set()
        
        for archivo in archivos_lista:
            # Leer archivo CSV
            df_raw = pd.read_csv(archivo, sep=";", header=None, dtype=str)
            
            # Buscar la palabra "importante" para determinar dónde terminar
            index_final = df_raw[df_raw.apply(lambda row: row.astype(str).str.contains("importante", case=False).any(), axis=1)].index
            if not index_final.empty:
                df_raw = df_raw.iloc[:index_final[0]]
            
            # Procesar bloques de 10 filas
            for i in range(0, df_raw.shape[0], 10):
                bloque = df_raw.iloc[i:i+10]
                if bloque.empty or len(bloque) < 3:
                    continue
                
                nombre_archivo_bloque = bloque.iloc[0, 0]
                tiempo, y_trav, z_base = extraer_tiempo_y_coordenadas_YZ(nombre_archivo_bloque)
                
                # Verificar si hay puntos sobrepuestos
                coordenada_key = (y_trav, z_base, tiempo)
                if coordenada_key in coordenadas_vistas:
                    puntos_sobrepuestos.append(coordenada_key)
                else:
                    coordenadas_vistas.add(coordenada_key)
                
                # Agregar bloque al contenido unido
                contenido_unido.extend(bloque.values.tolist())
        
        # Crear DataFrame final
        df_unido = pd.DataFrame(contenido_unido)
        
        # Convertir a CSV
        csv_output = df_unido.to_csv(sep=';', index=False, header=False)
        
        return csv_output, puntos_sobrepuestos
        
    except Exception as e:
        st.error(f"Error al unir archivos: {str(e)}")
        return None, []

def extraer_matriz_presiones_completa(archivo_incertidumbre, configuracion):
    """
    Devuelve un DataFrame con columnas Y, Z, Presion
    listo para exportar como VTK estructurado.
    Unificada y corregida para usar lógica Y-Z.
    """
    try:
        # Procesar archivo CSV
        datos = procesar_promedios(archivo_incertidumbre, configuracion["orden"])
        if datos is None:
            return pd.DataFrame(columns=["Y", "Z", "Presion"])

        registros = []
        sensor_cols = [c for c in datos.columns if re.search(r'(?i)presion[-_ ]*sensor', str(c))]

        for _, fila in datos.iterrows():
            y_trav = fila.get("Pos_Y_Traverser")
            z_base = fila.get("Pos_Z_Base") 
            if pd.isna(y_trav) or pd.isna(z_base):
                continue

            for col in sensor_cols:
                num = obtener_numero_sensor_desde_columna(col)
                if num is None:
                    continue

                z_real = calcular_altura_absoluta_z(
                    num,
                    z_base,
                    configuracion["distancia_toma_12"],
                    configuracion["distancia_entre_tomas"],
                    len(sensor_cols),
                    configuracion["orden"]
                )

                presion = fila.get(col, None)
                if presion is None or pd.isna(presion):
                    continue

                try:
                    presion_val = float(str(presion).replace(",", "."))
                    registros.append((float(y_trav), float(z_real), presion_val))
                except ValueError:
                    continue

        # Convertir a DataFrame ORDENADO
        df = pd.DataFrame(registros, columns=["Y", "Z", "Presion"])
        df = df.sort_values(by=["Y", "Z"]).reset_index(drop=True)
        return df

    except Exception as e:
        st.error(f"Error al extraer matriz de presiones: {str(e)}")
        return pd.DataFrame(columns=["Y", "Z", "Presion"])


def crear_archivo_vtk_superficie_delaunay(df_matriz, nombre_archivo_vtk):
    """
    Genera un archivo VTK con superficie triangulada (Delaunay) CORREGIDO para Salome/ParaView.
    La matriz debe tener columnas: Y, Z, Presion.
    """
    try:
        # Extraer puntos y presiones
        puntos_y = df_matriz["Y"].astype(float).values
        puntos_z = df_matriz["Z"].astype(float).values
        presiones = df_matriz["Presion"].astype(float).values
        
        # Filtrar valores NaN
        mask = ~(np.isnan(puntos_y) | np.isnan(puntos_z) | np.isnan(presiones))
        puntos_y = puntos_y[mask]
        puntos_z = puntos_z[mask]
        presiones = presiones[mask]

        if len(puntos_y) < 4:
            print("Error: No hay suficientes puntos válidos para generar una superficie triangulada.")
            return None

        # Triangulación en el plano (Y,Z)
        puntos_2d = np.column_stack([puntos_y, puntos_z])
        tri = Delaunay(puntos_2d)

        n_points = len(puntos_y)
        n_triangles = len(tri.simplices)

        # Crear contenido VTK con formato correcto
        vtk_content = "# vtk DataFile Version 3.0\n"
        vtk_content += "Superficie Delaunay - Matriz de Presion\n"
        vtk_content += "ASCII\n"
        vtk_content += "DATASET UNSTRUCTURED_GRID\n"
        vtk_content += f"POINTS {n_points} float\n"

        # CORRECCIÓN: Usar coordenadas Y, Z y presión como altura Z
        for i in range(n_points):
            vtk_content += f"{puntos_y[i]:.6f} {puntos_z[i]:.6f} {presiones[i]:.6f}\n"

        # Definir celdas triangulares
        vtk_content += f"\nCELLS {n_triangles} {4*n_triangles}\n"
        for simplex in tri.simplices:
            vtk_content += f"3 {simplex[0]} {simplex[1]} {simplex[2]}\n"

        # Tipos de celda (5 = VTK_TRIANGLE)
        vtk_content += f"\nCELL_TYPES {n_triangles}\n"
        for _ in range(n_triangles):
            vtk_content += "5\n"

        # Datos escalares en puntos
        vtk_content += f"\nPOINT_DATA {n_points}\n"
        vtk_content += "SCALARS Presion float 1\n"
        vtk_content += "LOOKUP_TABLE default\n"
        for p in presiones:
            vtk_content += f"{p:.6f}\n"

        # Coordenadas adicionales como campos escalares
        vtk_content += "\nSCALARS Coord_Y float 1\n"
        vtk_content += "LOOKUP_TABLE default\n"
        for y in puntos_y:
            vtk_content += f"{y:.6f}\n"

        vtk_content += "\nSCALARS Coord_Z float 1\n"
        vtk_content += "LOOKUP_TABLE default\n"
        for z in puntos_z:
            vtk_content += f"{z:.6f}\n"

        # Guardar archivo
        with open(nombre_archivo_vtk, "w", encoding="ascii", errors="replace") as f:
            f.write(vtk_content)

        print(f"✅ Archivo VTK creado exitosamente: {nombre_archivo_vtk}")
        print(f"Superficie con {n_points} puntos y {n_triangles} triángulos")
        
        return nombre_archivo_vtk

    except Exception as e:
        print(f"❌ Error al crear archivo VTK de superficie Delaunay: {str(e)}")
        return None

def crear_sub_archivos_3d_por_tiempo_y_posicion(df_datos, nombre_archivo):
    """Crear sub-archivos 3D por tiempo y posición (similar a 2D)"""
    sub_archivos = {}
    
    # Obtener tiempos únicos
    tiempos_unicos = df_datos["Tiempo_s"].dropna().unique()
    
    for tiempo in tiempos_unicos:
        # Filtrar datos por tiempo
        df_tiempo = df_datos[df_datos["Tiempo_s"] == tiempo].copy()
        
        # Crear clave para el sub-archivo
        clave_sub_archivo = f"{nombre_archivo}_T{tiempo}s"

        sub_archivos[clave_sub_archivo] = {
            'archivo_fuente': nombre_archivo,
            'tiempo': tiempo,
            'datos': df_tiempo,
            'nombre_archivo': f"{nombre_archivo}_T{tiempo}s.csv"
        }
    
    return sub_archivos

def mostrar_resumen_archivos_tabla(sub_archivos_por_fuente):
    """Mostrar resumen de archivos en formato tabla organizada"""
    st.markdown("### 📊 Resumen de Sub-archivos Generados")
    
    # Crear datos para la tabla
    datos_tabla = []
    
    for archivo_fuente, tiempos_dict in sub_archivos_por_fuente.items():
        for tiempo, sub_archivos_tiempo in sub_archivos_tiempo:
            for clave, sub_archivo in sub_archivos_tiempo:
                datos_tabla.append({
                    'Archivo_Fuente': archivo_fuente,
                    'Tiempo_s': f"T{tiempo}s", 
                    'Posición_X': sub_archivo['x_traverser'],
                    'Registros': len(sub_archivo['datos']),
                    'Nombre_Archivo': sub_archivo['nombre_archivo'],
                    'Clave': clave
                })
    
    # Crear DataFrame y mostrar como tabla
    df_resumen = pd.DataFrame(datos_tabla).sort_values(['Archivo_Fuente', 'Posición_X', 'Tiempo_s'])
    
    # NUEVO: Mostrar tabla con separadores correctos para CSV
    st.dataframe(
        df_resumen[['Archivo_Fuente', 'Tiempo_s', 'Registros', 'Nombre_Archivo']], 
        use_container_width=True,
        hide_index=True
    )
    
    # NUEVO: Botón para descargar tabla como CSV bien formateado
    csv_tabla = df_resumen[['Archivo_Fuente', 'Tiempo_s', 'Registros', 'Nombre_Archivo']].to_csv(
        index=False, 
        sep=';',  # CAMBIAR a punto y coma para Excel
        encoding='utf-8-sig',  # CAMBIAR encoding para Excel
        decimal=','  # AGREGAR separador decimal para Excel
    )
    
    st.download_button(
        label="📥 Descargar Tabla Resumen (CSV)",
        data=csv_tabla,
        file_name=f"resumen_subarchivos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
    
    # Estadísticas adicionales
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Sub-archivos", len(datos_tabla))
    with col2:
        st.metric("Archivos Fuente", len(sub_archivos_por_fuente))
    with col3:
        total_registros = sum([item['Registros'] for item in datos_tabla])
        st.metric("Total Registros", total_registros)

def cargar_matriz_para_vtk():
    if opcion_matriz == "Usar matriz existente" and matriz_disponible:
        st.info(f"Usando matriz existente: {matriz_disponible['nombre']}")
        return matriz_disponible['matriz']

    elif opcion_matriz == "Cargar nuevo archivo" and archivo_vtk_source:
        with st.spinner("Extrayendo matriz para VTK..."):
            try:
                    # Intentar leer como matriz ya procesada
                df = pd.read_csv(archivo_vtk_source)
                if {"Y", "Z", "Presion"}.issubset(df.columns):
                    return df
                else:
                    # Si no tiene las columnas, asumir que es archivo de sensores crudos
                    return extraer_matriz_presiones_completa(
                        archivo_vtk_source,
                        st.session_state.get("configuracion_inicial", {})
                    )
            except Exception as e:
                st.error(f"Error al cargar CSV: {e}")
                return None

    return None

def crear_archivo_vtk_interpolado(df_matriz, nombre_base, resolucion_factor=2, metadata=None, posicion_x=0.0):
    """
    Genera un archivo VTK ESTRUCTURADA con interpolación Cúbica (Spline).
    Permite aumentar la resolución de la grilla para suavizar la visualización.
    NOTA: Se removió la metadata para evitar errores de compatibilidad.
    """
    try:
        if df_matriz.empty or not {"Y", "Z", "Presion"}.issubset(df_matriz.columns):
            st.error("El DataFrame para VTK está vacío o no tiene las columnas requeridas (Y, Z, Presion).")
            return None

        # Obtener valores únicos
        y_vals = sorted(df_matriz['Y'].unique())
        z_vals = sorted(df_matriz['Z'].unique())
        
        # Grid original
        Y_orig, Z_orig = np.meshgrid(y_vals, z_vals, indexing='ij')
        
        # Puntos y valores conocidos
        puntos_conocidos = df_matriz[['Y', 'Z']].values
        valores_conocidos = df_matriz['Presion'].values

        # Crear nueva grilla de mayor resolución
        y_new = np.linspace(min(y_vals), max(y_vals), len(y_vals) * resolucion_factor)
        z_new = np.linspace(min(z_vals), max(z_vals), len(z_vals) * resolucion_factor)
        ny, nz = len(y_new), len(z_new)
        
        Y_grid_new, Z_grid_new = np.meshgrid(y_new, z_new, indexing='ij')
        
        # Interpolación Cúbica
        P_grid_new = griddata(
            puntos_conocidos, 
            valores_conocidos, 
            (Y_grid_new, Z_grid_new), 
            method='cubic', 
            fill_value=0.0
        )
        
        # Rellenar nans en bordes con nearest si es necesario, o dejar 0
        mask_nan = np.isnan(P_grid_new)
        if mask_nan.any():
             P_grid_new[mask_nan] = griddata(
                puntos_conocidos, 
                valores_conocidos, 
                (Y_grid_new[mask_nan], Z_grid_new[mask_nan]), 
                method='nearest'
            )

        nombre_archivo = f"{nombre_base}_interpolado_cubic.vtk"

        # Cabecera VTK
        lines = []
        lines.append("# vtk DataFile Version 3.0")
        lines.append("Campo de Presiones Interpolado (Cubic Spline)")
        lines.append("ASCII")
        lines.append("DATASET STRUCTURED_GRID")
        lines.append(f"DIMENSIONS 1 {ny} {nz}")
        lines.append(f"POINTS {ny * nz} float")

        # Escribir puntos (Planar YZ -> X=0)
        for j in range(nz):
            for i in range(ny):
                lines.append(f"{posicion_x:.6f} {y_new[i]:.6f} {z_new[j]:.6f}")

        # POINT DATA
        lines.append(f"\nPOINT_DATA {ny * nz}")
        lines.append("SCALARS Presion float 1")
        lines.append("LOOKUP_TABLE default")
        for j in range(nz):
            for i in range(ny):
                lines.append(f"{P_grid_new[i, j]:.6f}")

        # METADATA REMOVED PER USER REQUEST TO AVOID ERRORS

        with open(nombre_archivo, "w", encoding="ascii") as f:
            f.write("\n".join(lines))

        st.success(f"✅ Archivo VTK Avanzado creado: {nombre_archivo}")
        return nombre_archivo

    except Exception as e:
        st.error(f"❌ Error al crear el archivo VTK interpolado: {str(e)}")
        return None



def crear_vtk_superficie_3d_delaunay(df_matriz, nombre_base, posicion_x=0.0):
    """
    Genera un archivo VTK con una superficie 3D (malla no estructurada)
    usando triangulación de Delaunay.
    La base de la superficie está en el plano YZ y la presión se representa
    como la coordenada en el eje X.
    """
    try:
        if df_matriz.empty or not {"Y", "Z", "Presion"}.issubset(df_matriz.columns):
            st.error("El DataFrame para VTK 3D está vacío o no tiene las columnas requeridas.")
            return None

        # Extraer y limpiar los datos
        puntos_y = df_matriz["Y"].values
        puntos_z = df_matriz["Z"].values
        presiones = df_matriz["Presion"].values
        
        mask = ~np.isnan(puntos_y) & ~np.isnan(puntos_z) & ~np.isnan(presiones)
        puntos_y, puntos_z, presiones = puntos_y[mask], puntos_z[mask], presiones[mask]

        if len(puntos_y) < 3:
            st.error("Se necesitan al menos 3 puntos válidos para la triangulación.")
            return None

        # La triangulación se sigue haciendo en el plano YZ
        puntos_2d_plano = np.column_stack([puntos_y, puntos_z])
        tri = Delaunay(puntos_2d_plano)

        n_points = len(puntos_y)
        n_triangles = len(tri.simplices)
        nombre_archivo_vtk = f"{nombre_base}_superficie_3D_presion_en_X.vtk"

        # Contenido del archivo VTK
        vtk_content = "# vtk DataFile Version 3.0\n"
        vtk_content += "Superficie de Presion 3D (Plano YZ, Presion en X)\n"
        vtk_content += "ASCII\n"
        vtk_content += "DATASET UNSTRUCTURED_GRID\n"
        vtk_content += f"POINTS {n_points} float\n"

        for i in range(n_points):
            # ---------------------------------------------------------------- #
            # ¡CAMBIO CLAVE! AHORA SE AÑADE LA POSICIÓN X A LA PRESIÓN (Estilo 4D)
            # Formato (X, Y, Z) -> (posicion_x + Presion_valor, Y_coord, Z_coord)
            x_def = posicion_x + presiones[i]
            vtk_content += f"{x_def:.6f} {puntos_y[i]:.6f} {puntos_z[i]:.6f}\n"
            # ---------------------------------------------------------------- #

        # El resto de la función (celdas y datos) permanece igual
        vtk_content += f"\nCELLS {n_triangles} {4 * n_triangles}\n"
        for simplex in tri.simplices:
            vtk_content += f"3 {simplex[0]} {simplex[1]} {simplex[2]}\n"

        vtk_content += f"\nCELL_TYPES {n_triangles}\n"
        vtk_content += "5\n" * n_triangles

        vtk_content += f"\nPOINT_DATA {n_points}\n"
        vtk_content += "SCALARS Presion float 1\n"
        vtk_content += "LOOKUP_TABLE default\n"
        for p in presiones:
            vtk_content += f"{p:.6f}\n"
            
        with open(nombre_archivo_vtk, "w", encoding="ascii") as f:
            f.write(vtk_content)
            
        st.success(f"✅ Archivo VTK 3D (Presión en Eje X) creado: {nombre_archivo_vtk}")
        return nombre_archivo_vtk

    except Exception as e:
        st.error(f"❌ Error al crear el archivo VTK de superficie 3D: {str(e)}")
        return None

# ---------------------------------------------------------------------------
# FUNCIÓN: VTK PLANO DE PRESIÓN 2D
# Genera un archivo VTK ESTRUCTURADA plano (sin deformación en X).
# La presión se guarda SOLO como dato escalar (color), no como geometría.
# ---------------------------------------------------------------------------
def crear_vtk_plano_presion_2d(df_matriz, nombre_base, posicion_x=0.0):
    """
    Genera un VTK 'STRUCTURED_GRID' plano en el plano YZ (X fijo = posicion_x).
    La presión se codifica ÚNICAMENTE como escalar de color (POINT_DATA),
    sin ninguna deformación geométrica. Ideal para visualizar contornos de
    presión en ParaView con colormaps.
    """
    try:
        if df_matriz.empty or not {"Y", "Z", "Presion"}.issubset(df_matriz.columns):
            st.error("El DataFrame para VTK Plano está vacío o le faltan columnas (Y, Z, Presion).")
            return None

        y_vals = sorted(df_matriz['Y'].unique())
        z_vals = sorted(df_matriz['Z'].unique())
        ny, nz = len(y_vals), len(z_vals)

        # Mapa rápido (Y, Z) → Presion
        presion_map = {(float(row['Y']), float(row['Z'])): float(row['Presion'])
                       for _, row in df_matriz.iterrows()
                       if not (pd.isna(row['Y']) or pd.isna(row['Z']) or pd.isna(row['Presion']))}

        lines = []
        lines.append("# vtk DataFile Version 3.0")
        lines.append("Plano de Presion 2D (YZ) - Solo Color")
        lines.append("ASCII")
        lines.append("DATASET STRUCTURED_GRID")
        lines.append(f"DIMENSIONS 1 {ny} {nz}")
        lines.append(f"POINTS {ny * nz} float")

        presiones_ordenadas = []
        for z in z_vals:
            for y in y_vals:
                lines.append(f"{posicion_x:.6f} {y:.6f} {z:.6f}")
                # Presión para este punto (0.0 si no encontrado)
                presiones_ordenadas.append(presion_map.get((float(y), float(z)), 0.0))

        lines.append(f"\nPOINT_DATA {ny * nz}")
        lines.append("SCALARS Presion float 1")
        lines.append("LOOKUP_TABLE default")
        for p in presiones_ordenadas:
            lines.append(f"{p:.6f}")

        vtk_str = "\n".join(lines)
        nombre_archivo = f"{nombre_base}_plano2D_X{int(posicion_x)}.vtk"

        with open(nombre_archivo, "w", encoding="ascii") as f:
            f.write(vtk_str)

        st.success(f"✅ VTK Plano 2D creado: {nombre_archivo}")
        return nombre_archivo, vtk_str.encode('ascii')

    except Exception as e:
        st.error(f"❌ Error al crear VTK Plano 2D: {str(e)}")
        return None


# Sidebar (Legacy removed)

# Contenido principal según la sección
if st.session_state.seccion_actual == 'inicio':
    # --- HERO SECTION (SpaceX Style) ---
    st.markdown("""
    <style>
        .hero-container {
            position: relative;
            width: 100%;
            padding: 4rem 1rem;
            background-image: linear-gradient(to bottom, rgba(0,0,0,0.3), rgba(0,0,0,1)), url('https://images.unsplash.com/photo-1517976487492-5750f3195933?q=80&w=2070&auto=format&fit=crop');
            background-size: cover;
            background-position: center;
            border-radius: 0px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            margin-bottom: 3rem;
            border: 1px solid #333;
            min-height: 60vh;
        }
        
        .hero-title {
            font-family: 'Orbitron', sans-serif;
            font-size: 4rem;
            font-weight: 900;
            letter-spacing: 2px;
            margin-bottom: 0.5rem;
            text-shadow: 0 10px 30px rgba(0,0,0,0.5);
            color: white;
        }
        
        .hero-subtitle {
            font-family: 'Inter', sans-serif;
            font-size: 1.1rem;
            letter-spacing: 6px;
            text-transform: uppercase;
            color: rgba(255,255,255,0.8);
            margin-top: 0.5rem;
        }
        
        .scroll-indicator {
            margin-top: 4rem; 
            opacity: 0.7; 
            font-size: 0.8rem;
            animation: bounce 2s infinite;
        }
        
        @keyframes bounce {
            0%, 20%, 50%, 80%, 100% {transform: translateY(0);}
            40% {transform: translateY(-10px);}
            60% {transform: translateY(-5px);}
        }
    </style>
    
    <div class="hero-container">
        <h1 class="hero-title">LABORATORIO</h1>
        <p class="hero-subtitle">Aerodinámica Experimental</p>
        <div class="scroll-indicator">
            ▼ DESLIZA PARA NAVEGAR
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # --- RENDER NAVBAR AFTER HERO ---
    render_navbar()
    
    # --- 📖 SECCIÓN 1: MANUAL DE USUARIO (SCROLLING) ---
    st.markdown("""
<div class="section-card">
<h2 style="border-bottom: 2px solid #4ade80; padding-bottom: 15px; margin-bottom: 20px;">📖 MANUAL DE USUARIO</h2>
<div class="manual-text">
<h4 class="manual-header">1. INTRODUCCIÓN</h4>
<p>Bienvenido al Sistema de Procesamiento de Datos del Túnel de Viento (App BETZ). Esta aplicación ha sido diseñada para automatizar el análisis de perfiles de presión, visualización de estelas y generación de superficies 4D.</p>

<h4 class="manual-header">2. VISUALIZACIÓN DE ESTELA 1D</h4>
<p>Este módulo permite analizar perfiles de presión en un corte unidimensional. El usuario debe cargar los archivos CSV de incertidumbre. El sistema detectará automáticamente el tiempo de medición y la posición del traverser.</p>
<p><strong>Configuración:</strong> Antes de cargar datos, asegúrese de configurar la referencia geométrica (distancia de toma 12, separación entre tomas) en el 'Paso 1'.</p>

<h4 class="manual-header">3. VISUALIZACIÓN DE ESTELA 2D</h4>
<p>Próximamente disponible.</p>

<h4 class="manual-header">4. VISUALIZACIÓN DE ESTELA 3D</h4>
<p>Permite la reconstrucción de volúmenes de presión a partir de múltiples barridos. Cargue múltiples archivos CSV correspondientes a diferentes estaciones o tiempos. El visualizador 3D generará una superficie interactiva.</p>

<h4 class="manual-header">5. VISUALIZACIÓN DE ESTELA 4D</h4>
<p>Genera progresiones espaciales y temporales interactuando con las superficies tridimensionales.</p>

<h4 class="manual-header">6. HERRAMIENTAS ADICIONALES</h4>
<p>En la sección inferior encontrará utilidades para unir archivos fraccionados, extraer matrices puras y convertir formatos para software CFD externo (ParaView, Salome).</p>

<br>
<p style="font-style: italic; color: #888;">(Este es un texto de ejemplo. Por favor, reemplace este contenido con el texto completo de su archivo Word 'Manual de Usuario.docx').</p>
</div>
</div>
""", unsafe_allow_html=True)
    
    # --- 🛠️ SECCIÓN 2: ACCESO A SECCIONES (GRID) ---
    st.markdown("<h2 style='margin-top: 4rem; margin-bottom: 2rem; text-align: center;'>NUESTRO TABLERO DE TRABAJO</h2>", unsafe_allow_html=True)
    
    # === GRUPO 1: ESTELAS ===
    st.markdown("<h3 style='margin-top: 1rem; color: #aaa; border-bottom: 1px solid #333; padding-bottom: 10px;'>🌌 ENSAYOS DE ESTELA</h3>", unsafe_allow_html=True)
    
    r1c1, r1c2 = st.columns(2)
    with r1c1:
        st.markdown("""
        <div class="section-card" style="border-left: 5px solid #3b82f6; height: 160px; margin-bottom: 10px;">
            <h3 style="color: #3b82f6; margin-top: 0; margin-bottom: 10px;">📊 VIS. ESTELA 1D</h3>
            <p style="color: #bbb; font-size: 0.95rem; margin-bottom: 0;">Procesa archivos CSV de incertidumbre, calcula integrales de presión y permite exportar tabulados bidimensionales.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("ACCEDER AL MÓDULO 1D", key="btn_row_1d", use_container_width=True):
             st.session_state.seccion_actual = 'betz_2d'
             st.rerun()

    with r1c2:
        st.markdown("""
        <div class="section-card" style="border-left: 5px solid #06b6d4; height: 160px; margin-bottom: 10px;">
            <h3 style="color: #06b6d4; margin-top: 0; margin-bottom: 10px;">📈 VIS. ESTELA 2D</h3>
            <p style="color: #bbb; font-size: 0.95rem; margin-bottom: 0;">Sección en pleno desarrollo para procesamiento mejorado con distribuciones 2D.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("ACCEDER AL MÓDULO 2D", key="btn_row_2d_nueva", use_container_width=True):
             st.session_state.seccion_actual = 'vis_2d_nueva'
             st.rerun()

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    r2c1, r2c2 = st.columns(2)
    with r2c1:
        st.markdown("""
        <div class="section-card" style="border-left: 5px solid #8b5cf6; height: 160px; margin-bottom: 10px;">
            <h3 style="color: #8b5cf6; margin-top: 0; margin-bottom: 10px;">🌪️ VIS. ESTELA 3D</h3>
            <p style="color: #bbb; font-size: 0.95rem; margin-bottom: 0;">Reconstrucción 3D volumétrica a partir de cortes. Genera mallas VTK para exportación a CFD.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("ACCEDER AL MÓDULO 3D", key="btn_row_3d", use_container_width=True):
             st.session_state.seccion_actual = 'betz_3d'
             st.rerun()

    with r2c2:
        st.markdown("""
        <div class="section-card" style="border-left: 5px solid #ec4899; height: 160px; margin-bottom: 10px;">
            <h3 style="color: #ec4899; margin-top: 0; margin-bottom: 10px;">🌌 VIS. ESTELA 4D</h3>
            <p style="color: #bbb; font-size: 0.95rem; margin-bottom: 0;">Cálculo de progresiones espaciales y temporales interactuando con las superficies 3D.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("ACCEDER AL MÓDULO 4D", key="btn_row_4d", use_container_width=True):
             st.session_state.seccion_actual = 'betz_4d'
             st.rerun()

    # === GRUPO 2: BETZ ===
    st.markdown("<h3 style='margin-top: 3rem; color: #aaa; border-bottom: 1px solid #333; padding-bottom: 10px;'>🧪 ENSAYOS DE BETZ</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="section-card" style="border-left: 5px solid #f59e0b; height: 150px; margin-bottom: 10px;">
        <h3 style="color: #f59e0b; margin-top: 0; margin-bottom: 10px;">🧪 ENSAYO DE ALAS (BETZ)</h3>
        <p style="color: #bbb; font-size: 0.95rem; margin-bottom: 0;">Sección para el estudio y predicción de estela de perfiles de ala. Actualmente en diseño técnico y de algoritmos.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("ACCEDER A ENSAYOS", key="btn_row_ensayo", use_container_width=True):
         st.session_state.seccion_actual = 'ensayo_betz'
         st.rerun()

    # === GRUPO 3: HERRAMIENTAS ===
    st.markdown("<h3 style='margin-top: 3rem; color: #aaa; border-bottom: 1px solid #333; padding-bottom: 10px;'>🔧 HERRAMIENTAS MÚLTIPLES</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="section-card" style="border-left: 5px solid #10b981; height: 150px; margin-bottom: 10px;">
        <h3 style="color: #10b981; margin-top: 0; margin-bottom: 10px;">🔧 UTILIDADES</h3>
        <p style="color: #bbb; font-size: 0.95rem; margin-bottom: 0;">Unión de archivos fragmentados y extracción rápida de matrices de presión puras o tabuladas listas para graficadores externos.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("ACCEDER A UTILIDADES", key="btn_row_tools", use_container_width=True):
         st.session_state.seccion_actual = 'herramientas'
         st.rerun()

    st.markdown("---")
    st.markdown("<div style='text-align:center; color:#444; font-size: 0.8rem;'>UTN HAEDO // DEPARTAMENTO DE INGENIERÍA AERONÁUTICA</div>", unsafe_allow_html=True)



elif st.session_state.seccion_actual == 'betz_2d':
    if st.session_state.configuracion_inicial:
        st.markdown("# 📊 VISUALIZACIÓN DE ESTELA 1D - Análisis Unidimensional")
        st.markdown("Análisis de perfiles de presión concatenados con extracción automática de tiempo y coordenadas")
    # --- Inicializar variables persistentes ---
    if "datos_procesados_betz2d" not in st.session_state:
        st.session_state.datos_procesados_betz2d = {}
    if "sub_archivos_betz2d" not in st.session_state:
        st.session_state.sub_archivos_betz2d = {}
    if "uploaded_files_betz2d" not in st.session_state:
        st.session_state.uploaded_files_betz2d = []

    # Paso 1: Configuración inicial
    st.markdown("## ⚙️ Paso 1: Configuración Inicial")

    # --- PASO 1: CONFIGURACIÓN ---
    st.markdown("""
    <div class="section-card" style="margin-bottom: 20px;">
        <h3 style="margin-top: 0; color: white;">📍 PASO 1: CONFIGURACIÓN DE GEOMETRÍA</h3>
        <p style="color: #bbb; margin-bottom: 20px;">Defina los parámetros físicos del peine de sensores y el traverser.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_config, col_ref = st.columns([2, 1])
    
    with col_config:
        st.markdown("<div style='padding: 1rem; border: 1px solid #333; border-radius: 8px; background-color: #000;'>", unsafe_allow_html=True)
        orden_sensores = st.selectbox(
            "Orden de lectura de sensores",
            ["asc", "des"],
            format_func=lambda x: "Ascendente (Sensor 1 → 12)" if x == "asc" else "Descendente (Sensor 12 → 1)",
            help="Ascendente: Sensor 1 abajo, 12 arriba. Descendente: Sensor 12 abajo, 1 arriba."
        )

        sensor_referencia = st.selectbox(
            "Sensor de referencia (Toma 12)",
            [f"Sensor {i}" for i in range(1, 37)],
            index=11,
            help="Sensor físico conectado a la toma número 12."
        )

        c1, c2 = st.columns(2)
        with c1:
            distancia_toma_12 = st.number_input(
                "Distancia Toma 12 [mm]",
                value=-120.0, step=1.0, format="%.1f",
                help="Posición relativa al cero del traverser."
            )
        with c2:
            distancia_entre_tomas = st.number_input(
                "Sep. entre tomas [mm]",
                value=10.91, step=0.01, format="%.2f",
                help="Distancia física entre centros de tomas."
            )

        if st.button("💾 CONFIRMAR CONFIGURACIÓN", type="primary", use_container_width=True):
            st.session_state.configuracion_inicial = {
                'orden': orden_sensores,
                'sensor_referencia': sensor_referencia,
                'distancia_toma_12': distancia_toma_12,
                'distancia_entre_tomas': distancia_entre_tomas
            }
            st.success("Configuración aplicada.")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col_ref:
        st.markdown("""
        <div style="background: #111; border: 1px dashed #444; border-radius: 8px; padding: 1rem; text-align: center; height: 100%;">
            <p style="color: #888; font-size: 0.8rem; margin-bottom: 10px;">REFERENCIA TÉCNICA</p>
            <img src="https://raw.githubusercontent.com/Juan-Cruz-de-la-Fuente/Laboratorio/main/Peine.jpg" 
                 style="max-width: 100%; border-radius: 4px; opacity: 0.8;">
        </div>
        """, unsafe_allow_html=True)

    # Paso 2: Carga de archivos
    # --- PASO 2: CARGA Y PROCESAMIENTO ---
    if st.session_state.configuracion_inicial:
        st.markdown("---")
        st.markdown("""
        <div class="section-card" style="margin-bottom: 20px;">
            <h3 style="margin-top: 0; color: white;">📁 PASO 2: IMPORTACIÓN DE ARCHIVOS CRUDOS</h3>
            <p style="color: #bbb; margin-bottom: 20px;">Cargue los archivos CSV de incertidumbre generados por el sistema de adquisición.</p>
        </div>
        """, unsafe_allow_html=True)

        uploaded_files = st.file_uploader(
            "Arrastre sus archivos CSV aquí",
            type=['csv'],
            accept_multiple_files=True,
            key="uploader_betz2d"
        )

        if uploaded_files:
            st.session_state.uploaded_files_betz2d = uploaded_files
        else:
            uploaded_files = st.session_state.uploaded_files_betz2d

        # Procesamiento y Generación de Salidas
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} archivos cargados en memoria.")
            
            # Contenedor de procesados
            st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
            
            for archivo in uploaded_files:
                if archivo.name not in st.session_state.datos_procesados_betz2d:
                    with st.spinner(f"🔨 Procesando {archivo.name}..."):
                        datos = procesar_promedios(archivo, st.session_state.configuracion_inicial['orden'])
                        if datos is not None:
                            st.session_state.datos_procesados_betz2d[archivo.name] = datos
                            st.session_state.datos_procesados[archivo.name] = datos
                            
                            sub_archivos = crear_archivos_individuales_por_tiempo_y_posicion(datos, archivo.name)
                            if 'sub_archivos_generados' not in st.session_state:
                                st.session_state.sub_archivos_generados = {}
                            st.session_state.sub_archivos_generados.update(sub_archivos)
                
                # Mostrar tarjeta de archivo procesado con descargas rápidas
                if archivo.name in st.session_state.datos_procesados_betz2d:
                    datos = st.session_state.datos_procesados_betz2d[archivo.name]
                    nombre_base = extraer_nombre_base_archivo(archivo.name)
                    
                    with st.expander(f"✅ {archivo.name} (Procesado)", expanded=False):
                        c_d1, c_d2, c_d3 = st.columns(3)
                        
                        # Preparar datos
                        datos_ordenados_nombre = datos.sort_values("Archivo")
                        datos_ordenados_x = datos.sort_values("Pos_Y_Traverser")
                        datos_ordenados_tiempo = datos.sort_values("Tiempo_s")
                        
                        with c_d1:
                             csv_pk = datos_ordenados_nombre.to_csv(sep=';', index=False, decimal=',').encode('utf-8-sig')
                             st.download_button("📥 Ord. por Nombre", csv_pk, f"{nombre_base}_nombre.csv", "text/csv", key=f"dn_{nombre_base}")
                        with c_d2:
                             csv_x = datos_ordenados_x.to_csv(sep=';', index=False, decimal=',').encode('utf-8-sig')
                             st.download_button("📥 Ord. por Posición X", csv_x, f"{nombre_base}_x.csv", "text/csv", key=f"dx_{nombre_base}")
                        with c_d3:
                             csv_t = datos_ordenados_tiempo.to_csv(sep=';', index=False, decimal=',').encode('utf-8-sig')
                             st.download_button("📥 Ord. por Tiempo", csv_t, f"{nombre_base}_time.csv", "text/csv", key=f"dt_{nombre_base}")
    else:
        st.info("⚠️ Configure la geometría en el Paso 1 para habilitar la carga de archivos.")


    # Mostrar datos procesados
    if st.session_state.datos_procesados:
        st.markdown("## 📋 Datos Procesados")
        for nombre_archivo, datos in st.session_state.datos_procesados.items():
            with st.expander(f"Ver datos de {nombre_archivo}"):
                st.dataframe(datos, use_container_width=True)
                tiempos_unicos = datos['Tiempo_s'].dropna().unique()
                coordenadas_unicas = datos[['Pos_Y_Traverser', 'Pos_Z_Base']].drop_duplicates()
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Tiempos encontrados:** {sorted(tiempos_unicos)}")
                with col2:
                    st.markdown("**Coordenadas encontradas:**")
                    st.dataframe(coordenadas_unicas, use_container_width=True)


    # --- PASO 3: ANÁLISIS DETALLADO ---
    if st.session_state.sub_archivos_generados:
        st.markdown("---")
        st.markdown("""
        <div class="section-card" style="margin-bottom: 20px;">
            <h3 style="margin-top: 0; color: white;">📊 PASO 3: RESUMEN DE SUB-ARCHIVOS</h3>
            <p style="color: #bbb; margin-bottom: 10px;">Gestión de todos los archivos individualizados generados (separados por tiempo y posición).</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Recolectar datos
        filas_resumen = []
        for clave, sub in st.session_state.sub_archivos_generados.items():
            filas_resumen.append({
                'Archivo Fuente': sub.get('archivo_origen', sub.get('archivo_fuente', '-')),
                'Tiempo': f"{sub.get('tiempo')}s",
                'Pos X': sub.get('x_traverser'),
                'Registros': len(sub.get('datos', [])),
                'Nombre Salida': sub.get('nombre_archivo', ''),
                'Clave': clave
            })
        
        df_resumen = pd.DataFrame(filas_resumen)
        
        # Métricas
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.markdown(f"<div style='text-align:center; padding:10px; background:#111; border-radius:8px; border:1px solid #333;'><h2 style='margin:0; color:#3b82f6;'>{len(df_resumen)}</h2><p style='margin:0; color:#888;'>Sub-archivos Generados</p></div>", unsafe_allow_html=True)
        with col_m2:
            st.markdown(f"<div style='text-align:center; padding:10px; background:#111; border-radius:8px; border:1px solid #333;'><h2 style='margin:0; color:#10b981;'>{df_resumen['Archivo Fuente'].nunique()}</h2><p style='margin:0; color:#888;'>Archivos Fuente</p></div>", unsafe_allow_html=True)
        with col_m3:
            st.markdown(f"<div style='text-align:center; padding:10px; background:#111; border-radius:8px; border:1px solid #333;'><h2 style='margin:0; color:#8b5cf6;'>{df_resumen['Registros'].sum()}</h2><p style='margin:0; color:#888;'>Total Registros</p></div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.dataframe(
            df_resumen[['Archivo Fuente', 'Tiempo', 'Pos X', 'Registros', 'Nombre Salida']], 
            use_container_width=True,
            height=300
        )

        st.markdown("---")

        # --- 4) Agrupar por archivo origen para mostrar expanders ---
        grouped = {}
        for _, row in df_resumen.iterrows():
            archivo = row['Archivo Fuente']
            tiempo = row['Tiempo']
            grouped.setdefault(archivo, {}).setdefault(tiempo, []).append(row.to_dict())

        # Mostrar 1 expander por archivo origen
        for archivo_origen, tiempos_dict in grouped.items():
            num_tiempos = len(tiempos_dict)
            with st.expander(f"📁 {archivo_origen} - {num_tiempos} tiempos", expanded=False):
                # Generar ZIP con todos los sub-archivos de este origen (para descargar de una)
                # Crearlo aquí en memoria y mostrar botón
                buffer = io.BytesIO()
                with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                    for tiempo, items in tiempos_dict.items():
                        for it in items:
                            clave = it['Clave']
                            df_sub = st.session_state.sub_archivos_generados[clave]['datos']
                            csv_bytes = df_sub.to_csv(sep=';', index=False, decimal=',').encode('utf-8-sig')
                            zf.writestr(it['Nombre Salida'], csv_bytes)
                zip_bytes = buffer.getvalue()
                st.download_button(
                    label=f"📦 Descargar TODOS los sub-archivos ({archivo_origen}) .zip",
                    data=zip_bytes,
                    file_name=f"{archivo_origen}_subarchivos_{datetime.now().strftime('%Y%m%d')}.zip",
                    mime="application/zip",
                    key=f"zip_{archivo_origen}_{datetime.now().timestamp()}"
                )

                st.markdown("")

                # Para cada tiempo, listar sub-archivos (X) y dar botón CSV por cada uno
                for tiempo, items in sorted(tiempos_dict.items()):
                    st.markdown(f"#### ⏱️ {tiempo}")
                    for it in sorted(items, key=lambda r: (r['Pos X'] if pd.notna(r['Pos X']) else 1e9)):
                        clave = it['Clave']
                        nombre = it['Nombre Salida']
                        registros = it['Registros']
                        pos_x = it['Pos X']

                        col_a, col_b, col_c = st.columns([4, 1, 2])
                        col_a.markdown(f"**X{pos_x}** — `{nombre}`")
                        col_b.markdown(f"Registros: {registros}")

                        # generar bytes CSV para el botón
                        df_sub = st.session_state.sub_archivos_generados[clave]['datos']
                        csv_bytes = df_sub.to_csv(sep=';', index=False, decimal=',').encode('utf-8-sig')

                        # key única por descarga (clave ya debería ser única)
                        dl_key = f"dl_{clave}_{datetime.now().timestamp()}"
                        col_c.download_button(
                            label="📥 Descargar CSV",
                            data=csv_bytes,
                            file_name=nombre,
                            mime="text/csv",
                            key=dl_key,
                            use_container_width=True
                        )

                    st.markdown("---")
    else:
        st.info("No hay sub-archivos generados aún. Subí y procesá archivos en Paso 2.")

    # --- PASO 5: GUARDAR EN DRIVE (1D) ---
    if st.session_state.sub_archivos_generados:
        st.markdown("---")
        st.markdown("""
        <div class="section-card" style="margin-bottom: 20px;">
            <h3 style="margin-top: 0; color: white;">&#x2601;&#xFE0F; PASO 5: GUARDAR EN DRIVE (1D)</h3>
            <p style="color: #bbb; margin-bottom: 0;">Sube un sub-archivo procesado directamente a la carpeta <b>ENSAYO DE ESTELA / 1D</b> de tu Drive.</p>
        </div>
        """, unsafe_allow_html=True)

        opciones_1d = list(st.session_state.sub_archivos_generados.keys())
        clave_sel_1d = st.selectbox("Seleccionar sub-archivo para subir:", opciones_1d, key="sel_drive_1d")

        if clave_sel_1d:
            sub_sel = st.session_state.sub_archivos_generados[clave_sel_1d]
            df_sub_sel = sub_sel['datos']
            nombre_sub_sel = sub_sel.get('nombre_archivo', f"{clave_sel_1d}.csv")
            csv_bytes_1d = df_sub_sel.to_csv(sep=';', index=False, decimal=',').encode('utf-8-sig')

            col_1d_dl, col_1d_drive = st.columns(2)
            with col_1d_dl:
                st.download_button("&#x1F4E5; Descargar CSV", csv_bytes_1d,
                                   file_name=nombre_sub_sel, mime="text/csv", key="dl_1d_final")
            with col_1d_drive:
                if st.button("&#x2601;&#xFE0F; Guardar en Drive (1D)", key="save_1d_drive", use_container_width=True):
                    if auth.save_csv_1d(st.session_state.username, nombre_sub_sel, csv_bytes_1d):
                        st.success(f"✅ Subido a Drive → ENSAYO DE ESTELA/1D/{nombre_sub_sel}")
                    else:
                        st.error("Error al subir a Drive")

    # Paso 4: Sección de Gráficos
    st.markdown("## 📈 Paso 4: Sección de Gráficos")

    if st.session_state.datos_procesados:
        # Tomar el primer DataFrame procesado para obtener n_sensores
        primer_df = next(iter(st.session_state.datos_procesados.values()))
        n_sensores_detectados = primer_df.attrs.get("n_sensores", 12)

        posiciones_sensores = calcular_posiciones_sensores(
            st.session_state.configuracion_inicial['distancia_toma_12'],
            st.session_state.configuracion_inicial['distancia_entre_tomas'],
            n_sensores_detectados,
            st.session_state.configuracion_inicial['orden']
        )

        # Mostrar tabla de posiciones
        with st.expander("Ver posiciones calculadas de sensores"):
            pos_df = pd.DataFrame([
                {
                    'Sensor': sensor,
                    'Posición Y [mm]': pos['y'],
                    'Sensor Físico': pos['sensor_fisico']
                }
                for sensor, pos in posiciones_sensores.items()
            ])
            st.dataframe(pos_df, use_container_width=True)
    else:
        st.warning("⚠️ No hay datos procesados aún. Suba archivos en el Paso 2.")


    # Contenedor para los filtros de visualización
    with st.container(border=True):
        st.markdown("#### 🔍 Filtros de Visualización")
        
        sub_archivos = st.session_state.sub_archivos_generados.values()
        archivos_opciones = sorted(list(set(sa['archivo_fuente'] for sa in sub_archivos)))
        x_opciones = sorted(list(set(sa['x_traverser'] for sa in sub_archivos)))
        tiempo_opciones = sorted(list(set(sa['tiempo'] for sa in sub_archivos)))

        col1, col2, col3 = st.columns(3)
        archivos_seleccionados = col1.multiselect(
            "Filtrar por Archivo Origen:",
            options=archivos_opciones,
            default=archivos_opciones,
            key="filtro_archivos_origen"
        )
        x_seleccionados = col2.multiselect(
            "Filtrar por Posición X:",
            options=x_opciones,
            default=x_opciones,
            key="filtro_posicion_x"
        )
        tiempos_seleccionados = col3.multiselect(
            "Filtrar por Tiempo (s):",
            options=tiempo_opciones,
            default=tiempo_opciones,
            key="filtro_tiempo_s"
        )

    # Filtrar sub-archivos según filtros seleccionados
    sub_archivos_filtrados = {
        clave: sub_archivo for clave, sub_archivo in st.session_state.sub_archivos_generados.items()
        if sub_archivo['archivo_fuente'] in archivos_seleccionados
        and sub_archivo['x_traverser'] in x_seleccionados
        and sub_archivo['tiempo'] in tiempos_seleccionados
    }

    # Selección de sub-archivos para gráfico concatenado
    st.markdown("### 🎯 Selección de Sub-archivos para Gráfico Concatenado")

    if not sub_archivos_filtrados:
        st.warning("No hay datos que coincidan con los filtros seleccionados.")
    else:
        sub_archivos_seleccionados = {}

        # Generar color único aleatorio para cada sub-archivo
            # Inicializar colores persistentes en la sesión
        if "colores_por_subarchivo" not in st.session_state:
            st.session_state.colores_por_subarchivo = {}

        # Asignar color solo a los sub-archivos que no tengan uno
        for clave in sub_archivos_filtrados.keys():
            if clave not in st.session_state.colores_por_subarchivo:
                st.session_state.colores_por_subarchivo[clave] = "#{:06x}".format(random.randint(0, 0xFFFFFF))

        colores_por_subarchivo = st.session_state.colores_por_subarchivo

        # Mostrar lista de selección con colores
        for i, (clave, sub_archivo) in enumerate(sorted(sub_archivos_filtrados.items())):
            col1, col2 = st.columns([3, 1])
            label = f"{sub_archivo['archivo_fuente']} - T{sub_archivo['tiempo']}s - X{sub_archivo['x_traverser']} - {len(sub_archivo['datos'])} registros"
            
            if col1.checkbox(label, key=f"incluir_{clave}_{i}"):
                sub_archivos_seleccionados[clave] = sub_archivo
            
            with col2:
                color_sub = colores_por_subarchivo[clave]
                st.markdown(
                    f'<div style="background: {color_sub}; height: 20px; width: 60px; border-radius: 3px; margin-top: 8px;"></div>',
                    unsafe_allow_html=True
                )

        # Generar gráfico concatenado si hay selecciones
        if sub_archivos_seleccionados:
            st.markdown("### 📊 Gráfico Concatenado Vertical Modo Betz")

            fig = go.Figure()
            for clave, sub_archivo in sub_archivos_seleccionados.items():
                color = colores_por_subarchivo[clave]
                z_datos, presion_datos = extraer_datos_para_grafico(sub_archivo, st.session_state.configuracion_inicial)
                if z_datos and presion_datos:
                    fig.add_trace(go.Scatter(
                        x=presion_datos,
                        y=z_datos,
                        mode='lines',
                        name=clave,
                        line=dict(color=color, width=2),
                        fill='tozerox',
                        opacity=0.7
                    ))

            fig.update_layout(
                title="Perfil de Presión Concatenado",
                xaxis_title="Presión Total [Pa]",
                yaxis_title="Altura Z [mm]",
                plot_bgcolor='rgba(0,0,0,0)',   # transparente en área del gráfico
                paper_bgcolor='rgba(0,0,0,0)',  # transparente en todo el lienzo
                font=dict(color='white'),       # texto en blanco para que se lea bien
                height=900,
                width=1600
            )
            st.plotly_chart(fig, use_container_width=False)

            total_puntos = len(sub_archivos_seleccionados) * 12
            st.success(f"✅ Gráfico vertical generado con {total_puntos} puntos de datos concatenados")

            # Exportaciones
            st.markdown("### 📤 Exportación")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                html_string = fig.to_html()
                st.download_button(
                    label="📊 Descargar Gráfico (HTML)",
                    data=html_string,
                    file_name=f"grafico_betz_vertical_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                    mime="text/html"
                )

            with col2:
                datos_exportar = []
                for clave, sub_archivo in sub_archivos_seleccionados.items():
                    datos_sub = sub_archivo['datos'].copy()
                    datos_sub['Sub_archivo'] = clave
                    datos_exportar.append(datos_sub)
                
                df_exportar = pd.concat(datos_exportar, ignore_index=True)
                csv_data = df_exportar.to_csv(
                    index=False, sep=';', encoding='utf-8-sig', decimal=','
                )
                st.download_button(
                    label="📋 Descargar Datos (CSV)",
                    data=csv_data,
                    file_name=f"datos_betz_vertical_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

            with col3:
                st.metric("Total de puntos", total_puntos)
        else:
            st.error("❌ No se pudo generar el gráfico. Verifique los datos seleccionados.")

    
        # NUEVA SECCIÓN: RESTA DE ÁREAS
        # NUEVA SECCIÓN: RESTA DE ÁREAS
        if st.session_state.sub_archivos_generados:
            st.markdown("---")
            st.markdown("## ➖ Análisis de Diferencias de Áreas")
            st.markdown("Selecciona dos sub-archivos para calcular la diferencia de áreas entre sus perfiles de presión")
            
            # Crear lista de opciones para los selectores
            opciones_subarchivos = sorted(list(st.session_state.sub_archivos_generados.keys()))
            
            col1, col2, col3 = st.columns([2, 1, 2])
            
            with col1:
                archivo_a = st.selectbox(
                    "📊 Archivo A (minuendo):",
                    opciones_subarchivos,
                    key="archivo_a_resta",
                    help="Seleccione el primer sub-archivo (del cual se restará el segundo)"
                )
            
            with col2:
                st.markdown("<div style='text-align: center; font-size: 2rem; margin-top: 2rem;'>➖</div>", unsafe_allow_html=True)
            
            with col3:
                archivo_b = st.selectbox(
                    "📊 Archivo B (sustraendo):",
                    opciones_subarchivos,
                    index=1 if len(opciones_subarchivos) > 1 else 0,
                    key="archivo_b_resta",
                    help="Seleccione el segundo sub-archivo (que será restado del primero)"
                )
            
            # --- INICIO DE LA ESTRUCTURA CORREGIDA ---

            # PARTE 1: Botón para CALCULAR. Su única misión es generar el gráfico y ponerlo en una "bandeja" temporal.
            if st.button("🔄 Calcular Diferencia de Áreas", type="primary", use_container_width=True):
                if archivo_a and archivo_b and archivo_a != archivo_b:
                    with st.spinner("Calculando diferencia de áreas..."):
                        fig_diferencia, diferencia_area = crear_grafico_diferencia_areas(
                            st.session_state.sub_archivos_generados[archivo_a],
                            st.session_state.sub_archivos_generados[archivo_b],
                            st.session_state.configuracion_inicial
                        )
                        if fig_diferencia:
                            # Guardamos TODO lo necesario en la sesión para mostrarlo después del reinicio de la página.
                            st.session_state.figura_diferencia_temporal = {
                                "fig": fig_diferencia,
                                "nombre": f"Dif. 2D: {archivo_a.split('_')[0]} vs {archivo_b.split('_')[0]}",
                                "area_diferencia": diferencia_area,
                                "archivo_a": archivo_a,
                                "archivo_b": archivo_b
                            }
                        else:
                            st.error("❌ No se pudo calcular la diferencia.")
                            if 'figura_diferencia_temporal' in st.session_state:
                                del st.session_state.figura_diferencia_temporal
                else:
                    st.warning("⚠️ Seleccione dos sub-archivos diferentes para calcular la diferencia.")

            # PARTE 2: Este bloque está AFUERA del anterior. Revisa si hay algo en la "bandeja" temporal.
            # Si hay algo, lo muestra junto con TODOS sus botones (Guardar, métricas, descarga).
            if 'figura_diferencia_temporal' in st.session_state:
                # Recuperamos los datos de la sesión que guardamos en la PARTE 1
                temp_data = st.session_state.figura_diferencia_temporal
                fig_diferencia = temp_data["fig"]
                nombre_guardado = temp_data["nombre"]
                diferencia_area = temp_data["area_diferencia"]
                archivo_a_calc = temp_data["archivo_a"]
                archivo_b_calc = temp_data["archivo_b"]
                
                # 1. Mostramos el gráfico
                st.plotly_chart(fig_diferencia, use_container_width=False)
                
                # 2. Mostramos el botón de "Guardar". Ahora sí funcionará.
                if st.button("💾 Guardar Diferencia para Visualizar", key="save_diff_2d_for_viz_final"):
                    if 'diferencias_guardadas' not in st.session_state:
                        st.session_state.diferencias_guardadas = {}
                    st.session_state.diferencias_guardadas[nombre_guardado] = fig_diferencia
                    st.success(f"✅ Gráfico '{nombre_guardado}' guardado permanentemente.")
                    # Borramos la figura temporal después de guardarla para limpiar la "bandeja"
                    del st.session_state.figura_diferencia_temporal
                    st.rerun()

                # 3. Mostramos las métricas y el resto de tu código (sin cambios)
                col_m1, col_m2, col_m3 = st.columns(3)
                z_a, p_a = extraer_datos_para_grafico(st.session_state.sub_archivos_generados[archivo_a_calc], st.session_state.configuracion_inicial)
                z_b, p_b = extraer_datos_para_grafico(st.session_state.sub_archivos_generados[archivo_b_calc], st.session_state.configuracion_inicial)
                area_a = calcular_area_bajo_curva(z_a, p_a)
                area_b = calcular_area_bajo_curva(z_b, p_b)
                
                with col_m1:
                    st.metric(f"Área {st.session_state.sub_archivos_generados[archivo_a_calc]['archivo_fuente']}", f"{area_a:.2f} Pa·mm")
                with col_m2:
                    st.metric(f"Área {st.session_state.sub_archivos_generados[archivo_b_calc]['archivo_fuente']}", f"{area_b:.2f} Pa·mm")
                with col_m3:
                    st.metric("Diferencia de Áreas", f"{diferencia_area:.2f} Pa·mm", delta=f"{diferencia_area:.2f}", delta_color="normal" if diferencia_area >= 0 else "inverse")
                
                if diferencia_area > 0:
                    st.success(f"✅ El área de **{st.session_state.sub_archivos_generados[archivo_a_calc]['archivo_fuente']}** es **{diferencia_area:.2f} Pa·mm** mayor que la de **{st.session_state.sub_archivos_generados[archivo_b_calc]['archivo_fuente']}**")
                elif diferencia_area < 0:
                    st.info(f"ℹ️ El área de **{st.session_state.sub_archivos_generados[archivo_b_calc]['archivo_fuente']}** es **{abs(diferencia_area):.2f} Pa·mm** mayor que la de **{st.session_state.sub_archivos_generados[archivo_a_calc]['archivo_fuente']}**")
                else:
                    st.info("ℹ️ Las áreas son prácticamente iguales")
                
                html_diferencia = fig_diferencia.to_html()
                st.download_button(
                    label="📊 Descargar Gráfico de Diferencia (HTML)",
                    data=html_diferencia,
                    file_name=f"diferencia_areas_{archivo_a_calc}_vs_{archivo_b_calc}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                    mime="text/html"
                )

elif st.session_state.seccion_actual == 'vis_2d_nueva':
    st.markdown("""
        <div class="header-container">
            <h1 style="font-size: 3rem; margin-bottom: 1rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
            📈 VISUALIZACIÓN DE ESTELA 2D
            </h1>
            <h2 style="font-size: 1.8rem; margin-bottom: 0; opacity: 0.9;">
            Mapeo de Campos de Presión Interactivo
            </h2>
        </div>
    """, unsafe_allow_html=True)

    # --- PASO 1: CONFIGURACIÓN INICIAL ---
    st.markdown("## ⚙️ Paso 1: Configuración Inicial")
    col_config, col_ref = st.columns([2, 1])
    
    with col_config:
        st.markdown("<div style='padding: 1rem; border: 1px solid #333; border-radius: 8px; background-color: #000;'>", unsafe_allow_html=True)
        orden_sensores = st.selectbox(
            "Orden de lectura de sensores",
            ["asc", "des"],
            format_func=lambda x: "Ascendente (Sensor 1 → 12)" if x == "asc" else "Descendente (Sensor 12 → 1)",
            key="orden_2d"
        )

        sensor_referencia = st.selectbox(
            "Sensor de referencia (Toma 12)",
            [f"Sensor {i}" for i in range(1, 37)],
            index=11, key="sensor_ref_2d"
        )

        c1, c2 = st.columns(2)
        with c1:
            distancia_toma_12 = st.number_input("Distancia Toma 12 [mm]", value=-120.0, step=1.0, format="%.1f", key="dist_12_2d")
        with c2:
            distancia_entre_tomas = st.number_input("Sep. entre tomas [mm]", value=10.91, step=0.01, format="%.2f", key="dist_entre_2d")

        if st.button("💾 CONFIRMAR CONFIGURACIÓN", type="primary", use_container_width=True, key="btn_conf_2d"):
            st.session_state.configuracion_2d = {
                'orden': orden_sensores,
                'sensor_referencia': sensor_referencia,
                'distancia_toma_12': distancia_toma_12,
                'distancia_entre_tomas': distancia_entre_tomas
            }
            st.success("Configuración aplicada para el entorno 2D.")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col_ref:
        st.markdown("""
        <div style="background: #111; border: 1px dashed #444; border-radius: 8px; padding: 1rem; text-align: center; height: 100%;">
            <p style="color: #888; font-size: 0.8rem; margin-bottom: 10px;">REFERENCIA TÉCNICA</p>
            <img src="https://raw.githubusercontent.com/Juan-Cruz-de-la-Fuente/Laboratorio/main/Peine.jpg" 
                 style="max-width: 100%; border-radius: 4px; opacity: 0.8;">
        </div>
        """, unsafe_allow_html=True)


    # --- PASO 2: IMPORTACIÓN DE ARCHIVOS ---
    if st.session_state.get('configuracion_2d'):
        st.markdown("---")
        st.markdown("""
        <div class="section-card" style="margin-bottom: 20px;">
            <h3 style="margin-top: 0; color: white;">📁 PASO 2: IMPORTACIÓN DE ARCHIVOS CRUDOS</h3>
            <p style="color: #bbb; margin-bottom: 20px;">Cargue uno o múltiples archivos CSV crudos de ensayo para generar los planos espaciales en 2D.</p>
        </div>
        """, unsafe_allow_html=True)

        if 'archivos_2d_cargados' not in st.session_state:
            st.session_state.archivos_2d_cargados = {}

        uploaded_files_2d = st.file_uploader("Arrastre sus archivos CSV de Incertidumbre aquí", type=['csv'], accept_multiple_files=True, key="uploader_2d")
        
        if uploaded_files_2d:
            st.markdown("<br>", unsafe_allow_html=True)
            for file_2d in uploaded_files_2d:
                nombre_archivo = file_2d.name.replace('.csv', '').replace('incertidumbre_', '')
                if nombre_archivo not in st.session_state.archivos_2d_cargados:
                    with st.spinner(f"🔨 Procesando archivo {nombre_archivo}..."):
                        datos_procesados = procesar_promedios(file_2d, st.session_state.configuracion_2d['orden'])
                        if datos_procesados is not None:
                            st.session_state.archivos_2d_cargados[nombre_archivo] = datos_procesados
                            st.success(f"✅ Archivo extraído correctamente: {nombre_archivo}")
                            
        # Mostrar resumen interactivo de archivos con Progress list (como en 3D)
        if st.session_state.archivos_2d_cargados:
            st.markdown("### 📋 Archivos en Memoria")
            cols = st.columns(3)
            for idx, (nombre, datos) in enumerate(st.session_state.archivos_2d_cargados.items()):
                with cols[idx % 3]:
                    with st.container(border=True):
                        st.markdown(f"**📦 {nombre}**")
                        st.caption(f"{len(datos)} Puntos medidos • {len(datos['Tiempo_s'].unique())} Tiempos discretos")
                        st.progress(100)

            # --- PASO 3: VISUALIZADOR INTERACTIVO ---
            st.markdown("---")
            st.markdown("""
            <div class="section-card" style="margin-bottom: 20px;">
                <h3 style="margin-top: 0; color: white;">📈 PASO 3: VISUALIZADOR 2D INTERACTIVO</h3>
                <p style="color: #bbb; margin-bottom: 20px;">Explore el plano de presiones seleccionando archivo y escala, interactuando nativamente con las herramientas del trazado (regla configurable).</p>
            </div>
            """, unsafe_allow_html=True)
            
            c_cfg, c_plot = st.columns([1, 2.5])
            with c_cfg:
                st.markdown("### 1. Parámetros de Escala")
                cuerda_mm = st.number_input("Cuerda Referencia [mm]", value=300.0, step=1.0)
                
                st.markdown("### 2. Selección de Plano")
                archivo_sel = st.selectbox("Seleccionar Archivo (X):", list(st.session_state.archivos_2d_cargados.keys()))
                
                df_selected = st.session_state.archivos_2d_cargados[archivo_sel]
                tiempos = df_selected['Tiempo_s'].dropna().unique()
                tiempo_sel = st.selectbox("Seleccionar Tiempo:", sorted(tiempos))

                st.markdown("### 3. Visualización")
                plot_type = st.selectbox("Render de Pixeles:", ["Contour Suavizado", "Mapa de Calor (Celdas)"])

                st.markdown("---")
                st.markdown("### 📏 Medición de Trazos")
                st.info("La Regla ↘️ del gráfico mide nativamente en [mm]. Ingresa aquí el trazo medido para convertir a [c]:")
                long_leida = st.number_input("Longitud Leída [mm]:", value=0.0, step=1.0)
                if long_leida > 0:
                    st.success(f"**Longitud Equiv:** {(long_leida / cuerda_mm):.3f} c")

            with c_plot:
                with st.spinner("Ensamblando proyección de contornos 2D..."):
                    df_run = df_selected[df_selected['Tiempo_s'] == tiempo_sel].copy()
                    
                    results_2d = []
                    # Ensamblar la Matriz 2D extrayendo las posiciones absolutas
                    for _, row in df_run.iterrows():
                        y_trav = row.get('Pos_Y_Traverser')
                        z_base = row.get('Pos_Z_Base')
                        for col in df_run.columns:
                            num_sensor = obtener_numero_sensor_desde_columna(col)
                            if num_sensor is not None:
                                val_presion = row[col]
                                if pd.isna(val_presion): continue
                                z_real = calcular_altura_absoluta_z(
                                    num_sensor, z_base, 
                                    st.session_state.configuracion_2d.get('distancia_toma_12', -120),
                                    st.session_state.configuracion_2d.get('distancia_entre_tomas', 10.91),
                                    12, st.session_state.configuracion_2d.get('orden', 'asc')
                                )
                                results_2d.append({'Y': y_trav, 'Z': z_real, 'Presion': val_presion})
                                
                    df_matriz = pd.DataFrame(results_2d)
                    
                    if df_matriz.empty:
                        st.error("❌ No se pudieron extraer datos espaciales (Y, Z, P). Comprueba tu archivo físico.")
                    else:
                        y_plot = df_matriz['Y'].values
                        z_plot = df_matriz['Z'].values
                        val_plot = df_matriz['Presion'].values
                        eje_label = "mm"
                        z_title = "P [Pa]"
                        cs_name = "Jet"

                        # Create Grid Interpolation cubic 150x150 res
                        y_grid_vals = np.linspace(y_plot.min(), y_plot.max(), 150)
                        z_grid_vals = np.linspace(z_plot.min(), z_plot.max(), 150)
                        Y_grid, Z_grid = np.meshgrid(y_grid_vals, z_grid_vals)
                        
                        try:
                            V_grid = griddata((y_plot, z_plot), val_plot, (Y_grid, Z_grid), method='cubic')
                            fig = go.Figure()
                            
                            if plot_type == "Contour Suavizado":
                                fig.add_trace(go.Contour(
                                    x=y_grid_vals, y=z_grid_vals, z=V_grid,
                                    colorscale=cs_name, colorbar=dict(title=z_title),
                                    contours=dict(showlines=False)
                                ))
                            else:
                                fig.add_trace(go.Heatmap(
                                    x=y_grid_vals, y=z_grid_vals, z=V_grid,
                                    colorscale=cs_name, colorbar=dict(title=z_title)
                                ))

                            fig.update_layout(
                                title=dict(text=f"Proyección Espacial 2D: Presión [Pa]", font=dict(size=20, color="white")),
                                xaxis_title=dict(text=f"Envergadura (Y) [{eje_label}]", font=dict(color="white")),
                                yaxis_title=dict(text=f"Altura (Z) [{eje_label}]", font=dict(color="white")),
                                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                font=dict(color="white"),
                                dragmode="drawline",
                                newshape=dict(line_color="magenta", line_width=3, opacity=1.0),
                                margin=dict(l=60, r=60, t=60, b=60),
                                height=800
                            )
                            # Ancla física de ejes. Garantiza que la matriz mida proporcionalmente 1:1 en la pantalla
                            fig.update_xaxes(scaleanchor="y", scaleratio=1, showgrid=True, gridcolor="rgba(255,255,255,0.1)")
                            fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.1)")

                            st.plotly_chart(fig, use_container_width=True, config={
                                'modeBarButtonsToAdd': ['drawline', 'drawcircle', 'eraseshape'],
                                'displaylogo': False, 'scrollZoom': True
                            })
                            st.info("💡 **Gráfico Físico Proporcional:** Los ejes representan dimensiones nativas (1 pixel unitario X = 1 pixel unitario Y). Usa la mini-calculadora de la izquierda para convertir tu medición `drawline` directamente a tamaño de Escala Cuerda [c] de la aeronave.")
                        except Exception as e:
                            st.error(f"Error trazando proyecciones cúbicas: {e}")

            # --- GUARDAR MATRIZ 2D EN DRIVE ---
            st.markdown("---")
            st.markdown("""
            <div class="section-card" style="margin-bottom: 20px;">
                <h3 style="margin-top: 0; color: white;">&#x2601;&#xFE0F; PASO 4: GUARDAR MATRIZ EN DRIVE (2D)</h3>
                <p style="color: #bbb; margin-bottom: 0;">Guarda la matriz de presiones del plano seleccionado en <b>ENSAYO DE ESTELA / 2D</b>.</p>
            </div>
            """, unsafe_allow_html=True)
            if not df_matriz.empty:
                nombre_csv_2d = f"{archivo_sel}_T{tiempo_sel}s_2D.csv"
                csv_bytes_2d = df_matriz.to_csv(sep=';', index=False, decimal=',').encode('utf-8-sig')
                col_2d_dl, col_2d_drive = st.columns(2)
                with col_2d_dl:
                    st.download_button("&#x1F4E5; Descargar Matriz 2D", csv_bytes_2d,
                                       file_name=nombre_csv_2d, mime="text/csv", key="dl_2d_matriz")
                with col_2d_drive:
                    if st.button("&#x2601;&#xFE0F; Guardar en Drive (2D)", key="save_2d_drive", use_container_width=True):
                        if auth.save_csv_2d(st.session_state.username, nombre_csv_2d, csv_bytes_2d):
                            st.success(f"✅ Subido a Drive → ENSAYO DE ESTELA/2D/{nombre_csv_2d}")
                        else:
                            st.error("Error al subir a Drive")

elif st.session_state.seccion_actual == 'ensayo_betz':
    st.markdown("""
        <div class="header-container">
            <h1 style="font-size: 3rem; margin-bottom: 1rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
            🧪 ENSAYO DE BETZ
            </h1>
            <h2 style="font-size: 1.8rem; margin-bottom: 0; opacity: 0.9;">
            Sección en desarrollo
            </h2>
        </div>
    """, unsafe_allow_html=True)
    st.info("Esta sección se encuentra actualmente en desarrollo y no contiene funcionalidades activas por el momento.")

elif st.session_state.seccion_actual == 'modelos':
    st.markdown("""
    <div class="header-container">
        <h1 style="font-size: 3rem; margin-bottom: 1rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
            📦 GESTOR DE OBJETOS DE REFERENCIA
        </h1>
        <h2 style="font-size: 1.8rem; margin-bottom: 0; opacity: 0.9;">
            Configura modelos 3D para visualizar junto a las estelas en 4D
        </h2>
    </div>
    """, unsafe_allow_html=True)

    c_conf, c_preview = st.columns([1.2, 2])
    
    # --- MODIFICACIÓN ACTIVA (FUERA DE TABS) ---
    if 'objeto_referencia_4d' in st.session_state and 'transform_active' not in st.session_state:
         # Init si existe objeto pero no transformState (recuperación de error/estado previo)
         st.session_state.transform_active = {'dx': 0.0, 'dy': 0.0, 'dz': 0.0, 'rx': 0.0, 'ry': 0.0, 'rz': 0.0}
         # Si no existe base, crearla desde el actual (asumiendo que es el base)
         if 'objeto_referencia_base' not in st.session_state:
             st.session_state.objeto_referencia_base = st.session_state.objeto_referencia_4d.copy()

    with c_conf:
        # SECCION DE MODIFICACION ACTIVA
        if 'objeto_referencia_4d' in st.session_state:
            with st.expander("🛠️ Modificar Transformación (Objeto Actual)", expanded=True):
                st.info("Ajusta la posición y rotación del objeto cargado en tiempo real.")
                
                # Callback function to apply transform
                def apply_transform():
                    base = st.session_state.objeto_referencia_base
                    t = st.session_state.transform_active
                    
                    # 1. Recuperar base
                    x, y, z = base['x'].copy(), base['y'].copy(), base['z'].copy()
                    
                    # 2. Rotar
                    if t['rx'] != 0 or t['ry'] != 0 or t['rz'] != 0:
                        x, y, z = rotate_points(x, y, z, t['rx'], t['ry'], t['rz'])
                    
                    # 3. Trasladar
                    x = x + t['dx']
                    y = y + t['dy']
                    z = z + t['dz']
                    
                    # 4. Actualizar objeto activo
                    updated_obj = base.copy()
                    updated_obj['x'] = x
                    updated_obj['y'] = y
                    updated_obj['z'] = z
                    st.session_state.objeto_referencia_4d = updated_obj

                # Controls binded to session_state dictionary
                c_t1, c_t2, c_t3 = st.columns(3)
                st.session_state.transform_active['dx'] = c_t1.number_input("dX", value=0.0, step=10.0, key="t_dx", on_change=apply_transform)
                st.session_state.transform_active['dy'] = c_t2.number_input("dY", value=0.0, step=10.0, key="t_dy", on_change=apply_transform)
                st.session_state.transform_active['dz'] = c_t3.number_input("dZ", value=0.0, step=10.0, key="t_dz", on_change=apply_transform)
                
                c_r1, c_r2, c_r3 = st.columns(3)
                st.session_state.transform_active['rx'] = c_r1.number_input("Rot X", value=0.0, step=90.0, key="t_rx", on_change=apply_transform)
                st.session_state.transform_active['ry'] = c_r2.number_input("Rot Y", value=0.0, step=90.0, key="t_ry", on_change=apply_transform)
                st.session_state.transform_active['rz'] = c_r3.number_input("Rot Z", value=0.0, step=90.0, key="t_rz", on_change=apply_transform)

        st.markdown("### ⚙️ Configuración")
        tab_gen, tab_imp, tab_load, tab_save = st.tabs(["📦 Generar Bloque", "📂 Importar Archivo", "📂 Cargar Guardado", "💾 Guardar Actual"])
        
        # --- GENERADOR DE BLOQUE ---
        with tab_gen:
            c1, c2, c3 = st.columns(3)
            p_width = c1.number_input("Ancho Y [mm]:", value=500.0, step=10.0, key="obj_w")
            p_height = c2.number_input("Alto Z [mm]:", value=20.0, step=10.0, key="obj_h")
            p_length = c3.number_input("Largo X [mm]:", value=20.0, step=10.0, key="obj_l")
            
            c4, c5, c6 = st.columns(3)
            p_x_pos = c4.number_input("Posición X (Frente) [mm]:", value=0.0, step=10.0, key="obj_x")
            
            # Helper para centrado automático
            use_auto_center = st.checkbox("📍 Calcular Centro Automáticamente (Dimensiones Túnel)", value=False)
            
            if use_auto_center:
                c_auto1, c_auto2 = st.columns(2)
                tunnel_w = c_auto1.number_input("Ancho Total Túnel/Plano [mm]:", value=760.0, step=10.0)
                tunnel_h = c_auto2.number_input("Alto Total Túnel/Plano [mm]:", value=860.0, step=10.0)
                
                # Calcular centros atomáticamente
                val_y_center = tunnel_w / 2
                val_z_center = tunnel_h / 2
                st.info(f"💡 Centro Calculado: Y={val_y_center:.1f}, Z={val_z_center:.1f}")
            else:
                val_y_center = 0.0
                val_z_center = 10.0

            # Inputs de centro (se actualizan si auto está activo, sino manuales)
            if use_auto_center:
                 p_y_center = c5.number_input("Centro Y [mm]:", value=float(val_y_center), disabled=True, key="obj_yc_auto")
                 p_z_center = c6.number_input("Centro Z [mm]:", value=float(val_z_center), disabled=True, key="obj_zc_auto")
            else:
                 p_y_center = c5.number_input("Centro Y [mm]:", value=0.0, step=10.0, help="Desplazamiento lateral (0 = centrado)", key="obj_yc")
                 p_z_center = c6.number_input("Centro Z [mm]:", value=10.0, step=10.0, help="Altura del centro del objeto", key="obj_zc")
            
            if st.button("Generar Bloque", type="primary", use_container_width=True):
                # Crear malla de cubo (Box)
                x_min, x_max = p_x_pos, p_x_pos + p_length
                
                # Centrado en Y y Z
                y_min = p_y_center - (p_width / 2)
                y_max = p_y_center + (p_width / 2)
                
                z_min = p_z_center - (p_height / 2)
                z_max = p_z_center + (p_height / 2)
                
                # 8 Vértices
                obj_x = [x_min, x_min, x_min, x_min,  x_max, x_max, x_max, x_max]
                obj_y = [y_min, y_max, y_max, y_min,  y_min, y_max, y_max, y_min]
                obj_z = [z_min, z_min, z_max, z_max,  z_min, z_min, z_max, z_max]
                
                # Triángulos (12 caras)
                obj_i = [0, 0,  5, 5,  1, 1,  4, 4,  3, 3,  4, 4]
                obj_j = [1, 2,  4, 7,  5, 6,  0, 3,  2, 6,  5, 1]
                obj_k = [2, 3,  7, 6,  6, 2,  3, 7,  6, 7,  1, 0]
                
                st.session_state.objeto_referencia_4d = {
                    'type': 'mesh',
                    'x': obj_x, 'y': obj_y, 'z': obj_z,
                    'i': obj_i, 'j': obj_j, 'k': obj_k,
                    'name': f'Bloque {int(p_width)}x{int(p_height)}x{int(p_length)}'
                }
                # Guardar BASE y resetear transformaciones
                st.session_state.objeto_referencia_base = st.session_state.objeto_referencia_4d.copy()
                st.session_state.transform_active = {'dx': 0.0, 'dy': 0.0, 'dz': 0.0, 'rx': 0.0, 'ry': 0.0, 'rz': 0.0}
                
                st.success("✅ Bloque generado")

        # --- IMPORTAR CSV/STL ---
        with tab_imp:
            st.markdown("##### 🔧 Configuración de Posicionamiento")
            
            # Controles de Posición (Offsets)
            c_imp1, c_imp2, c_imp3 = st.columns(3)
            imp_off_x = c_imp1.number_input("Posición X (Longitudinal) [mm]", value=0.0, step=10.0, key="imp_off_x")
            imp_off_y = c_imp2.number_input("Posición Y (Transversal) [mm]", value=0.0, step=10.0, key="imp_off_y")
            imp_off_z = c_imp3.number_input("Posición Z (Vertical) [mm]", value=0.0, step=10.0, key="imp_off_z")
            
            st.markdown("##### 🔄 2. Rotación (Grados)")
            c_rot1, c_rot2, c_rot3 = st.columns(3)
            rot_x = c_rot1.number_input("Rotación X", value=0.0, step=90.0, key="rot_x")
            rot_y = c_rot2.number_input("Rotación Y", value=0.0, step=90.0, key="rot_y")
            rot_z = c_rot3.number_input("Rotación Z", value=0.0, step=90.0, key="rot_z")

            # Auto-Centrado
            c_auto_imp1, c_auto_imp2 = st.columns([1, 2])
            use_auto_center_imp = c_auto_imp1.checkbox("📍 Auto-Centrar Objeto Importado", value=True, help="Calcula el centro geométrico del objeto y lo mueve al origen (0,0,0) antes de aplicar los offsets.")
            
            st.divider()
            
            file_obj = st.file_uploader("Cargar Archivo (CSV o STL)", type=['csv', 'stl'])
            
            if file_obj and st.button("📥 Cargar y Procesar Objeto", type="primary", use_container_width=True):
                # Determinar extensión
                file_ext = file_obj.name.split('.')[-1].lower()
                
                x_points, y_points, z_points = None, None, None
                faces_i, faces_j, faces_k = None, None, None
                obj_type = None
                
                try:
                    if file_ext == 'csv':
                        df_obj = pd.read_csv(file_obj, sep=None, engine='python')
                        cols_map = {c.lower(): c for c in df_obj.columns}
                        if 'x' in cols_map and 'y' in cols_map and 'z' in cols_map:
                            # Use correct columns
                            # Check column names carefully as user might upload anything
                            x_points = df_obj[cols_map['x']].values
                            y_points = df_obj[cols_map['y']].values
                            z_points = df_obj[cols_map['z']].values
                            obj_type = 'scatter'
                        else:
                            st.error("El CSV requiere columnas X, Y, Z")
                
                    elif file_ext == 'stl':
                        # PyVista necesita leer de archivo físico, usamos tempfile
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.stl') as tmp:
                            tmp.write(file_obj.getvalue())
                            tmp_path = tmp.name
                        
                        # Leer con PyVista
                        mesh = pv.read(tmp_path)
                        os.unlink(tmp_path) # Limpiar temp
                        
                        # Triangular si es necesario
                        if not mesh.is_all_triangles:
                            mesh = mesh.triangulate()
                            
                        points = mesh.points
                        x_points = points[:, 0]
                        y_points = points[:, 1]
                        z_points = points[:, 2]
                        
                        faces = mesh.faces.reshape(-1, 4)[:, 1:]
                        faces_i = faces[:, 0]
                        faces_j = faces[:, 1]
                        faces_k = faces[:, 2]
                        obj_type = 'mesh'

                    # --- TRANSFORMACIONES ---
                    if x_points is not None:
                        # 1. Auto-Centrado (Llevar Centro Geométrico a 0,0,0)
                        if use_auto_center_imp:
                            cx = (np.min(x_points) + np.max(x_points)) / 2
                            cy = (np.min(y_points) + np.max(y_points)) / 2
                            cz = (np.min(z_points) + np.max(z_points)) / 2
                            
                            x_points = x_points - cx
                            y_points = y_points - cy
                            z_points = z_points - cz

                        # 2. Rotación (Alrededor del centro local 0,0,0)
                        if rot_x != 0 or rot_y != 0 or rot_z != 0:
                            x_points, y_points, z_points = rotate_points(x_points, y_points, z_points, rot_x, rot_y, rot_z)
                        
                        # 3. Aplicar Offsets del Usuario
                        x_points = x_points + imp_off_x
                        y_points = y_points + imp_off_y
                        z_points = z_points + imp_off_z
                        

                        # Guardar en Session State
                        obj_data = {
                            'type': obj_type,
                            'x': x_points,
                            'y': y_points,
                            'z': z_points,
                            'name': f"{file_obj.name}"
                        }
                        if obj_type == 'mesh':
                             obj_data.update({'i': faces_i, 'j': faces_j, 'k': faces_k})
                             
                        st.session_state.objeto_referencia_4d = obj_data
                        # Guardar copia BASE para permitir modificaciones posteriores sin degradación
                        st.session_state.objeto_referencia_base = obj_data.copy()
                        # Resetear transformaciones activas al cargar nuevo
                        st.session_state.transform_active = {'dx': 0.0, 'dy': 0.0, 'dz': 0.0, 'rx': 0.0, 'ry': 0.0, 'rz': 0.0}
                        
                        st.success(f"✅ Objeto Cargado Exitosamente: {file_obj.name}")
                        if use_auto_center_imp:
                            st.info("ℹ️ Objeto centrado automáticamente y desplazado según configuración.")
                        else:
                            st.info("ℹ️ Objeto cargado en coordenadas originales + configuración.")
 
                except Exception as e:
                    st.error(f"Error procesando archivo: {str(e)}")
 
        # --- CARGAR GUARDADO (Persistencia) ---
        with tab_load:
            # Check if using the mocked auth or real auth
            try:
                saved_objs = auth.get_user_objects(st.session_state.username)
            except AttributeError:
                st.error("Error: Función get_user_objects no encontrada en auth.py. Verifique la actualización del módulo.")
                saved_objs = []

            if saved_objs:
                st.write(f"Objetos guardados de **{st.session_state.username}**:")
                
                for obj_id, name, o_type, d_json, f_date in saved_objs:
                    with st.expander(f"📦 {name} ({f_date})"):
                        st.text(f"Tipo: {o_type}")
                        c_l1, c_l2 = st.columns(2)
                        with c_l1:
                            if st.button("Cargar este Objeto", key=f"load_obj_{obj_id}"):
                                try:
                                    data_loaded = json.loads(d_json)
                                    # Convert list back to numpy where needed (for consistency)
                                    data_loaded['x'] = np.array(data_loaded['x'])
                                    data_loaded['y'] = np.array(data_loaded['y'])
                                    data_loaded['z'] = np.array(data_loaded['z'])
                                    if 'i' in data_loaded:
                                        data_loaded['i'] = np.array(data_loaded['i'])
                                        data_loaded['j'] = np.array(data_loaded['j'])
                                        data_loaded['k'] = np.array(data_loaded['k'])
                                    
                                    st.session_state.objeto_referencia_4d = data_loaded
                                    # Guardar BASE y resetear transformaciones
                                    st.session_state.objeto_referencia_base = data_loaded.copy()
                                    st.session_state.transform_active = {'dx': 0.0, 'dy': 0.0, 'dz': 0.0, 'rx': 0.0, 'ry': 0.0, 'rz': 0.0}
                                    
                                    st.success(f"✅ {name} cargado a la sesión.")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error cargando JSON: {e}")
                        with c_l2:
                            if st.button("🗑️ Eliminar", key=f"del_obj_{obj_id}"):
                                try:
                                    auth.delete_user_object(obj_id)
                                    st.rerun()
                                except:
                                    st.error("Error al eliminar")
            else:
                st.info("No tienes objetos guardados.")

        # --- GUARDAR ACTUAL (Persistencia) ---
        with tab_save:
            if 'objeto_referencia_4d' in st.session_state:
                st.info("Objeto actual en memoria listo para guardar:")
                st.write(f"**Nombre:** {st.session_state.objeto_referencia_4d.get('name', 'Sin Nombre')}")
                st.write(f"**Tipo:** {st.session_state.objeto_referencia_4d.get('type')}")
                
                name_to_save = st.text_input("Nombre para guardar:", value=st.session_state.objeto_referencia_4d.get('name', 'MiObjeto'))
                
                if st.button("💾 Guardar en Base de Datos"):
                    # Serializar a JSON
                    # Numpy arrays need to be converted to lists
                    obj_to_save = st.session_state.objeto_referencia_4d.copy()
                    
                    class NumpyEncoder(json.JSONEncoder):
                        def default(self, obj):
                            if isinstance(obj, np.ndarray):
                                return obj.tolist()
                            return json.JSONEncoder.default(self, obj)
                    
                    try:
                        json_str = json.dumps(obj_to_save, cls=NumpyEncoder)
                        if auth.save_user_object(
                            st.session_state.username, 
                            name_to_save, 
                            obj_to_save['type'], 
                            json_str
                        ):
                            st.success(f"✅ Objeto '{name_to_save}' guardado exitosamente.")
                        else:
                            st.error("Error al guardar en base de datos.")
                    except Exception as e:
                        st.error(f"Error serializando objeto: {e}")
            else:
                st.warning("⚠️ No hay ningún objeto cargado/generado actualmente.")

    with c_preview:
        st.markdown("### 👁️ Vista Previa 3D")
        if 'objeto_referencia_4d' in st.session_state:
            obj = st.session_state.objeto_referencia_4d
            fig_prev = go.Figure()
            
            if obj['type'] == 'mesh':
                fig_prev.add_trace(go.Mesh3d(
                    x=obj['x'], y=obj['y'], z=obj['z'],
                    i=obj['i'], j=obj['j'], k=obj['k'],
                    color='gray', opacity=0.8, name=obj['name'],
                    alphahull=0, showscale=False
                ))
            elif obj['type'] == 'scatter':
                fig_prev.add_trace(go.Scatter3d(
                    x=obj['x'], y=obj['y'], z=obj['z'],
                    mode='markers', marker=dict(size=2, color='gray'),
                    name=obj['name']
                ))
                
            fig_prev.update_layout(
                scene=dict(aspectmode='data', xaxis_title="X", yaxis_title="Y", zaxis_title="Z"),
                margin=dict(l=0, r=0, b=0, t=0),
                height=500
            )
            st.plotly_chart(fig_prev, use_container_width=True)
        else:
            st.warning("No hay objeto definido. Genera uno o importa un CSV.")


elif st.session_state.seccion_actual == '3d' or st.session_state.seccion_actual == 'betz_3d':
    st.markdown("# 🌪️ VISUALIZACIÓN DE ESTELA 3D - Análisis Tridimensional")
    st.markdown("Análisis 3D con superficie interactiva de presiones")
    
    # Paso 1: Configuración inicial
    st.markdown("## ⚙️ Paso 1: Configuración Inicial")

    # Reorganizar: datos a la izquierda, imagen más pequeña a la derecha
    col_datos, col_imagen = st.columns([2, 1])

    with col_datos:
        st.markdown("### 📍 Configuración de Sensores y Geometría")
        
        # Orden de sensores
        orden_sensores = st.selectbox(
            "Orden de lectura de sensores:",
            ["asc", "des"],
            format_func=lambda x: "Ascendente (sensor 1 más abajo al 12 más arriba)" if x == "asc" else "Descendente (sensor 12 más abajo y sensor 1 más arriba)",
            help="Define cómo se leen los datos de los sensores en relación a su posición física",
            key="orden_3d"
        )
        
        # Pregunta sobre el sensor de referencia
        st.info("🔍 **Pregunta:** ¿Qué sensor corresponde a la toma número 12 (la que se encuentra cerca del piso)?")
        sensor_referencia = st.selectbox(
            "Sensor de referencia (toma 12):",
            [f"Sensor {i}" for i in range(1, 13)],
            index=11,  # Por defecto Sensor 12
            help="Seleccione el sensor que corresponde a la toma física número 12",
            key="sensor_ref_3d"
        )
        
        distancia_toma_12 = st.number_input(
            "Distancia de la toma 12 a la posición X=0, Y=0 (coordenadas del traverser) [mm]:",
            value=-120.0,
            step=1.0,
            format="%.1f",
            help="Distancia en mm desde el punto de referencia del traverser",
            key="dist_toma_3d"
        )
        
        distancia_entre_tomas = st.number_input(
            "Distancia entre tomas [mm]:",
            value=10.0,
            step=0.01,
            format="%.2f",
            help="Distancia física entre tomas consecutivas según el plano técnico",
            key="dist_entre_3d"
        )
        
        # Guardar configuración
        if st.button("💾 Guardar Configuración 3D", type="primary", key="save_3d"):
            st.session_state.configuracion_3d = {
                'orden': orden_sensores,
                'sensor_referencia': sensor_referencia,
                'distancia_toma_12': distancia_toma_12,
                'distancia_entre_tomas': distancia_entre_tomas
            }
            st.success("✅ Configuración 3D guardada correctamente")
            st.rerun()

    with col_imagen:
        st.markdown("### 📐 Diagrama de Referencia")
        st.markdown("""
        <div style="background: #f8fafc; border: 2px dashed #e5e7eb; border-radius: 12px; padding: 2rem; text-align: center; color: #64748b;">
            <h4>📐 Diagrama de Referencia</h4>
            <p>Aquí iría el diagrama técnico de sensores</p>
            <p><small>Subir imagen del plano técnico</small></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Mostrar configuración actual
    if st.session_state.get('configuracion_3d'):
        st.markdown("---")
        # Estilo de configuración actual
        st.markdown("""
        <div class="section-card" style="margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h3 style="margin: 0; color: white;">⚙️ CONFIGURACIÓN ACTIVA</h3>
                <span style="color: #666; font-size: 0.8rem;">Parámetros 3D</span>
            </div>
            <div style="display: flex; gap: 20px; margin-top: 15px;">
                <div style="background: #111; padding: 10px; border-radius: 6px; border: 1px solid #333; flex: 1;">
                    <p style="color: #888; font-size: 0.8rem; margin: 0;">Orden</p>
                    <p style="color: white; font-weight: bold; margin: 0;">{}</p>
                </div>
                <div style="background: #111; padding: 10px; border-radius: 6px; border: 1px solid #333; flex: 1;">
                    <p style="color: #888; font-size: 0.8rem; margin: 0;">Toma 12</p>
                    <p style="color: white; font-weight: bold; margin: 0;">{:.1f} mm</p>
                </div>
                <div style="background: #111; padding: 10px; border-radius: 6px; border: 1px solid #333; flex: 1;">
                    <p style="color: #888; font-size: 0.8rem; margin: 0;">Sep. Tomas</p>
                    <p style="color: white; font-weight: bold; margin: 0;">{:.2f} mm</p>
                </div>
            </div>
        </div>
        """.format(
            st.session_state.configuracion_3d['orden'].upper(),
            st.session_state.configuracion_3d['distancia_toma_12'],
            st.session_state.configuracion_3d['distancia_entre_tomas']
        ), unsafe_allow_html=True)
        
        # --- PASO 2: CARGA DE ARCHIVOS 3D ---
        st.markdown("""
        <div class="section-card" style="margin-bottom: 20px;">
            <h3 style="margin-top: 0; color: white;">📁 PASO 2: IMPORTACIÓN DE VOLÚMENES 3D</h3>
            <p style="color: #bbb; margin-bottom: 20px;">Cargue múltiples archivos CSV para generar superficies tridimensionales.</p>
        </div>
        """, unsafe_allow_html=True)

        # Almacenar múltiples archivos 3D
        if 'archivos_3d_cargados' not in st.session_state:
            st.session_state.archivos_3d_cargados = {}

        uploaded_files_3d = st.file_uploader(
            "Arrastre sus archivos CSV 3D aquí",
            type=['csv'],
            accept_multiple_files=True,
            key="uploader_betz3d"
        )
        
        if uploaded_files_3d:
            st.markdown("<br>", unsafe_allow_html=True)
            for uploaded_file_3d in uploaded_files_3d:
                nombre_archivo = uploaded_file_3d.name.replace('.csv', '').replace('incertidumbre_', '')
                
                if nombre_archivo not in st.session_state.archivos_3d_cargados:
                    with st.spinner(f"🌐 Procesando geometría 3D para {nombre_archivo}..."):
                        datos_3d = procesar_promedios(uploaded_file_3d, st.session_state.configuracion_3d['orden'])
                        
                        if datos_3d is not None:
                            st.session_state.archivos_3d_cargados[nombre_archivo] = datos_3d
                            
                            sub_archivos_3d = crear_sub_archivos_3d_por_tiempo_y_posicion(datos_3d, nombre_archivo)
                            st.session_state.sub_archivos_3d_generados.update(sub_archivos_3d)
                            
                            st.success(f"✅ Geometría reconstruida: {nombre_archivo}")

        # Mostrar archivos cargados (Resumen)
        if st.session_state.archivos_3d_cargados:
            st.markdown("### 📋 Resumen de Carga")
            
            # Grid layout for files
            cols = st.columns(3)
            for idx, (nombre, datos) in enumerate(st.session_state.archivos_3d_cargados.items()):
                with cols[idx % 3]:
                    with st.container(border=True):
                        st.markdown(f"**📦 {nombre}**")
                        st.caption(f"{len(datos)} Puntos • {len(datos['Tiempo_s'].unique())} Tiempos")
                        st.progress(100) # Visual indicator that it is ready

            st.markdown("---")
            
            # --- PASO 3: VISUALIZACIÓN ---
            st.markdown("""
            <div class="section-card" style="margin-bottom: 20px;">
                <h3 style="margin-top: 0; color: white;">🌪️ PASO 3: INTERACCIÓN 3D</h3>
                <p style="color: #bbb; margin-bottom: 20px;">Explore la superficie generada, ajuste la cámara y analice la distribución de presiones.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("#### 🎛️ Controles Globales de Escena")
            st.info("Visualización estándar activa.")
            # Controls removed as per user request
            mostrar_cuerpo = False # Default disabled
            aspect_ratio = "auto" # Default auto

        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        
        # 🔘 Checkbox para activar/desactivar puntos medidos
        mostrar_puntos_3d = st.checkbox("🔘 Mostrar puntos originales (Nube de puntos)", value=False, key="mostrar_puntos_3d")

        if st.session_state.archivos_3d_cargados:
            st.markdown("#### 📂 Selección de Geometría a Visualizar")
            
            # Mostrar archivos como botones seleccionables
            archivos_disponibles = list(st.session_state.archivos_3d_cargados.keys())
            
            # Crear columnas para mostrar archivos
            cols_per_row = 3
            for i in range(0, len(archivos_disponibles), cols_per_row):
                cols = st.columns(cols_per_row)
                
                for j, col in enumerate(cols):
                    if i + j < len(archivos_disponibles):
                        nombre_archivo = archivos_disponibles[i + j]
                        datos_archivo = st.session_state.archivos_3d_cargados[nombre_archivo]
                        
                        with col:
                            # Crear card para cada archivo
                            st.markdown(f"""
                            <div style="
                                background: white;
                                border: 2px solid #e5e7eb;
                                border-radius: 12px;
                                padding: 1rem;
                                margin: 0.5rem 0;
                                text-align: center;
                                transition: all 0.3s ease;
                                cursor: pointer;
                            ">
                                <h4 style="color: #08596C; margin-bottom: 0.5rem;">📊 {nombre_archivo}</h4>
                                <p style="color: #6b7280; font-size: 0.9rem; margin-bottom: 0.5rem;">
                                    {len(datos_archivo)} registros
                                </p>
                                <p style="color: #6b7280; font-size: 0.8rem;">
                                    Tiempos: {len(datos_archivo['Tiempo_s'].dropna().unique())}<br>
                                    Pos. Y (Trav): {len(datos_archivo['Pos_Y_Traverser'].dropna().unique())}<br>
                                    Pos. Z (Base): {len(datos_archivo['Pos_Z_Base'].dropna().unique())}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if st.button(f"🏔️ Ver Superficie Completa", key=f"ver_mesh3d_{nombre_archivo}", use_container_width=True):
                                with st.spinner(f"Construyendo superficie completa para {nombre_archivo}..."):
                                    # Llamada a la NUEVA función de graficación con 300 puntos
                                    fig_individual = crear_superficie_delaunay_3d(
                                        datos_archivo,
                                        st.session_state.configuracion_3d,
                                        nombre_archivo,
                                        mostrar_puntos=mostrar_puntos_3d  # ← Aquí
                                    )
                                    
                                    if fig_individual:
                                        st.plotly_chart(fig_individual, use_container_width=False)
                                        
                                        # Información del archivo
                                        st.success(f"✅ Superficie de malla 3D generada para: **{nombre_archivo}** usando {len(fig_individual.data[0].x)} vértices.")
                                        
                                        # Botón de descarga
                                        html_individual = fig_individual.to_html()
                                        st.download_button(
                                            label=f"📊 Descargar Malla 3D (HTML)",
                                            data=html_individual,
                                            file_name=f"mesh_3d_{nombre_archivo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                                            mime="text/html",
                                            key=f"download_mesh3d_{nombre_archivo}"
                                        )
                                    else:
                                        st.error(f"❌ No se pudo generar la superficie de malla 3D para {nombre_archivo}")   
        
        # --- NUEVO PASO 4: DIFERENCIA ENTRE SUPERFICIES ---
        st.markdown("""
        <div class="section-card" style="margin-bottom: 20px;">
            <h3 style="margin-top: 0; color: white;">📉 PASO 4: ANÁLISIS DE DIFERENCIAS</h3>
            <p style="color: #bbb; margin-bottom: 20px;">Calcule y visualice la diferencia aritmética entre dos superficies medidas (A - B).</p>
        </div>
        """, unsafe_allow_html=True)

        if len(st.session_state.get('archivos_3d_cargados', {})) >= 2:
            archivos_disponibles_diff = list(st.session_state.get('archivos_3d_cargados', {}).keys())

            col1_diff, col2_diff = st.columns(2)
            with col1_diff:
                st.markdown("**Superficie A (Base)**")
                archivo_a = st.selectbox(
                    "Minuendo",
                    archivos_disponibles_diff,
                    label_visibility="collapsed",
                    key="diff_3d_a"
                )
            with col2_diff:
                st.markdown("**Superficie B (Resta)**")
                archivo_b = st.selectbox(
                    "Sustraendo",
                    archivos_disponibles_diff,
                    index=1 if len(archivos_disponibles_diff) > 1 else 0,
                    label_visibility="collapsed",
                    key="diff_3d_b"
                )
            
            # 🔘 Checkbox para activar/desactivar puntos en diferencia
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            mostrar_puntos_diff = st.checkbox("🔘 Incluir puntos de medición en el gráfico de diferencia", value=True, key="mostrar_puntos_diff")

            # PARTE 1: El botón "Calcular" solo genera el gráfico y lo guarda en una "bandeja" temporal.
            if st.button("Calcular Diferencia de Superficies", use_container_width=True, type="primary"):
                if archivo_a == archivo_b:
                    st.error("Por favor, selecciona dos archivos diferentes para comparar.")
                else:
                    with st.spinner(f"Calculando diferencia entre '{archivo_a}' y '{archivo_b}'..."):
                        datos_a = st.session_state.archivos_3d_cargados[archivo_a]
                        datos_b = st.session_state.archivos_3d_cargados[archivo_b]
                        
                        fig_diferencia_3d = crear_superficie_diferencia_delaunay_3d(
                            datos_a,
                            datos_b,
                            archivo_a,
                            archivo_b,
                            st.session_state.configuracion_3d,
                            mostrar_puntos=mostrar_puntos_diff  # ← Aquí
                        )

                        if fig_diferencia_3d:
                            # Guardamos la figura y su nombre en la sesión para que sobrevivan al reinicio de la página.
                            st.session_state.figura_diferencia_temporal_3d = {
                                "fig": fig_diferencia_3d,
                                "nombre": f"Dif. 3D: {archivo_a} vs {archivo_b}"
                            }
                        else:
                            if 'figura_diferencia_temporal_3d' in st.session_state:
                                del st.session_state.figura_diferencia_temporal_3d
            
            # PARTE 2: Este bloque (fuera del anterior) revisa si hay algo en la "bandeja" temporal y lo muestra.
            if 'figura_diferencia_temporal_3d' in st.session_state:
                temp_data_3d = st.session_state.figura_diferencia_temporal_3d
                fig_diferencia_3d = temp_data_3d["fig"]
                nombre_guardado_3d = temp_data_3d["nombre"]

                # 1. Mostramos el gráfico
                st.plotly_chart(fig_diferencia_3d, use_container_width=False)
                
                # 2. Mostramos el botón "Guardar". Ahora sí funcionará.
                if st.button("💾 Guardar Diferencia para Visualizar", key="save_diff_3d_for_viz_final"):
                    if 'diferencias_guardadas' not in st.session_state:
                        st.session_state.diferencias_guardadas = {}
                    
                    st.session_state.diferencias_guardadas[nombre_guardado_3d] = fig_diferencia_3d
                    st.success(f"✅ Gráfico '{nombre_guardado_3d}' guardado permanentemente.")
                    
                    # Borramos la figura temporal después de guardarla para limpiar la "bandeja"
                    del st.session_state.figura_diferencia_temporal_3d
                    st.rerun()

        else:
            st.info("Carga al menos dos archivos 3D para poder calcular una diferencia.")

        def extraer_pos_x_estacion(nombre_archivo):
            """
            Intenta extraer la posición X (Estación) del nombre del archivo.
            Patrones buscados: X100, Est100, Station100, _100mm, etc.
            """
            import re
            nombre = os.path.basename(str(nombre_archivo))
            # Patrones comunes: X100, X-100, X_100, Est100, etc.
            patrones = [
                r'[Xx][_\-]?(-?\d+)',        # X100, X-100, X_100
                r'[Ee]st[_\-]?(-?\d+)',      # Est100
                r'[Ss]tation[_\-]?(-?\d+)',  # Station100
                r'[Pp]os[_\-]?(-?\d+)'       # Pos100
            ]
            
            for p in patrones:
                m = re.search(p, nombre)
                if m:
                    try:
                        return float(m.group(1))
                    except:
                        continue
            return 0.0

# --- PASO 5: GUARDAR SUPERFICIE EN BASE DE DATOS ---
        st.markdown("""
        <div class="section-card" style="margin-bottom: 20px;">
            <h3 style="margin-top: 0; color: white;">💾 PASO 5: PERSISTENCIA DE DATOS</h3>
            <p style="color: #bbb; margin-bottom: 0;">Almacene la superficie procesada en la base de datos centralizada.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.get('archivos_3d_cargados'):
            
            # Seleccionar archivo para guardar
            archivos_para_guardar = list(st.session_state.archivos_3d_cargados.keys())
            archivo_guardar = st.selectbox("Seleccionar Archivo para Guardar:", archivos_para_guardar, key="sel_guardar_bd")
            
            if archivo_guardar:
                df_guardar = st.session_state.archivos_3d_cargados[archivo_guardar]
                
                # Filtrar por tiempo si hay múltiples
                tiempos_g = df_guardar['Tiempo_s'].dropna().unique()
                tiempo_g_sel = st.selectbox("Seleccionar Tiempo:", sorted(tiempos_g), key="tiempo_guardar_bd")
                
                # Filtrar datos
                df_filtrado_g = df_guardar[df_guardar['Tiempo_s'] == tiempo_g_sel].copy()
                
                # INTELIGENCIA: Pre-calcular X y Nombre basado en archivo
                x_detectado = extraer_pos_x_estacion(archivo_guardar)
                nombre_base_sugerido = f"{os.path.splitext(archivo_guardar)[0]}_X{int(x_detectado)}_T{tiempo_g_sel}s"
                
                col_g1, col_g2 = st.columns(2)
                nombre_surf = col_g1.text_input("Nombre identificador:", value=nombre_base_sugerido, key="nombre_surf_bd")
                pos_x_surf = col_g2.number_input("Posición X (Estación) [mm]:", value=x_detectado, step=10.0, key="pos_x_bd")
                
                if st.button("💾 Guardar en Base de Datos", key="btn_guardar_bd"):
                    # Convertir a matriz
                    results_g = []
                    # Recorrer filas (cada fila es un instante/posicion con N sensores)
                    for _, row in df_filtrado_g.iterrows():
                         y_trav = row.get('Pos_Y_Traverser')
                         z_base = row.get('Pos_Z_Base')
                         
                         for col in df_filtrado_g.columns:
                             num_sensor = obtener_numero_sensor_desde_columna(col)
                             if num_sensor is not None:
                                 val_presion = row[col]
                                 if pd.isna(val_presion): continue
                                 
                                 # Calcular altura Z real
                                 z_real = calcular_altura_absoluta_z(
                                     num_sensor, 
                                     z_base, 
                                     st.session_state.configuracion_3d.get('distancia_toma_12', -120),
                                     st.session_state.configuracion_3d.get('distancia_entre_tomas', 10.91),
                                     12, # n_sensores default
                                     st.session_state.configuracion_3d.get('orden', 'asc')
                                 )
                                 
                                 results_g.append({
                                     'Y': y_trav,
                                     'Z': z_real,
                                     'Presion': val_presion
                                 })
                    
                    df_final_g = pd.DataFrame(results_g)
                    
                    if not df_final_g.empty:
                        json_str = df_final_g.to_json(orient='records')
                        if auth.save_surface_data(st.session_state.username, nombre_surf, pos_x_surf, json_str):
                            st.success(f"✅ Superficie guardada en BD: {nombre_surf} en X={pos_x_surf}")
                        else:
                            st.error("Error al guardar en base de datos.")
                    else:
                        st.error("No se pudieron extraer datos válidos (Y, Z, Presion).")
        
        else:
            st.info("ℹ️ Para guardar una superficie, primero debe procesar al menos un archivo CSV en el **Paso 2**.")


elif st.session_state.seccion_actual == 'betz_4d':
    st.markdown("""
    <div class="header-container">
        <h1 style="font-size: 3rem; margin-bottom: 1rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
            🌌 VISUALIZACIÓN DE ESTELA 4D
        </h1>
        <h2 style="font-size: 1.8rem; margin-bottom: 0; opacity: 0.9;">
            Visualización Multidimensional y Animación
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Cargar superficies del usuario de la BD
    try:
        mis_superficies = auth.get_user_surfaces(st.session_state.username)
    except AttributeError:
        st.error("Error conectando con base de datos (función get_user_surfaces no encontrada).")
        mis_superficies = []

    if not mis_superficies:
        st.info("⚠️ No tienes superficies guardadas. Ve a 'BETZ 3D' > Paso 5 para guardar superficies procesadas.")
    else:
        # Dictionary for selection: Label -> Data Tuple
        # Data Tuple: (id, filename, x_pos, created_at, data_json)
        dict_superficies = {f"{s[1]} (X={s[2]}) [{s[3]}]": s for s in mis_superficies}
        
        # Multiselect for surfaces
        sel_labels = st.multiselect("Seleccionar Superficies para Análisis:", list(dict_superficies.keys()), key="sel_4d_main")
        
        if sel_labels:
            # Prepare data common for both tabs
            loaded_dfs = {}
            all_pressures = []
            
            for label in sel_labels:
                s_data = dict_superficies[label]
                try:
                    df = pd.read_json(s_data[4])
                    loaded_dfs[label] = df
                    if 'Presion' in df.columns:
                        all_pressures.extend(df['Presion'].tolist())
                except Exception as e:
                    st.error(f"Error cargando datos de {label}: {e}")

            if all_pressures:
                g_min, g_max = min(all_pressures), max(all_pressures)
            else:
                g_min, g_max = 0, 1
            
            tab_viz, tab_anim = st.tabs(["👁️ Visualización Estática 4D", "🎬 Generador de Animación (GIF)"])
            
            # --- TAB 1: VISUALIZACIÓN 4D ---
            with tab_viz:
                st.markdown("### 🌌 Visualización Espacial (Deformación por Presión)")
                st.info("💡 La presión se representa como una deformación en el eje X (Estación).")
                
                pressure_scale = st.slider("Factor de Escala de Relieve:", 0.1, 10.0, 1.0, 0.1, key="scale_4d_viz")
                
                if st.button("🚀 Generar Escena 4D", key="btn_render_4d"):
                    fig_4d = go.Figure()
                    
                    # 1. Render Reference Object
                    if 'objeto_referencia_4d' in st.session_state:
                         obj = st.session_state.objeto_referencia_4d
                         if obj['type'] == 'mesh':
                             fig_4d.add_trace(go.Mesh3d(
                                 x=obj['x'], y=obj['y'], z=obj['z'],
                                 i=obj['i'], j=obj['j'], k=obj['k'],
                                 color='gray', opacity=0.3, name=obj['name'], alphahull=0
                             ))
                         elif obj['type'] == 'scatter':
                             fig_4d.add_trace(go.Scatter3d(
                                 x=obj['x'], y=obj['y'], z=obj['z'],
                                 mode='markers', marker=dict(size=2, color='gray', opacity=0.5), name=obj['name']
                             ))
                    
                    # 2. Render Surfaces
                    for label in sel_labels:
                        df = loaded_dfs.get(label)
                        if df is None: continue
                        
                        s_data = dict_superficies[label]
                        x_base = s_data[2]
                        
                        # Deform X
                        x_def = x_base + (df['Presion'] * pressure_scale)
                        
                        # Triangulate
                        try:
                            tri = Delaunay(df[['Y', 'Z']].values)
                            fig_4d.add_trace(go.Mesh3d(
                                x=x_def, y=df['Y'], z=df['Z'],
                                i=tri.simplices[:,0], j=tri.simplices[:,1], k=tri.simplices[:,2],
                                intensity=df['Presion'],
                                colorscale='Turbo',
                                cmin=g_min, cmax=g_max,
                                showscale=True,
                                opacity=0.9,
                                name=f"{s_data[1]} (X={x_base})"
                            ))
                        except:
                            pass
                            
                    fig_4d.update_layout(
                        title="Escena 4D Integrada",
                        scene=dict(aspectmode='data', xaxis_title="X (Pos + Presion)", yaxis_title="Y", zaxis_title="Z"),
                        height=800,
                        margin=dict(l=0, r=0, b=0, t=40)
                    )
                    st.plotly_chart(fig_4d, use_container_width=True)

            # --- TAB 2: ANIMACIÓN GIF ---
            with tab_anim:
                st.markdown("### 🎬 Generador de Secuencia Temporal")
                st.markdown("Crea un GIF animado interpolando entre las superficies seleccionadas.")
                
                c_anim1, c_anim2, c_anim3 = st.columns(3)
                fps = c_anim1.slider("Velocidad (Cuadros por segundo):", 1, 30, 2, key="fps_anim")
                quality = c_anim2.select_slider("Calidad de Renderizado:", options=["Baja", "Media", "Alta"], value="Media")
                pressure_scale_gif = c_anim3.slider("Escala de Relieve (GIF):", 0.1, 10.0, 1.0, 0.1, key="scale_anim")
                
                # Checkbox for accumulative view
                acumular_frames = st.checkbox("Visualizar progresión acumulativa (Mostrar anteriores)", value=True, key="anim_accum")
                
                # Sort logic
                # We want to animate in order. Either by X position or by Time.
                # Let's extract metadata to sort.
                anim_items = []
                for label in sel_labels:
                    s_data = dict_superficies[label]  # (id, name, x, created, json)
                    # Try to extract 'Time' from name if possible, or use X
                    # Name format usually "File_T10s"
                    time_val = 0
                    try:
                        import re
                        m = re.search(r'T(\d+)s', s_data[1])
                        if m: time_val = int(m.group(1))
                    except: pass
                    
                    anim_items.append({
                        'label': label,
                        'x': s_data[2],
                        'time': time_val,
                        'df': loaded_dfs[label],
                        'name': s_data[1]
                    })
                
                c_sort1, c_sort2 = st.columns([2, 1])
                sort_mode = c_sort1.radio("Ordenar secuencia por:", ["Posición X (Espacial)", "Tiempo (Temporal)"], horizontal=True, key="sort_mode_anim")
                sort_desc = c_sort2.checkbox("Invertir orden (Descendente)", value=True, help="Ordena de Mayor a Menor (Positivo -> Negativo)", key="sort_desc_anim")
                
                if sort_mode == "Posición X (Espacial)":
                    anim_items.sort(key=lambda x: x['x'], reverse=sort_desc)
                else:
                    anim_items.sort(key=lambda x: x['time'], reverse=sort_desc)
                
                if st.button("🎥 Renderizar Animación (GIF)", type="primary"):
                    # Check for kaleido
                    try:
                        import kaleido
                    except ImportError:
                        st.error("❌ Librería 'kaleido' no encontrada. Es necesaria para exportar imágenes. Contacte al administrador.")
                        st.stop()
                        
                    status_text = st.empty()
                    prog_bar = st.progress(0)
                    
                    frames = []
                    temp_dir = tempfile.mkdtemp()
                    
                    try:
                        # 1. Calcular límites globales (Bounding Box de TODA la animación + Objeto ref)
                        all_x, all_y, all_z = [], [], []
                        
                        # Límites de superficies
                        for item in anim_items:
                            df = item['df']
                            # Considerar deformación maxima aproximada para el bounding box
                            # (Asumiendo que la presion positiva deforma hacia +X)
                            max_p = df['Presion'].max()
                            if pd.isna(max_p): max_p = 0
                            
                            all_x.append(item['x'])
                            all_x.append(item['x'] + max_p * pressure_scale_gif) # Incluir deformación
                            
                            all_y.extend(df['Y'].tolist())
                            all_z.extend(df['Z'].tolist())
                            
                        # Límites de objeto referencia (si existe)
                        if 'objeto_referencia_4d' in st.session_state:
                             obj = st.session_state.objeto_referencia_4d
                             all_x.extend(obj.get('x', []))
                             all_y.extend(obj.get('y', []))
                             all_z.extend(obj.get('z', []))
                        
                        if not all_x: all_x = [0, 1]
                        if not all_y: all_y = [0, 1]
                        if not all_z: all_z = [0, 1]

                        # Calcular min/max con un margen MAYOR para alejar la cámara
                        pad = 1.0  # Aumentado a 1.0 para mucho márgen (zoom out)
                        x_min, x_max = min(all_x), max(all_x)
                        y_min, y_max = min(all_y), max(all_y)
                        z_min, z_max = min(all_z), max(all_z)
                        
                        dx = x_max - x_min if x_max != x_min else 1.0
                        dy = y_max - y_min if y_max != y_min else 1.0
                        dz = z_max - z_min if z_max != z_min else 1.0
                        
                        x_range = [x_min - dx*pad, x_max + dx*pad]
                        y_range = [y_min - dy*pad, y_max + dy*pad]
                        z_range = [z_min - dz*pad, z_max + dz*pad]

                        # Generate frames
                        val_range = [g_min, g_max]
                        
                        for i, item in enumerate(anim_items):
                            status_text.text(f"Renderizando cuadro {i+1}/{len(anim_items)}: {item['name']}...")
                            
                            # Create individual figure for this frame
                            fig_frame = go.Figure()
                            
                            # Add Reference Object (Static background)
                            if 'objeto_referencia_4d' in st.session_state:
                                obj = st.session_state.objeto_referencia_4d
                                if obj['type'] == 'mesh':
                                    fig_frame.add_trace(go.Mesh3d(
                                        x=obj['x'], y=obj['y'], z=obj['z'],
                                        i=obj['i'], j=obj['j'], k=obj['k'],
                                        color='black', opacity=0.15, alphahull=0, showscale=False
                                    ))
                                elif obj['type'] == 'scatter':
                                     fig_frame.add_trace(go.Scatter3d(
                                     x=obj['x'], y=obj['y'], z=obj['z'],
                                     mode='markers', marker=dict(size=2, color='black', opacity=0.5), name=obj['name']
                                     ))
                            
                            # DETERMINAR QUÉ MOSTRAR: Solo actual o Acumulado
                            items_to_show = anim_items[:i+1] if acumular_frames else [item]
                            
                            for frame_item in items_to_show:
                                df_f = frame_item['df']
                                tri = Delaunay(df_f[['Y', 'Z']].values)
                                
                                # Calcular deformación
                                x_def = frame_item['x'] + (df_f['Presion'] * pressure_scale_gif)
                                
                                fig_frame.add_trace(go.Mesh3d(
                                    x=x_def, 
                                    y=df_f['Y'],
                                    z=df_f['Z'],
                                    i=tri.simplices[:,0], j=tri.simplices[:,1], k=tri.simplices[:,2],
                                    intensity=df_f['Presion'],
                                    colorscale='Turbo',
                                    cmin=val_range[0], cmax=val_range[1],
                                    showscale=(frame_item == items_to_show[-1]), 
                                    opacity=1.0
                                ))
                            
                            # Layout - ISOMETRIC FIXED VIEW ZOOMED OUT
                            fig_frame.update_layout(
                                title=f"Secuencia: {item['name']} (X={item['x']})",
                                scene=dict(
                                    xaxis=dict(range=x_range, title="X (Estación)"),
                                    yaxis=dict(range=y_range, title="Y (Envergadura)"),
                                    zaxis=dict(range=z_range, title="Z (Altura)"),
                                    aspectmode='data',
                                    camera=dict(
                                        projection=dict(type="orthographic"), 
                                        eye=dict(x=2.5, y=2.5, z=2.5)  # Más alejado aún (antes 2.0)
                                    )
                                ),
                                margin=dict(l=0,r=0,b=0,t=40)
                            )
                            
                            # Save frame
                            frame_path = os.path.join(temp_dir, f"frame_{i:03d}.png")
                            # Scale factor for quality
                            scale = 1.0 if quality == "Baja" else (2.0 if quality == "Media" else 3.0)
                            fig_frame.write_image(frame_path, engine="kaleido", scale=scale)
                            frames.append(frame_path)
                            
                            prog_bar.progress((i + 1) / len(anim_items))
                        
                        # Build GIF
                        status_text.text("Compilando GIF...")
                        gif_path = os.path.join(temp_dir, "animation.gif")
                        
                        images = []
                        for filename in frames:
                            images.append(imageio.imread(filename))
                        
                        imageio.mimsave(gif_path, images, fps=fps, loop=0)
                        
                        # Show
                        st.success("✅ Animación completada")
                        st.image(gif_path)
                        
                        # Download using file read
                        with open(gif_path, "rb") as f:
                            btn = st.download_button(
                                label="📥 Descargar GIF",
                                data=f,
                                file_name="betz_4d_animation.gif",
                                mime="image/gif"
                            )
                            
                    except Exception as e:
                        st.error(f"Error generando animación: {e}")
                    finally:
                        # Cleanup done automatically by temp dir removal? No, explicit needed usually but mkdtemp persists.
                        # We leave it for now or try to clean up.
                         pass


elif st.session_state.seccion_actual == 'herramientas':
    st.markdown("""
    <div class="header-container">
        <h1 style="font-size: 3rem; margin-bottom: 1rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
            🔧 HERRAMIENTAS DE PROCESAMIENTO
        </h1>
        <h2 style="font-size: 1.8rem; margin-bottom: 0; opacity: 0.9;">
            Herramientas avanzadas para el procesamiento y análisis de datos aerodinámicos
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Inicializar variables de sesión si no existen
    if 'archivos_unidos' not in st.session_state:
        st.session_state.archivos_unidos = None
    if 'matriz_presiones' not in st.session_state:
        st.session_state.matriz_presiones = None
    if 'archivo_vtk' not in st.session_state:
        st.session_state.archivo_vtk = None
    
    # --- HERRAMIENTA 1: Unir Archivos de Incertidumbre ---
    with st.container():
        st.markdown("""
        <div class="section-card" style="border-left: 5px solid #0ea5e9; margin-bottom: 10px;">
            <h3 style="color: #0ea5e9; margin: 0;">📁 01. UNIÓN DE ARCHIVOS</h3>
        </div>
        """, unsafe_allow_html=True)
        
        c_desc, c_func = st.columns([1, 2])
        
        with c_desc:
            st.markdown("""
            <p style="color: #ccc; font-size: 0.95rem;">
                Utilidad para combinar múltiples archivos CSV de incertidumbre en un único conjunto de datos.
                <br><br>
                El sistema detectará automáticamente si hay puntos temporales sobrepuestos y generará una alerta.
            </p>
            """, unsafe_allow_html=True)

        with c_func:
            archivos_union = st.file_uploader(
                "Seleccionar archivos CSV:",
                type=['csv'],
                accept_multiple_files=True,
                key="union_archivos",
                label_visibility="collapsed"
            )
            
            c_input, c_btn = st.columns([2, 1])
            with c_input:
                 nombre_archivo_union = st.text_input("Nombre saliente:", value="archivos_unidos", key="nombre_union")
            with c_btn:
                 st.write("") # Spacer
                 st.write("")
                 btn_unir = st.button("🔗 Unir Ahora", key="btn_unir", type="primary", use_container_width=True)

            if btn_unir:
                if archivos_union and len(archivos_union) > 1:
                    with st.spinner("Uniendo archivos..."):
                        contenido_unido, puntos_sobrepuestos = unir_archivos_incertidumbre(
                            archivos_union, nombre_archivo_union
                        )
                        
                        if contenido_unido:
                            st.session_state.archivos_unidos = {
                                'contenido': contenido_unido,
                                'nombre': nombre_archivo_union,
                                'puntos_sobrepuestos': puntos_sobrepuestos
                            }
                            
                            st.success(f"✅ {len(archivos_union)} archivos unidos correctamente")
                            
                            if puntos_sobrepuestos:
                                st.warning(f"⚠️ Se detectaron {len(puntos_sobrepuestos)} puntos sobrepuestos")
                                with st.expander("Ver puntos sobrepuestos"):
                                    for punto in puntos_sobrepuestos:
                                        st.write(f"Y={punto[0]}, Z={punto[1]}, Tiempo={punto[2]}s")
                            
                            # Botón de descarga
                            st.download_button(
                                label="📥 Descargar CSV Unido",
                                data=contenido_unido.encode('utf-8-sig'),
                                file_name=f"{nombre_archivo_union}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )
                else:
                    st.error("❌ Seleccione min. 2 archivos")

    st.markdown("---")

    # --- HERRAMIENTA 2: Extraer matriz de presiones ---
    with st.container():
        st.markdown("""
        <div class="section-card" style="border-left: 5px solid #f59e0b; margin-bottom: 10px;">
            <h3 style="color: #f59e0b; margin: 0;">📊 02. MATRIZ DE PRESIONES</h3>
        </div>
        """, unsafe_allow_html=True)
        
        c_desc, c_func = st.columns([1, 2])
        
        with c_desc:
            st.markdown("""
            <p style="color: #ccc; font-size: 0.95rem;">
                Extrae una matriz estructurada (Filas=Y, Columnas=Z) de presiones a partir de datos crudos.
                <br><br>
                Ideal para análisis numérico posterior o verificación manual de campos.
            </p>
            """, unsafe_allow_html=True)
            
        with c_func:
            archivo_matriz = st.file_uploader(
                "Cargar archivo de incertidumbre:",
                type=['csv'],
                key="archivo_matriz",
                 label_visibility="collapsed"
            )
            
            c_input, c_btn = st.columns([2, 1])
            with c_input:
                nombre_matriz = st.text_input("Nombre matriz:", value="matriz_presiones", key="nombre_matriz")
            with c_btn:
                st.write("")
                st.write("")
                btn_matriz = st.button("📊 Extraer", key="btn_matriz", type="primary", use_container_width=True)

            # Configuración de sensores para esta herramienta
            with st.expander("Configuración de Sensores (Avanzado)"):
                configuracion_matriz = mostrar_configuracion_sensores("herramienta2")

            if btn_matriz:
                if archivo_matriz:
                    with st.spinner("Procesando..."):
                        matriz = extraer_matriz_presiones_completa(archivo_matriz, configuracion_matriz)

                        if matriz is not None and not matriz.empty:
                            st.session_state.matriz_presiones = {
                                'matriz': matriz,
                                'nombre': nombre_matriz
                            }

                            st.success("✅ Matriz extraída")
                            st.dataframe(matriz.head(), use_container_width=True)

                            # Botón de descarga
                            df_matriz = pd.DataFrame(matriz, columns=["Y", "Z", "Presion"])
                            csv_matriz = df_matriz.to_csv(sep=';', decimal=',', index=False)
                            st.download_button(
                                label="📥 Descargar Matriz CSV",
                                data=csv_matriz.encode('utf-8-sig'),
                                file_name=f"{nombre_matriz}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )
                else:
                    st.error("❌ Falta archivo")

    st.markdown("---")

    # --- HERRAMIENTA 3: Generador VTK ---
    with st.container():
        st.markdown("""
        <div class="section-card" style="border-left: 5px solid #10b981; margin-bottom: 10px;">
            <h3 style="color: #10b981; margin: 0;">🎯 03. GENERADOR VTK (CFD)</h3>
        </div>
        """, unsafe_allow_html=True)
        
        c_desc, c_func = st.columns([1, 2])
        
        with c_desc:
            st.markdown("""
            <p style="color: #ccc; font-size: 0.95rem;">
                Convierte matrices de presión en archivos .VTK compatibles con ParaView o Salome.
                <br><br>
                Permite interpolación cúbica para suavizar mallas o triangulación de Delaunay para superficies topográficas.
            </p>
            """, unsafe_allow_html=True)
            
        with c_func:
            opcion_matriz = st.radio(
                "Fuente de datos:",
                ["Usar matriz existente (de paso anterior)", "Cargar nuevo archivo CSV"],
                key="opcion_matriz_vtk",
                horizontal=True
            )

            df_matriz_vtk = None
            matriz_disponible = st.session_state.get('matriz_presiones')

            if opcion_matriz == "Usar matriz existente (de paso anterior)":
                if matriz_disponible:
                    st.success(f"✅ Usando: {matriz_disponible['nombre']}")
                    df_matriz_vtk = matriz_disponible['matriz']
                else:
                    st.warning("⚠️ No hay matriz en memoria. Cargue un archivo nuevo.")
            else:
                archivo_vtk_source = st.file_uploader(
                    "CSV Matriz:", type=['csv'], key="archivo_vtk", label_visibility="collapsed"
                )
                if archivo_vtk_source:
                    try:
                        df_matriz_vtk = pd.read_csv(archivo_vtk_source, sep=';', decimal=',')
                    except:
                        st.error("Error leyendo CSV")
            
            c_in, c_sl, c_px = st.columns([2, 1, 1])
            with c_in:
                 nombre_vtk = st.text_input("Nombre VTK:", value="datos_presion", key="nombre_vtk")
            with c_sl:
                 resolucion_factor = st.slider("Interpolación / Suavizado:", 1, 5, 2)
            with c_px:
                 posicion_x_vtk = st.number_input("Posición X (mm):", value=0.0, step=10.0, key="pos_x_vtk_herr")
            
            # Botones de acción
            c_b1, c_b2 = st.columns(2)

            # --- VTK INTERPOLADO CÚBICO (OCULTO - No borrar, solo silenciado) ---
            # with c_b1:
            #     if st.button("🚀 VTK Interpolado", use_container_width=True):
            #          if df_matriz_vtk is not None:
            #             meta = {"Temperatura_C": 20, "Humedad_Rel_Porc": 50, "Presion_Atm_hPa": 1013, "Velocidad_Ref_ms": 0}
            #             res = crear_archivo_vtk_interpolado(df_matriz_vtk, nombre_vtk, resolucion_factor, meta, posicion_x_vtk)
            #             if res:
            #                 with open(res, "rb") as f:
            #                     st.download_button("📥 Bajar VTK", f.read(), f"{nombre_vtk}.vtk")
            #          else:
            #             st.error("No Data")

            with c_b1:
                if st.button("🗺️ VTK Plano 2D", use_container_width=True,
                             help="Plano YZ plano (X fijo). Presión solo como color, sin deformación geométrica."):
                    if df_matriz_vtk is not None:
                        resultado = crear_vtk_plano_presion_2d(df_matriz_vtk, nombre_vtk, posicion_x_vtk)
                        if resultado:
                            vtk_path, vtk_bytes = resultado
                            col_dl1, col_dl2 = st.columns(2)
                            with col_dl1:
                                st.download_button("📥 Descargar VTK Plano", vtk_bytes,
                                                   file_name=os.path.basename(vtk_path),
                                                   mime="application/octet-stream", key="dl_vtk_plano")
                            with col_dl2:
                                if st.button("☁️ Guardar en Drive", key="save_vtk_plano_drive"):
                                    if auth.save_vtk_plano(st.session_state.username,
                                                           os.path.basename(vtk_path), vtk_bytes):
                                        st.success("✅ Subido → HERRAMIENTAS/ARCHIVOS VTK/PLANOS DE PRESION")
                                    else:
                                        st.error("Error al subir a Drive")
                    else:
                        st.error("❌ No hay datos de matriz cargados")

            with c_b2:
                if st.button("🕸️ VTK 3D (Malla Delaunay)", use_container_width=True,
                             help="Triangula los puntos medidos con Delaunay. Fiel a los datos reales, ideal para CFD."):
                     if df_matriz_vtk is not None:
                        res = crear_vtk_superficie_3d_delaunay(df_matriz_vtk, nombre_vtk, posicion_x_vtk)
                        if res:
                            with open(res, "rb") as vtk_f:
                                vtk_bytes_3d = vtk_f.read()
                            col_dl3, col_dl4 = st.columns(2)
                            with col_dl3:
                                st.download_button("📥 Descargar VTK 3D", vtk_bytes_3d,
                                                   file_name=f"{nombre_vtk}_3D.vtk",
                                                   mime="application/octet-stream", key="dl_vtk_3d")
                            with col_dl4:
                                if st.button("☁️ Guardar en Drive", key="save_vtk_3d_drive"):
                                    if auth.save_vtk_superficie(st.session_state.username,
                                                                f"{nombre_vtk}_3D.vtk", vtk_bytes_3d):
                                        st.success("✅ Subido → HERRAMIENTAS/ARCHIVOS VTK/SUPERFICIES 3D")
                                    else:
                                        st.error("Error al subir a Drive")
                     else:
                        st.error("❌ No hay datos de matriz cargados")






elif st.session_state.seccion_actual == 'configuracion':
    # Hero Title for Config
    st.markdown("""
    <div style="text-align: center; padding: 4rem 2rem; background: linear-gradient(180deg, #000 0%, #111 100%); margin-bottom: 3rem;">
        <h1 style="font-size: 3.5rem; margin-bottom: 1rem; letter-spacing: 4px; color: #fff; text-transform: uppercase;">Configuración</h1>
        <p style="color: #666; font-size: 1.2rem; max-width: 600px; margin: 0 auto;">Estado del sistema y gestión de parámetros operativos.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🔌 Estado del Sistema")
    
    # Check Database
    db_ok = os.path.exists("users.db")
    db_size = os.path.getsize("users.db") / 1024 if db_ok else 0
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="section-card" style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 10px;">💾</div>
            <h4 style="margin:0; color:white;">Base de Datos</h4>
            <div style="font-size: 1.2rem; font-weight:bold; color: {'#4ade80' if db_ok else '#f87171'}; margin: 10px 0;">
                {'● ONLINE' if db_ok else '● OFFLINE'}
            </div>
            <p style="color: grey; font-size: 0.8rem; margin:0;">users.db ({db_size:.1f} KB)</p>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown(f"""
        <div class="section-card" style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 10px;">👤</div>
            <h4 style="margin:0; color:white;">Sesión Activa</h4>
            <div style="font-size: 1.2rem; font-weight:bold; color: #60a5fa; margin: 10px 0;">
                {st.session_state.username}
            </div>
            <p style="color: grey; font-size: 0.8rem; margin:0;">Privilegios: {'Admin' if st.session_state.username=='admin' else 'Usuario'}</p>
        </div>
        """, unsafe_allow_html=True)
        
    with c3:
        st.markdown(f"""
        <div class="section-card" style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 10px;">🚀</div>
            <h4 style="margin:0; color:white;">Versión App</h4>
            <div style="font-size: 1.2rem; font-weight:bold; color: #a78bfa; margin: 10px 0;">
                v2.1.0
            </div>
            <p style="color: grey; font-size: 0.8rem; margin:0;">Build: {datetime.now().strftime('%Y.%m.%d')}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🗃️ Gestión de Datos de Perfil")
    st.info("Administre las superficies guardadas y los modelos 3D asociados a su cuenta.")
    
    try:
        sup_perfil = auth.get_user_surfaces(st.session_state.username)
        obj_perfil = auth.get_user_objects(st.session_state.username)
    except Exception as e:
        sup_perfil = []
        obj_perfil = []
        st.error(f"Error accediendo a datos de perfil: {e}")
        
    tab_p1, tab_p2 = st.tabs(["📊 Superficies Guardadas (CSVs)", "📦 Modelos 3D Guardados"])
    
    with tab_p1:
        if not sup_perfil:
            st.write("No tienes superficies guardadas.")
        else:
            sup_dict = {f"{s[1]} (X={s[2]}) [{s[3]}]": s[0] for s in sup_perfil}
            sel_sup_label = st.selectbox("Seleccionar Superficie:", list(sup_dict.keys()), key="sel_sup_perfil")
            sel_sup_id = sup_dict[sel_sup_label]
            
            cp1, cp2 = st.columns(2)
            with cp1:
                nuevo_nombre_sup = st.text_input("Nuevo Nombre (Archivo):", value=sel_sup_label.split(" (")[0], key="ren_sup_inp")
                if st.button("Renombrar Superficie", key="btn_ren_sup"):
                    auth.rename_user_surface(sel_sup_id, nuevo_nombre_sup)
                    st.success("✅ Nombre actualizado.")
                    st.rerun()
            with cp2:
                st.write("")
                st.write("")
                if st.button("🗑️ Eliminar Superficie", type="primary", key="btn_del_sup"):
                    auth.delete_user_surface(sel_sup_id)
                    st.success("✅ Superficie eliminada.")
                    st.rerun()

    with tab_p2:
        if not obj_perfil:
            st.write("No tienes modelos 3D guardados.")
        else:
            obj_dict = {f"{o[1]} [{o[4]}]": o[0] for o in obj_perfil}
            sel_obj_label = st.selectbox("Seleccionar Modelo 3D:", list(obj_dict.keys()), key="sel_obj_perfil")
            sel_obj_id = obj_dict[sel_obj_label]
            
            cp3, cp4 = st.columns(2)
            with cp3:
                nuevo_nombre_obj = st.text_input("Nuevo Nombre (Objeto):", value=sel_obj_label.split(" [")[0], key="ren_obj_inp")
                if st.button("Renombrar Modelo 3D", key="btn_ren_obj"):
                    auth.rename_user_object(sel_obj_id, nuevo_nombre_obj)
                    st.success("✅ Nombre actualizado.")
                    st.rerun()
            with cp4:
                st.write("")
                st.write("")
                if st.button("🗑️ Eliminar Modelo 3D", type="primary", key="btn_del_obj"):
                    auth.delete_user_object(sel_obj_id)
                    st.success("✅ Modelo 3D eliminado.")
                    st.rerun()

    st.markdown("---")
    st.markdown("### 👥 Gestión de Usuarios")
    
    if st.session_state.username == 'admin':
        st.success("✅ Acceso de Administrador - Panel de Gestión de Usuarios")
        
        with st.expander("➕ Crear Nuevo Usuario", expanded=False):
            col_u1, col_u2 = st.columns(2)
            with col_u1:
                new_username = st.text_input("Nombre de Usuario", key="admin_new_user")
            with col_u2:
                new_password = st.text_input("Contraseña", type="password", key="admin_new_pass")
            
            if st.button("Crear Usuario", type="primary"):
                if not new_username or not new_password:
                    st.error("Complete todos los campos")
                elif len(new_password) < 4:
                    st.error("La contraseña debe tener al menos 4 caracteres")
                else:
                    if auth.create_user(new_username, new_password):
                        st.success(f"✅ Usuario '{new_username}' creado exitosamente")
                    else:
                        st.error(f"❌ El usuario '{new_username}' ya existe")
        
        st.info("💡 Los usuarios creados podrán acceder inmediatamente con sus credenciales.")
    else:
        st.warning("⚠️ Solo el administrador puede gestionar usuarios. Contacte al admin para solicitar acceso.")


# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #6b7280; padding: 2rem;'>
    <p><strong>Laboratorio de Aerodinámica y Fluidos - UTN HAEDO</strong></p>
    <p>Sistema de Análisis de Datos Aerodinámicos • Versión 1.43 - Con Herramientas de Procesamiento</p>
    <p><small>Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</small></p>
</div>
""", unsafe_allow_html=True)
