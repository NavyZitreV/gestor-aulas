import streamlit as st
import pandas as pd
import os
import re
import datetime
import json

# 1. Configuración de página principal
st.set_page_config(layout="wide", page_title="Buscador de Aulas", page_icon="🏫")

# 2. Estilos personalizados Premium (CSS)
st.markdown("""
<style>
    .titulo-principal { font-size: 2.8rem; font-weight: bold; color: #1E3A8A; margin-bottom: 5px; }
    .subtitulo { font-size: 1.2rem; color: #4B5563; margin-bottom: 30px; }
    .tarjeta-aula {
        background-color: #F8FAFC; border-left: 5px solid #3B82F6; padding: 15px; 
        border-radius: 8px; margin-bottom: 15px; font-weight: 600; font-size: 1.1rem;
        color: #1F2937; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .metric-container {
        background-color: #D1FAE5; color: #065F46; padding: 15px 25px;
        border-radius: 10px; font-size: 1.5rem; font-weight: bold;
        display: inline-block; margin-bottom: 25px; border: 1px solid #A7F3D0; box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .alerta-choque {
        background-color: #FEE2E2; color: #991B1B; padding: 15px;
        border-radius: 8px; margin-bottom: 10px; border-left: 5px solid #EF4444;
    }
</style>
""", unsafe_allow_html=True)

# Directorio para base de datos
DATA_DIR = "datos_horarios"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

RESERVAS_FILE = os.path.join(DATA_DIR, "reservas_temporales.json")

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
st.sidebar.header("📂 Base de Datos")
st.sidebar.info("La plataforma guardará el último archivo que subas para que no tengas que subirlo de nuevo.")
uploaded_file = st.sidebar.file_uploader("Actualizar archivo de horarios (.xlsx, .csv)", type=["xlsx", "csv"])

