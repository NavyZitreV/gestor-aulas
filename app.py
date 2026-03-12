import streamlit as st
import pandas as pd
import os
import re
import datetime
import json

# 1. Configuración de página principal
st.set_page_config(layout="wide", page_title="Gestor Académico")

# 2. Estilos personalizados Premium (CSS) con íconos vectoriales
st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
    .titulo-principal { font-size: 2.5rem; font-weight: 600; color: #0F172A; margin-bottom: 5px; }
    .subtitulo { font-size: 1.1rem; color: #475569; margin-bottom: 30px; font-weight: 400; }
    
    .text-blue { color: #1E3A8A; }
    .text-orange { color: #EA580C; }
    
    .tarjeta-aula {
        background-color: #FFFFFF; 
        border: 1px solid #E2E8F0; 
        padding: 16px; 
        border-radius: 6px; 
        margin-bottom: 15px; 
        font-weight: 500; 
        font-size: 1.05rem;
        color: #1E293B; 
        text-align: center; 
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
        border-bottom: 3px solid #1E3A8A;
    }
    
    .metric-container {
        background-color: #F8FAFC; 
        color: #334155; 
        padding: 15px 25px;
        border-radius: 6px; 
        font-size: 1.25rem; 
        font-weight: 600;
        display: inline-block; 
        margin-bottom: 25px; 
        border: 1px solid #E2E8F0; 
        border-left: 4px solid #EA580C;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    
    .alert-custom {
        padding: 12px 16px;
        border-radius: 6px;
        margin-bottom: 12px;
        font-weight: 500;
        font-size: 0.95rem;
    }
    .alert-info-custom { background-color: #E0F2FE; color: #075985; border-left: 4px solid #1E3A8A; } /* Azul oscuro */
    .alert-success-custom { background-color: #ECFCCB; color: #3F6212; border-left: 4px solid #84CC16; }
    .alert-warning-custom { background-color: #FFEDD5; color: #9A3412; border-left: 4px solid #EA580C; } /* Naranja */
    .alert-error-custom { background-color: #FEE2E2; color: #991B1B; border-left: 4px solid #EF4444; }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
        color: #1E3A8A;
        font-weight: 600;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #EA580C;
    }
    
    /* === Sobrescribir color base de Streamlit (Rojo -> Naranja) === */
    /* Botones primarios */
    button[kind="primary"] {
        background-color: #EA580C !important;
        border-color: #EA580C !important;
        color: #FFFFFF !important;
    }
    button[kind="primary"]:hover {
        background-color: #C2410C !important;
        border-color: #C2410C !important;
    }
    /* Etiquetas del multiselect */
    span[data-baseweb="tag"] {
        background-color: #EA580C !important;
    }
    /* Selecciones de radio y checkbox */
    div[data-baseweb="radio"] div[data-checked="true"] > div {
        background-color: #EA580C !important;
        border-color: #EA580C !important;
    }
    .stCheckbox [data-baseweb="checkbox"] [data-checked="true"] > div {background-color: #EA580C !important; border-color: #EA580C !important;}
    
    /* Iconos FontAwesome en pestañas directamente vía CSS */
    button[data-baseweb="tab"]:nth-child(1) p::before, button[data-baseweb="tab"]:nth-child(1) span::before { content: "\f52b"; font-family: "Font Awesome 6 Free"; font-weight: 900; margin-right: 8px; }
    button[data-baseweb="tab"]:nth-child(2) p::before, button[data-baseweb="tab"]:nth-child(2) span::before { content: "\f002"; font-family: "Font Awesome 6 Free"; font-weight: 900; margin-right: 8px; }
    button[data-baseweb="tab"]:nth-child(3) p::before, button[data-baseweb="tab"]:nth-child(3) span::before { content: "\f46c"; font-family: "Font Awesome 6 Free"; font-weight: 900; margin-right: 8px; }
    button[data-baseweb="tab"]:nth-child(4) p::before, button[data-baseweb="tab"]:nth-child(4) span::before { content: "\f3c5"; font-family: "Font Awesome 6 Free"; font-weight: 900; margin-right: 8px; }
    button[data-baseweb="tab"]:nth-child(5) p::before, button[data-baseweb="tab"]:nth-child(5) span::before { content: "\f073"; font-family: "Font Awesome 6 Free"; font-weight: 900; margin-right: 8px; }
</style>
""", unsafe_allow_html=True)

# Directorio para base de datos
DATA_DIR = "datos_horarios"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

RESERVAS_FILE = os.path.join(DATA_DIR, "reservas_temporales.json")

def mostrar_alerta(mensaje, tipo="info", icono="fa-info-circle"):
    css_class = f"alert-custom alert-{tipo}-custom"
    color_icon = "text-blue" if tipo == "info" else "text-orange" if tipo == "warning" else ""
    # Override de color para ícono si es success/error
    st.markdown(f"<div class='{css_class}'><i class='fa-solid {icono} {color_icon}' style='margin-right:8px;'></i> {mensaje}</div>", unsafe_allow_html=True)

def cargar_reservas():
    if os.path.exists(RESERVAS_FILE):
        try:
            with open(RESERVAS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def guardar_reservas(reservas):
    with open(RESERVAS_FILE, "w", encoding="utf-8") as f:
        json.dump(reservas, f, ensure_ascii=False, indent=4)

def obtener_archivo_guardado():
    if os.path.exists(DATA_DIR):
        archivos = [f for f in os.listdir(DATA_DIR) if f.endswith(('.xlsx', '.csv'))]
        if archivos:
            return os.path.join(DATA_DIR, archivos[0])
    return None

# Barra lateral para carga
st.sidebar.markdown('<h3><i class="fa-solid fa-server text-blue"></i> Base de Datos</h3>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="alert-custom alert-info-custom"><i class="fa-solid fa-cloud-arrow-up text-blue"></i> El sistema almacenará el último archivo cargado para evitar subidas recurrentes.</div>', unsafe_allow_html=True)
uploaded_file = st.sidebar.file_uploader("Actualizar archivo de horarios (.xlsx, .csv)", type=["xlsx", "csv"])

if uploaded_file is not None:
    for f in os.listdir(DATA_DIR):
        os.remove(os.path.join(DATA_DIR, f))
    
    ruta_guardado = os.path.join(DATA_DIR, uploaded_file.name)
    with open(ruta_guardado, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.sidebar.markdown('<div class="alert-custom alert-success-custom"><i class="fa-solid fa-check"></i> Archivo almacenado correctamente.</div>', unsafe_allow_html=True)

archivo_activo = obtener_archivo_guardado()

if archivo_activo:
    st.sidebar.markdown(f'<div class="alert-custom alert-success-custom"><i class="fa-solid fa-database"></i> Origen de datos: {os.path.basename(archivo_activo)}</div>', unsafe_allow_html=True)

st.sidebar.markdown('<hr style="margin:20px 0;">', unsafe_allow_html=True)
st.sidebar.markdown('<h4 style="color:#1E3A8A; font-weight:600;"><i class="fa-solid fa-palette text-orange"></i> Preferencias Visuales</h4>', unsafe_allow_html=True)
modo_nocturno = st.sidebar.toggle("Modo Nocturno", value=False)

if modo_nocturno:
    st.markdown("""
    <style>
        /* Variables y colores para Modo Nocturno */
        [data-testid="stAppViewContainer"], .stApp { background-color: #0F172A; color: #F8FAFC; }
        [data-testid="stHeader"] { background-color: transparent; }
        [data-testid="stSidebar"] { background-color: #1E293B; }
        
        body, p, span, div, label, h1, h2, h3, h4, h5, h6 { color: #E2E8F0 !important; }
        
        .titulo-principal { color: #FFFFFF !important; }
        .titulo-principal i { color: #60A5FA !important; }
        .subtitulo { color: #CBD5E1 !important; }
        .text-blue { color: #60A5FA !important; }
        .text-orange { color: #FB923C !important; }
        
        .tarjeta-aula {
            background-color: #1E293B !important;
            border: 1px solid #334155 !important;
            color: #F1F5F9 !important;
            border-bottom: 3px solid #60A5FA !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3) !important;
        }
        
        .metric-container {
            background-color: #1E293B !important;
            color: #F8FAFC !important;
            border: 1px solid #334155 !important;
            border-left: 4px solid #FB923C !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3) !important;
        }
        
        /* Alertas en Modo Oscuro */
        .alert-info-custom { background-color: #082F49 !important; color: #E0F2FE !important; border-left-color: #38BDF8 !important; }
        .alert-success-custom { background-color: #14532D !important; color: #DCFCE7 !important; border-left-color: #4ADE80 !important; }
        .alert-warning-custom { background-color: #7C2D12 !important; color: #FFEDD5 !important; border-left-color: #FB923C !important; }
        .alert-error-custom { background-color: #7F1D1D !important; color: #FEE2E2 !important; border-left-color: #F87171 !important; }
        
        /* Ajuste de Pestañas */
        .stTabs [data-baseweb="tab"] { background-color: transparent !important; }
        .stTabs [data-baseweb="tab"] p, .stTabs [data-baseweb="tab"] span { color: #94A3B8 !important; }
        .stTabs [data-baseweb="tab"][aria-selected="true"] p, .stTabs [data-baseweb="tab"][aria-selected="true"] span {
            color: #FB923C !important;
        }
        
        /* Elementos nativos de Streamlit */
        .stTextInput > div > div > input, .stSelectbox > div > div > div, .stNumberInput > div > div > input, .stDateInput > div > div > input, .stTimeInput > div > div > input {
            background-color: #334155 !important;
            color: #FFFFFF !important;
            border-color: #475569 !important;
        }
        
        .stMultiSelect div[data-baseweb="select"] > div {
            background-color: #334155 !important;
            border-color: #475569 !important;
        }
        
        .stRadio label, .stCheckbox label {
            color: #E2E8F0 !important;
        }
        
        /* Ocultar posibles artefactos visuales blancos */
        section[data-testid="stSidebar"] div.stRadio > div { background-color: transparent !important; }
        
    </style>
    <script>
        // Pequeño hack para forzar renderización del body completo si es necesario
        document.body.style.backgroundColor = "#0F172A";
    </script>
    """, unsafe_allow_html=True)

st.markdown('<p class="titulo-principal"><i class="fa-solid fa-building-columns text-blue"></i> Gestor Académico UNICEN</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitulo"><i class="fa-solid fa-chart-network text-orange"></i> Sistema integral de consulta, auditoría y seguimiento de asignaciones de aulas e infraestructura.</p>', unsafe_allow_html=True)

# 3. Mapeos de horarios 
MAPEO_REGULAR = {
    "08:00 A 09:30": ["08:00:00 - 08:45:00", "08:45:00 - 09:30:00"],
    "09:40 A 11:10": ["09:40:00 - 10:25:00", "10:25:00 - 11:10:00"],
    "11:20 A 12:50": ["11:20:00 - 12:05:00", "12:05:00 - 12:50:00"],
    "14:00 A 15:30": ["14:00:00 - 14:45:00", "14:45:00 - 15:30:00"],
    "15:40 A 17:10": ["15:40:00 - 16:25:00", "16:25:00 - 17:10:00"],
    "17:20 A 18:50": ["17:20:00 - 18:05:00", "18:05:00 - 18:50:00"],
    "19:00 A 20:30": ["19:00:00 - 19:45:00", "19:45:00 - 20:30:00"],
    "20:40 A 22:10": ["20:40:00 - 21:25:00", "21:25:00 - 22:10:00"]
}

MAPEO_SABADO = {
    "08:00 A 09:30": ["08:00:00 - 08:45:00", "08:45:00 - 09:30:00"],
    "09:40 A 11:10": ["09:40:00 - 10:25:00", "10:25:00 - 11:10:00"],
    "11:20 A 12:50": ["11:20:00 - 12:05:00", "12:05:00 - 12:50:00"],
    "14:00 A 17:10 (FINANZAS I)": ["14:00:00 - 14:45:00", "14:45:00 - 15:30:00", "15:40:00 - 16:25:00", "16:25:00 - 17:10:00"],
    "17:20 A 20:30 (AUDITORIA DE SISTEMAS)": ["17:20:00 - 18:05:00", "18:05:00 - 18:50:00", "19:00:00 - 19:45:00", "19:45:00 - 20:30:00"]
}

MAPEO_DOMINGO = {
    "08:00 A 09:30": ["08:00:00 - 08:45:00", "08:45:00 - 09:30:00"],
    "09:40 A 11:10": ["09:40:00 - 10:25:00", "10:25:00 - 11:10:00"],
    "11:20 A 12:50": ["11:20:00 - 12:05:00", "12:05:00 - 12:50:00"],
    "13:00 A 14:30": ["13:00:00 - 13:45:00", "13:45:00 - 14:30:00"]
}

def parse_time(time_str):
    time_str = time_str.strip()
    try:
        if len(time_str.split(":")) == 3:
            return datetime.datetime.strptime(time_str, "%H:%M:%S").time()
        else:
            return datetime.datetime.strptime(time_str, "%H:%M").time()
    except Exception:
        return None

def en_rango_horario(hora_str, hora_obj):
    """Verifica si un objeto datetime.time está dentro del string 'HH:MM:SS - HH:MM:SS'"""
    try:
        partes = str(hora_str).split("-")
        if len(partes) == 2:
            inicio = parse_time(partes[0])
            fin = parse_time(partes[1])
            if inicio and fin:
                return inicio <= hora_obj <= fin
    except Exception:
        pass
    return False

@st.cache_data
def cargar_datos(ruta_archivo):
    try:
        if ruta_archivo.endswith('.csv'):
            df = pd.read_csv(ruta_archivo)
        else:
            df = pd.read_excel(ruta_archivo)
    except Exception as e:
        mostrar_alerta(f"Error en la lectura del archivo: {e}", "error", "fa-circle-xmark")
        return None
    
    df.columns = df.columns.astype(str).str.strip().str.upper()
    return df

if not archivo_activo:
    mostrar_alerta("Para iniciar, por favor cargue el archivo Excel o CSV correspondiente al plan semestral.", "info", "fa-circle-info")
else:
    try:
        with st.spinner("Procesando estructura de datos..."):
            df = cargar_datos(archivo_activo)
        
        if df is not None:
            dias_semana = ["LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES", "SABADO", "DOMINGO"]
            
            if 'TORRE' in df.columns:
                torres = sorted([t for t in df['TORRE'].dropna().astype(str).str.upper().str.strip().unique() if t])
            else:
                mostrar_alerta("No se encontró la columna clave 'TORRE'. La filtración por bloque no está disponible.", "warning", "fa-triangle-exclamation")
                torres = []
                
            dias_presentes = [d for d in dias_semana if d in df.columns]
            
            re_docente = re.compile(r'DOCENTE\s*:([^:]+)(?:MATERIA\s*:|GRUPO\s*:|$)')
            re_materia = re.compile(r'MATERIA\s*:([^:]+)(?:GRUPO\s*:|DOCENTE\s*:|$)')
            
            # 4. Creación de las 4 Pestañas
            tab_libres, tab_busqueda, tab_auditoria, tab_ahora, tab_reservas = st.tabs([
                "Disponibilidad de Aulas", 
                "Consulta de Asignaciones", 
                "Auditoría de Conflictos", 
                "Seguimiento Operativo",
                "Gestión de Reservas"
            ])
            
            # --- PESTAÑA 1: AULAS LIBRES ---
            with tab_libres:
                st.markdown("### <i class='fa-solid fa-door-open text-blue'></i> Disponibilidad de Aulas", unsafe_allow_html=True)
                modo_busqueda = st.radio("Criterio de Búsqueda:", ["Planificación Semestral (Día de la semana)", "Consulta Específica (Fecha calendario)"], horizontal=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if "Semestral" in modo_busqueda:
                        dias_sel = st.multiselect("Día(s) de la semana:", dias_semana, default=["LUNES"])
                        fecha_sel = None
                        st.caption("Criterio general que excluye contingencias operativas.")
                    else:
                        fecha_sel = st.date_input("Fecha a consultar:")
                        dias_map = {0: "LUNES", 1: "MARTES", 2: "MIERCOLES", 3: "JUEVES", 4: "VIERNES", 5: "SABADO", 6: "DOMINGO"}
                        dia_busqueda = dias_map[fecha_sel.weekday()]
                        mostrar_alerta(f"Día determinado: {dia_busqueda}", "info", "fa-calendar-day")
                        dias_sel = [dia_busqueda] if dia_busqueda in dias_presentes else []
                        
                with col2:
                    torre_sel = st.selectbox("Torre / Edificio:", torres) if torres else st.selectbox("Torre / Edificio:", ["N/A"])
                    
                with col3:
                    todos_los_bloques = {}
                    todos_los_bloques.update(MAPEO_REGULAR)
                    todos_los_bloques.update(MAPEO_SABADO)
                    todos_los_bloques.update(MAPEO_DOMINGO)
                    nombres_bloques = list(dict.fromkeys(list(MAPEO_REGULAR.keys()) + list(MAPEO_SABADO.keys()) + list(MAPEO_DOMINGO.keys())))
                    bloques_sel = st.multiselect("Franja(s) Horaria(s):", nombres_bloques, default=[nombres_bloques[0]] if nombres_bloques else [])
                    
                st.markdown("<br>", unsafe_allow_html=True)
                col_btn, _, _ = st.columns([1,1,1])
                with col_btn:
                    buscar_aulas_btn = st.button("Ejecutar Consulta de Disponibilidad", use_container_width=True, type="primary")
                
                if buscar_aulas_btn:
                    st.markdown("<hr style='margin-top:0px; margin-bottom:25px;'>", unsafe_allow_html=True)
                    if not dias_sel:
                        if "Específica" in modo_busqueda:
                            mostrar_alerta(f"El vector {dia_busqueda} no cuenta con datos de estructura base.", "warning", "fa-triangle-exclamation")
                        else:
                            mostrar_alerta("Especifique al menos un día en el formulario.", "warning", "fa-triangle-exclamation")
                    elif not bloques_sel:
                        mostrar_alerta("Seleccione al menos una franja horaria.", "warning", "fa-triangle-exclamation")
                    elif not torres:
                        mostrar_alerta("Restricción de datos: No se encontró la columna 'TORRE'.", "error", "fa-circle-xmark")
                    elif 'HR/DIA' not in df.columns:
                        mostrar_alerta("Restricción de datos: Faltan registros horarios ('HR/DIA').", "error", "fa-circle-xmark")
                    elif 'AULA' not in df.columns:
                        mostrar_alerta("Restricción de datos: No hay identificadores de recintos ('AULA').", "error", "fa-circle-xmark")
                    else:
                        dias_validos = [d for d in dias_sel if d in df.columns]
                        if dias_validos:
                            df_limpio = df.copy()
                            df_limpio['TORRE_CLEAN'] = df_limpio['TORRE'].astype(str).str.upper().str.strip()
                            df_limpio['HR_CLEAN'] = df_limpio['HR/DIA'].astype(str).str.replace(" ", "")
                            df_torre = df_limpio[df_limpio['TORRE_CLEAN'] == torre_sel].copy()
                            
                            aulas_comunes = None
                            for dia_actual in dias_validos:
                                df_torre['ESTADO'] = df_torre[dia_actual].astype(str).str.upper().str.strip()
                                for bloque in bloques_sel:
                                    if bloque in todos_los_bloques:
                                        for b in todos_los_bloques[bloque]:
                                            b_clean = b.replace(" ", "")
                                            aulas_libres_bloque = set(df_torre[(df_torre['HR_CLEAN'] == b_clean) & ((df_torre['ESTADO'] == 'LIBRE') | (df_torre['ESTADO'] == 'NAN') | (df_torre['ESTADO'] == ''))]['AULA'].dropna())
                                            if aulas_comunes is None:
                                                aulas_comunes = aulas_libres_bloque
                                            else:
                                                aulas_comunes = aulas_comunes.intersection(aulas_libres_bloque)
                                            
                            aulas_comunes = sorted(list(aulas_comunes)) if aulas_comunes else []
                            
                            if "Específica" in modo_busqueda and fecha_sel:
                                reservas = cargar_reservas()
                                aulas_finales = []
                                for aula in aulas_comunes:
                                    esta_reservada = False
                                    for res in reservas:
                                        try:
                                            res_inicio = datetime.date.fromisoformat(res['fecha_inicio'])
                                            res_fin = datetime.date.fromisoformat(res['fecha_fin'])
                                            if res_inicio <= fecha_sel <= res_fin:
                                                t_res = str(res['torre']).upper().strip()
                                                a_res = str(res['aula']).upper().strip()
                                                a_check = str(aula).upper().strip()
                                                
                                                if t_res == torre_sel.upper().strip() and a_res == a_check:
                                                    if any(b in bloques_sel for b in res['bloques']):
                                                        esta_reservada = True
                                                        break
                                        except Exception:
                                            pass
                                    
                                    if not esta_reservada:
                                        aulas_finales.append(aula)
                                
                                aulas_comunes = aulas_finales

                            if aulas_comunes:
                                st.markdown(f'<div class="metric-container"><i class="fa-solid fa-check-double text-blue"></i> Capacidad Disponible: {len(aulas_comunes)} Recintos</div>', unsafe_allow_html=True)
                                cols_grid = st.columns(5)
                                for idx, aula in enumerate(aulas_comunes):
                                    with cols_grid[idx % 5]:
                                        st.markdown(f'<div class="tarjeta-aula"><i class="fa-solid fa-chalkboard text-orange" style="margin-right:5px;"></i> {aula}</div>', unsafe_allow_html=True)
                            else:
                                mostrar_alerta(f"Capacidad del recinto agotada para la franja seleccionada en la torre o edificio {torre_sel}.", "info", "fa-circle-info")

            # --- PESTAÑA 2: BUSQUEDA NORMAL ---
            with tab_busqueda:
                st.markdown("### <i class='fa-solid fa-magnifying-glass text-orange'></i> Consulta de Asignaciones", unsafe_allow_html=True)
                docentes = set()
                materias = set()
                for dia in dias_presentes:
                    for val in df[dia].dropna().astype(str).str.upper().str.strip():
                        if val not in ('NAN', 'LIBRE', ''):
                            m_doc = re_docente.search(val)
                            if m_doc: docentes.add(re.sub(r'[-]+$', '', m_doc.group(1)).strip())
                            m_mat = re_materia.search(val)
                            if m_mat: materias.add(re.sub(r'[-]+$', '', m_mat.group(1)).strip())
                
                c1, c2 = st.columns(2)
                with c1: sel_docente = st.selectbox("Docente Asignado:", [""] + sorted(list(docentes)))
                with c2: sel_materia = st.selectbox("Unidad Académica:", [""] + sorted(list(materias)))
                
                col_btn, _, _ = st.columns([1,1,1])
                with col_btn:
                    buscar_clases_btn = st.button("Consultar Asignación", type="primary")
                
                if buscar_clases_btn:
                    resultados = []
                    for index, row in df.iterrows():
                        for dia in dias_presentes:
                            val = str(row.get(dia, "")).upper().strip()
                            if val not in ('NAN', 'LIBRE', 'NONE', ''):
                                c_doc = not sel_docente or (re_docente.search(val) and sel_docente in re_docente.search(val).group(1))
                                c_mat = not sel_materia or (re_materia.search(val) and sel_materia in re_materia.search(val).group(1))
                                if c_doc and c_mat and (sel_docente or sel_materia):
                                    resultados.append({"Día": dia, "Horario": row.get("HR/DIA", ""), "Planta Física": row.get("TORRE", ""), "Recinto": row.get("AULA", ""), "Anotación de Registro": val})
                    if resultados:
                        st.dataframe(pd.DataFrame(resultados), use_container_width=True, hide_index=True)
                    elif sel_docente or sel_materia:
                        mostrar_alerta("Sin registros concordantes en la base de datos.", "info", "fa-circle-info")
                    else:
                        mostrar_alerta("Seleccione al menos un parámetro de búsqueda.", "warning", "fa-triangle-exclamation")

            # --- PESTAÑA 3: AUDITORÍA DE HORARIOS ---
            with tab_auditoria:
                st.markdown("### <i class='fa-solid fa-clipboard-check text-blue'></i> Reporte Analítico de Conflictos", unsafe_allow_html=True)
                st.write("Herramienta estructurada para el análisis y detección temprana de solapamientos e irregularidades operativas de docentes en los horarios emitidos.")
                
                col_btn, _, _ = st.columns([1,1,1])
                with col_btn:
                    auditar_btn = st.button("Ejecutar Auditoría Profunda", type="primary")
                
                if auditar_btn:
                    mapa_asignaciones = {}
                    
                    for index, row in df.iterrows():
                        hora = str(row.get("HR/DIA", "")).strip()
                        torre = str(row.get("TORRE", "")).strip()
                        aula = str(row.get("AULA", "")).strip()
                        
                        for dia in dias_presentes:
                            val = str(row.get(dia, "")).upper().strip()
                            if val not in ('NAN', 'LIBRE', 'NONE', ''):
                                m_doc = re_docente.search(val)
                                if m_doc:
                                    doc = re.sub(r'[-]+$', '', m_doc.group(1)).strip()
                                    if doc:
                                        key = (dia, hora, doc)
                                        if key not in mapa_asignaciones:
                                            mapa_asignaciones[key] = []
                                        mapa_asignaciones[key].append(f"{torre} - {aula}")
                    
                    conflictos = []
                    for (dia, hora, doc), aulas_asignadas in mapa_asignaciones.items():
                        aulas_unicas = list(set(aulas_asignadas))
                        if len(aulas_unicas) > 1:
                            conflictos.append({
                                "Día": dia,
                                "Hora": hora,
                                "Docente": doc,
                                "Aulas en Conflicto": " y ".join(aulas_unicas)
                            })
                            
                    if conflictos:
                        mostrar_alerta(f"Sistema emitió aviso de nivel rojo: {len(conflictos)} contingencias detectadas.", "error", "fa-circle-exclamation")
                        for conf in conflictos:
                            st.markdown(f"""
                            <div class="alerta-choque">
                                <strong>Día:</strong> {conf['Día']} | <strong>Hora:</strong> {conf['Hora']} <br>
                                <strong>Identificador de Docente:</strong> {conf['Docente']} <br>
                                <strong>Inconsistencia Informada:</strong> Conflicto de doble asignación en: {conf['Aulas en Conflicto']}
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        mostrar_alerta("Validación satisfactoria. Cero incidencias reportadas en la actual estructura.", "success", "fa-check-double")

            # --- PESTAÑA 4: DÓNDE ESTÁ AHORA ---
            with tab_ahora:
                st.markdown("### <i class='fa-solid fa-location-dot text-orange'></i> Panel de Control Operativo", unsafe_allow_html=True)
                
                modo_prueba = st.checkbox("Activar Entorno de Pruebas (Simulación Predictiva)")
                
                if modo_prueba:
                    col_p1, col_p2 = st.columns(2)
                    with col_p1:
                        dia_actual = st.selectbox("Parámetro - Día:", dias_presentes) if dias_presentes else st.selectbox("Parámetro - Día:", dias_semana)
                    with col_p2:
                        hora_actual = st.time_input("Parámetro - Tiempo:", value=datetime.time(9, 0))
                else:
                    now = datetime.datetime.now()
                    try:
                        dia_actual = dias_semana[now.weekday()]
                    except:
                        dia_actual = "LUNES"
                    hora_actual = now.time()
                    mostrar_alerta(f"Sincronizado: Servidor operando sobre la matriz del {dia_actual}, a las {hora_actual.strftime('%H:%M')}", "info", "fa-clock")
                
                if dia_actual not in dias_presentes:
                    mostrar_alerta("Los parámetros ingresados no cuentan con despliegue en la base de datos.", "warning", "fa-triangle-exclamation")
                else:
                    lista_docentes = sorted(list(docentes))
                    docente_buscar = st.selectbox("Filtro Activo de Seguimiento (Docente):", [""] + lista_docentes)
                    
                    if docente_buscar:
                        encontrado = False
                        for index, row in df.iterrows():
                            hora_bloque = str(row.get("HR/DIA", "")).strip()
                            if en_rango_horario(hora_bloque, hora_actual):
                                val_celda = str(row.get(dia_actual, "")).upper().strip()
                                
                                if val_celda not in ('NAN', 'LIBRE', 'NONE', ''):
                                    m_doc = re_docente.search(val_celda)
                                    if m_doc and docente_buscar in val_celda:
                                        torre = row.get("TORRE", "")
                                        aula = row.get("AULA", "")
                                        mostrar_alerta(f"Confirmación de Asignación Física: {docente_buscar}", "success", "fa-user-check")
                                        st.markdown(f'<div class="metric-container"><i class="fa-solid fa-map-pin text-orange"></i> Planta Operativa: {torre} | Identificador de Recinto: {aula}</div>', unsafe_allow_html=True)
                                        st.write(f"**Referencia Descriptiva:** {val_celda}")
                                        st.write(f"**Intervalo de Ocupación:** {hora_bloque}")
                                        encontrado = True
                                        break
                        
                        if not encontrado:
                            mostrar_alerta("Sin actividad reportada en la franja transitoria actual respecto de la solicitud de búsqueda.", "info", "fa-circle-info")

            # --- PESTAÑA 5: GESTIÓN DE RESERVAS ---
            with tab_reservas:
                st.markdown("### <i class='fa-solid fa-calendar-days text-blue'></i> Excepciones Operativas", unsafe_allow_html=True)
                st.write("Administración integral de asignaciones suplementarias y bloqueos temporales.")
                
                reservas_actuales = cargar_reservas()
                
                with st.form("form_nueva_reserva", clear_on_submit=True):
                    st.subheader("Captura de Nuevo Registro")
                    col_r1, col_r2 = st.columns(2)
                    with col_r1:
                        motivo = st.text_input("Justificación Documental")
                        torre_reserva = st.selectbox("Planta Física", torres) if torres else st.selectbox("Torre", ["N/A"])
                        aulas_unicas = sorted(list(df['AULA'].dropna().astype(str).unique())) if 'AULA' in df.columns else ["N/A"]
                        aula_reserva = st.selectbox("Salón Destino", aulas_unicas)
                        
                    with col_r2:
                        fecha_inicio = st.date_input("Día de Activación")
                        fecha_fin = st.date_input("Día de Término", value=fecha_inicio)
                        
                        todos_los_bloques_res = {}
                        todos_los_bloques_res.update(MAPEO_REGULAR)
                        todos_los_bloques_res.update(MAPEO_SABADO)
                        todos_los_bloques_res.update(MAPEO_DOMINGO)
                        nombres_bloques_res = list(dict.fromkeys(list(MAPEO_REGULAR.keys()) + list(MAPEO_SABADO.keys()) + list(MAPEO_DOMINGO.keys())))
                        
                        bloques_reserva = st.multiselect("Esquema de Carga Horaria", nombres_bloques_res)
                    
                    submit_reserva = st.form_submit_button("Efectuar Bloqueo de Recinto", type="primary")
                    
                    if submit_reserva:
                        if not motivo or not bloques_reserva:
                            mostrar_alerta("Campos compulsorios no cumplimentados. Se requiere Justificación y Esquema.", "error", "fa-circle-xmark")
                        elif fecha_fin < fecha_inicio:
                            mostrar_alerta("Discordancia de validación: La fecha de término es previa a su activación.", "error", "fa-circle-xmark")
                        else:
                            nueva_reserva = {
                                "id": str(datetime.datetime.now().timestamp()),
                                "motivo": motivo,
                                "torre": torre_reserva,
                                "aula": aula_reserva,
                                "fecha_inicio": fecha_inicio.isoformat(),
                                "fecha_fin": fecha_fin.isoformat(),
                                "bloques": bloques_reserva
                            }
                            reservas_actuales.append(nueva_reserva)
                            guardar_reservas(reservas_actuales)
                            st.success("Contingencia anexada al registro principal debidamente.")
                            st.rerun()
                            
                st.markdown("---")
                st.subheader("Registros Hábiles en Matriz")
                if reservas_actuales:
                    for res in reservas_actuales:
                        with st.container():
                            c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 3, 1])
                            c1.markdown(f"**{res['motivo']}**")
                            c2.markdown(f"{res['torre']} - {res['aula']}")
                            c3.markdown(f"{res['fecha_inicio']} a {res['fecha_fin']}")
                            c4.markdown(f"{', '.join(res['bloques'])}")
                            if c5.button("Revocar", key=f"del_{res['id']}"):
                                reservas_actuales = [r for r in reservas_actuales if r['id'] != res['id']]
                                guardar_reservas(reservas_actuales)
                                st.rerun()
                        st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)
                else:
                    mostrar_alerta("Sin registros subyacentes operativos.", "info", "fa-circle-info")

    except Exception as e:
        import traceback
        mostrar_alerta(f"Anomalía severa de ejecución en el aplicativo. Origen de evento adverso: {e}", "error", "fa-bug")
        st.code(traceback.format_exc())