if uploaded_file is not None:
    for f in os.listdir(DATA_DIR):
        os.remove(os.path.join(DATA_DIR, f))
    
    ruta_guardado = os.path.join(DATA_DIR, uploaded_file.name)
    with open(ruta_guardado, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.sidebar.success("✅ ¡Archivo guardado exitosamente!")

archivo_activo = obtener_archivo_guardado()

if archivo_activo:
    st.sidebar.success(f"📁 Usando datos locales de: {os.path.basename(archivo_activo)}")

st.markdown('<p class="titulo-principal">🏫 Gestor Académico UNICEN</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitulo">Búsqueda, auditoría de choques y seguimiento en tiempo real.</p>', unsafe_allow_html=True)

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
    except Exception as e:
        print(f"Error parsing time range: {hora_str} - {e}")
    return False

@st.cache_data
def cargar_datos(ruta_archivo):
    try:
        if ruta_archivo.endswith('.csv'):
            df = pd.read_csv(ruta_archivo)
        else:
            df = pd.read_excel(ruta_archivo)
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        return None
    
    df.columns = df.columns.astype(str).str.strip().str.upper()
    return df

if not archivo_activo:
    st.info("👋 ¡Hola! Para empezar, por favor sube el archivo Excel o CSV de horarios del semestre en el menú lateral.")
else:
    try:
        with st.spinner("Procesando base de datos guardada..."):
            df = cargar_datos(archivo_activo)
        
        if df is not None:
            dias_semana = ["LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES", "SABADO", "DOMINGO"]
            
            # Verificar si la columna TORRE existe antes de usarla
            if 'TORRE' in df.columns:
                torres = sorted([t for t in df['TORRE'].dropna().astype(str).str.upper().str.strip().unique() if t])
            else:
                st.warning("⚠️ No se encontró la columna 'TORRE' en el archivo. La búsqueda por torre no funcionará correctamente.")
                torres = []
                
            dias_presentes = [d for d in dias_semana if d in df.columns]
            
            re_docente = re.compile(r'DOCENTE\s*:([^:]+)(?:MATERIA\s*:|GRUPO\s*:|$)')
            re_materia = re.compile(r'MATERIA\s*:([^:]+)(?:GRUPO\s*:|DOCENTE\s*:|$)')
            
            # 4. Creación de las 4 Pestañas
            tab_libres, tab_busqueda, tab_auditoria, tab_ahora, tab_reservas = st.tabs([
                "🏫 Aulas Libres", 
                "🔎 Docentes/Materias", 
                "⚠️ Auditoría de Horarios", 
                "📍 ¿Dónde está ahora?",
                "🗓️ Gestión de Reservas"
            ])
            
            # --- PESTAÑA 1: AULAS LIBRES ---
            with tab_libres:
                col1, col2, col3 = st.columns(3)
                with col1:
                    fecha_sel = st.date_input("📅 Fecha a buscar:")
                    dias_map = {0: "LUNES", 1: "MARTES", 2: "MIERCOLES", 3: "JUEVES", 4: "VIERNES", 5: "SABADO", 6: "DOMINGO"}
                    dia_busqueda = dias_map[fecha_sel.weekday()]
                    st.info(f"Día de la semana deducido: **{dia_busqueda}**")
                    dias_sel = [dia_busqueda] if dia_busqueda in dias_presentes else []
                with col2:
                    torre_sel = st.selectbox("🏢 Torre / Edificio:", torres) if torres else st.selectbox("🏢 Torre / Edificio:", ["N/A"])
                with col3:
                    todos_los_bloques = {}
                    todos_los_bloques.update(MAPEO_REGULAR)
                    todos_los_bloques.update(MAPEO_SABADO)
                    todos_los_bloques.update(MAPEO_DOMINGO)
                    nombres_bloques = list(dict.fromkeys(list(MAPEO_REGULAR.keys()) + list(MAPEO_SABADO.keys()) + list(MAPEO_DOMINGO.keys())))
                    bloques_sel = st.multiselect("⏱️ Franja(s) Horaria(s):", nombres_bloques, default=[nombres_bloques[0]] if nombres_bloques else [])
                    
                st.markdown("<br>", unsafe_allow_html=True)
                
                if st.button("🔍 Buscar Aulas Libres", use_container_width=True, type="primary"):
                    st.markdown("<hr style='margin-top:0px; margin-bottom:25px;'>", unsafe_allow_html=True)
                    if not dias_sel:
                        st.warning(f"⚠️ El día deducido ({dia_busqueda}) no tiene horarios registrados en la base de datos.")
                    elif not bloques_sel:
                        st.warning("⚠️ Selecciona al menos una franja horaria.")
                    elif not torres:
                        st.error("No se puede realizar la búsqueda porque falta la columna 'TORRE'.")
                    elif 'HR/DIA' not in df.columns:
                        st.error("No se puede realizar la búsqueda porque falta la columna 'HR/DIA'.")
                    elif 'AULA' not in df.columns:
                        st.error("No se puede realizar la búsqueda porque falta la columna 'AULA'.")
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
                            
                            # Filtro Maestro: Cruce con Reservas Temporales
                            reservas = cargar_reservas()
                            aulas_finales = []
                            for aula in aulas_comunes:
                                esta_reservada = False
                                for res in reservas:
                                    try:
                                        res_inicio = datetime.date.fromisoformat(res['fecha_inicio'])
                                        res_fin = datetime.date.fromisoformat(res['fecha_fin'])
                                        if res_inicio <= fecha_sel <= res_fin:
                                            # Chequear misma torre y aula
                                            t_res = str(res['torre']).upper().strip()
                                            a_res = str(res['aula']).upper().strip()
                                            a_check = str(aula).upper().strip()
                                            
                                            if t_res == torre_sel.upper().strip() and a_res == a_check:
                                                # Chequear solapamiento en franjas horarias
                                                if any(b in bloques_sel for b in res['bloques']):
                                                    esta_reservada = True
                                                    break
                                    except Exception as e:
                                        pass
                                
                                if not esta_reservada:
                                    aulas_finales.append(aula)
                            
                            aulas_comunes = aulas_finales

                            if aulas_comunes:
                                st.markdown(f'<div class="metric-container">✅ {len(aulas_comunes)} Aulas Disponibles</div>', unsafe_allow_html=True)
                                cols_grid = st.columns(5)
                                for idx, aula in enumerate(aulas_comunes):
                                    with cols_grid[idx % 5]:
                                        st.markdown(f'<div class="tarjeta-aula">{aula}</div>', unsafe_allow_html=True)
                            else:
                                st.info(f"😕 No hay aulas ininterrumpidamente libres para la combinación elegida en la {torre_sel}.")

            # --- PESTAÑA 2: BUSQUEDA NORMAL ---
            with tab_busqueda:
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
                with c1: sel_docente = st.selectbox("👨🏫 Docente:", [""] + sorted(list(docentes)))
                with c2: sel_materia = st.selectbox("📚 Materia:", [""] + sorted(list(materias)))
                
                if st.button("Buscar Clases", type="primary"):
                    resultados = []
                    for index, row in df.iterrows():
                        for dia in dias_presentes:
                            val = str(row.get(dia, "")).upper().strip()
                            if val not in ('NAN', 'LIBRE', 'NONE', ''):
                                c_doc = not sel_docente or (re_docente.search(val) and sel_docente in re_docente.search(val).group(1))
                                c_mat = not sel_materia or (re_materia.search(val) and sel_materia in re_materia.search(val).group(1))
                                if c_doc and c_mat and (sel_docente or sel_materia):
                                    resultados.append({"Día": dia, "Horario": row.get("HR/DIA", ""), "Torre": row.get("TORRE", ""), "Aula": row.get("AULA", ""), "Detalle": val})
                    if resultados:
                        st.dataframe(pd.DataFrame(resultados), use_container_width=True, hide_index=True)
                    elif sel_docente or sel_materia:
                        st.info("No se encontraron clases.")
                    else:
                        st.warning("Por favor, selecciona un docente o una materia para buscar.")

            # --- PESTAÑA 3: AUDITORÍA DE HORARIOS (NUEVO) ---
            with tab_auditoria:
                st.markdown("### ⚠️ Auditoría de Solapamientos")
                st.write("Esta herramienta escanea la base de datos en busca de docentes que tengan asignadas dos aulas diferentes a la misma hora exacta.")
                
                if st.button("🚀 Iniciar Auditoría Completa", type="primary"):
                    mapa_asignaciones = {}
                    
                    # Recorrer todo el excel
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
                                        # Llave única: Día + Hora + Docente
                                        key = (dia, hora, doc)
                                        if key not in mapa_asignaciones:
                                            mapa_asignaciones[key] = []
                                        mapa_asignaciones[key].append(f"{torre} - {aula}")
                    
                    # Detectar conflictos (cuando un docente tiene >1 aula en el mismo bloque)
                    conflictos = []
                    for (dia, hora, doc), aulas_asignadas in mapa_asignaciones.items():
                        # Eliminamos duplicados por si acaso el excel tiene la misma aula dos veces
                        aulas_unicas = list(set(aulas_asignadas))
                        if len(aulas_unicas) > 1:
                            conflictos.append({
                                "Día": dia,
                                "Hora": hora,
                                "Docente": doc,
                                "Aulas en Conflicto": " Y ".join(aulas_unicas)
                            })
                            
                    if conflictos:
                        st.error(f"🚨 Se han detectado {len(conflictos)} conflictos de horario (solapamientos).")
                        for conf in conflictos:
                            st.markdown(f"""
                            <div class="alerta-choque">
                                <strong>Día:</strong> {conf['Día']} | <strong>Hora:</strong> {conf['Hora']} <br>
                                <strong>Docente:</strong> {conf['Docente']} <br>
                                <strong>Error:</strong> Asignado simultáneamente en: {conf['Aulas en Conflicto']}
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.success("✅ ¡Auditoría superada! No se detectaron choques de horario en la asignación de docentes.")

            # --- PESTAÑA 4: DÓNDE ESTÁ AHORA (NUEVO) ---
            with tab_ahora:
                st.markdown("### 📍 Seguimiento en Tiempo Real")
                
                # Opciones de prueba
                modo_prueba = st.checkbox("⚙️ Habilitar modo de simulación (para probar fuera de horario de clases)")
                
                if modo_prueba:
                    col_p1, col_p2 = st.columns(2)
                    with col_p1:
                        dia_actual = st.selectbox("Simular Día:", dias_presentes) if dias_presentes else st.selectbox("Simular Día:", dias_semana)
                    with col_p2:
                        hora_actual = st.time_input("Simular Hora:", value=datetime.time(9, 0))
                else:
                    now = datetime.datetime.now()
                    try:
                        dia_actual = dias_semana[now.weekday()]
                    except:
                        dia_actual = "LUNES"
                    hora_actual = now.time()
                    st.info(f"🕒 Tiempo real del sistema: **{dia_actual}**, **{hora_actual.strftime('%H:%M')}**")
                
                if dia_actual not in dias_presentes:
                    st.warning("El día actual no tiene horarios registrados en la base de datos.")
                else:
                    lista_docentes = sorted(list(docentes))
                    docente_buscar = st.selectbox("Selecciona al docente para ver dónde está ahora:", [""] + lista_docentes)
                    
                    if docente_buscar:
                        encontrado = False
                        # Buscar en las filas donde la hora actual coincide
                        for index, row in df.iterrows():
                            hora_bloque = str(row.get("HR/DIA", "")).strip()
                            # hora_bloque format from excel might be "08:00 - 08:45"
                            # the `en_rango_horario` function checks if `hora_actual` is in `hora_bloque`.
                            if en_rango_horario(hora_bloque, hora_actual):
                                val_celda = str(row.get(dia_actual, "")).upper().strip()
                                
                                if val_celda not in ('NAN', 'LIBRE', 'NONE', ''):
                                    m_doc = re_docente.search(val_celda)
                                    if m_doc and docente_buscar in val_celda:
                                        torre = row.get("TORRE", "")
                                        aula = row.get("AULA", "")
                                        st.success(f"📍 **{docente_buscar}** se encuentra actualmente en:")
                                        st.markdown(f'<div class="metric-container">🏢 {torre} | 🚪 Aula {aula}</div>', unsafe_allow_html=True)
                                        st.write(f"**Detalle de clase:** {val_celda}")
                                        st.write(f"**Bloque de hora:** {hora_bloque}")
                                        encontrado = True
                                        break
                        
                        if not encontrado:
                            st.info(f"😴 El docente **{docente_buscar}** no tiene clases asignadas en este preciso momento ({hora_actual.strftime('%H:%M')}).")

            # --- PESTAÑA 5: GESTIÓN DE RESERVAS (NUEVO) ---
            with tab_reservas:
                st.markdown("### 🗓️ Gestión de Reservas Temporales")
                st.write("Registra aulas ocupadas temporalmente por ferias, reposiciones o eventos especiales.")
                
                reservas_actuales = cargar_reservas()
                
                with st.form("form_nueva_reserva", clear_on_submit=True):
                    st.subheader("Nueva Reserva")
                    col_r1, col_r2 = st.columns(2)
                    with col_r1:
                        motivo = st.text_input("Motivo (ej. Feria, Reposición)")
                        torre_reserva = st.selectbox("Torre", torres) if torres else st.selectbox("Torre", ["N/A"])
                        aulas_unicas = sorted(list(df['AULA'].dropna().astype(str).unique())) if 'AULA' in df.columns else ["N/A"]
                        aula_reserva = st.selectbox("Aula", aulas_unicas)
                        
                    with col_r2:
                        fecha_inicio = st.date_input("Fecha de Inicio")
                        fecha_fin = st.date_input("Fecha de Fin", value=fecha_inicio)
                        
                        todos_los_bloques_res = {}
                        todos_los_bloques_res.update(MAPEO_REGULAR)
                        todos_los_bloques_res.update(MAPEO_SABADO)
                        todos_los_bloques_res.update(MAPEO_DOMINGO)
                        nombres_bloques_res = list(dict.fromkeys(list(MAPEO_REGULAR.keys()) + list(MAPEO_SABADO.keys()) + list(MAPEO_DOMINGO.keys())))
                        
                        bloques_reserva = st.multiselect("Franjas Horarias Afectadas", nombres_bloques_res)
                    
                    submit_reserva = st.form_submit_button("Guardar Reserva", type="primary")
                    
                    if submit_reserva:
                        if not motivo or not bloques_reserva:
                            st.error("El motivo y las franjas horarias son obligatorios.")
                        elif fecha_fin < fecha_inicio:
                            st.error("La fecha de fin no puede ser anterior a la de inicio.")
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
                            st.success(f"Reserva para '{motivo}' guardada exitosamente.")
                            st.rerun()
                            
                st.markdown("---")
                st.subheader("Reservas Activas")
                if reservas_actuales:
                    for res in reservas_actuales:
                        with st.container():
                            c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 3, 1])
                            c1.markdown(f"**{res['motivo']}**")
                            c2.markdown(f"🏢 {res['torre']} - 🚪 {res['aula']}")
                            c3.markdown(f"📅 {res['fecha_inicio']} a {res['fecha_fin']}")
                            c4.markdown(f"⏱️ {', '.join(res['bloques'])}")
                            if c5.button("Eliminar", key=f"del_{res['id']}"):
                                reservas_actuales = [r for r in reservas_actuales if r['id'] != res['id']]
                                guardar_reservas(reservas_actuales)
                                st.rerun()
                        st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)
                else:
                    st.info("No hay reservas temporales activas.")

    except Exception as e:
        import traceback
        st.error(f"Error procesando la información del archivo: {e}")
        st.code(traceback.format_exc())
