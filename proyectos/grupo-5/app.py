import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

# ==============================================================================
# 1. CONFIGURACIÓN DE LA INTERFAZ
# ==============================================================================
st.set_page_config(
    page_title="Sistema de Gestión de Crisis - Biobío",
    page_icon="🚨",
    layout="wide"
)

st.title("🚨 Sistema Integrado de Alertas, Mitigación y Planes de Evacuación")
st.markdown("### Centro de Operaciones de Emergencia (COE) | SIC 2026 - Grupo 5")

albergues_biobio = {
    "Concepción": "Gimnasio Municipal (Av. Collao 525) - Abierto 24/7",
    "Los Ángeles": "Liceo Comercial (Ricardo Vicuña 310) - Zona de Resguardo",
    "Talcahuano": "Coliseo La Tortuga (Blanco Encalada 450) - Centro de Acopio",
    "Coronel": "Escuela Básica Manuel Montt - Habilitado como Refugio",
    "Hualpén": "Liceo Pedro del Río Zañartu - Zona Segura de Evacuación",
    "Chiguayante": "Gimnasio Machasa - Punto de Encuentro Familiar",
    "San Pedro de La Paz": "Colegio Concepción (San Pedro) - Albergue Activo",
    "Penco": "Escuela Patricio Lynch - Zona de Resguardo Temporal",
    "Tomé": "Internado Bellavista - Centro de Atención de Emergencias",
    "Lota": "Liceo Carlos Cousiño - Zona de Seguridad Civil"
}

# ==============================================================================
# 2. CARGA ULTRA-ROBUSTA DE DATOS (MÉTODOS DE RESPALDO MÚLTIPLES)
# ==============================================================================
@st.cache_data
def inicializar_sistema():
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    archivo_comunas = "Latitud - Longitud Chile.csv"
    archivo_bosques = "bosques_chile_excel.csv"
    
    rutas_comunas_posibles = [
        os.path.join(base_path, "data", archivo_comunas),
        os.path.join(base_path, archivo_comunas),
        archivo_comunas
    ]
    
    rutas_bosques_posibles = [
        os.path.join(base_path, "data", archivo_bosques),
        os.path.join(base_path, archivo_bosques),
        archivo_bosques
    ]
    
    df_c = None
    for r in rutas_comunas_posibles:
        if os.path.exists(r):
            df_c = pd.read_csv(r)
            break
            
    df_b = None
    for r in rutas_bosques_posibles:
        if os.path.exists(r):
            df_b = pd.read_csv(r, sep=';')
            break

    if df_c is None:
        df_c = pd.DataFrame({
            'Comuna': ['Concepción', 'Los Ángeles', 'Talcahuano', 'Coronel', 'Hualpén', 'Chiguayante', 'San Pedro de la Paz', 'Penco', 'Tomé', 'Lota'],
            'Región': ['Biobío'] * 10,
            'Provincia': ['Concepción', 'Biobío', 'Concepción', 'Concepción', 'Concepción', 'Concepción', 'Concepción', 'Concepción', 'Concepción', 'Concepción'],
            'Población Año 2017': ['223.574', '202.331', '151.749', '116.262', '91.773', '85.938', '131.808', '47.367', '54.537', '43.535'],
            'Latitud (Decimal)': [-36.8150, -37.4697, -36.7358, -36.9819, -36.7932, -36.9089, -36.8639, -36.7419, -36.6167, -37.0889],
            'Longitud (decimal)': [-73.0289, -72.3508, -73.1050, -73.1569, -73.1678, -73.0278, -73.1078, -72.9978, -72.9500, -73.1550]
        })

    if df_b is None:
        vegetacion = {
            "plantacion_forestal_ha": 875178.4,
            "bosque_nativo_ha": 597572.7,
            "bosque_mixto_ha": 51635.9,
            "humedales_ha": 10172.8,
            "bosques_total_ha": 1524387.0
        }
    else:
        df_b['Región'] = df_b['Región'].str.strip()
        def limpiar_numero_chileno(val):
            if pd.isna(val): return 0.0
            return float(str(val).strip().replace('.', '').replace(',', '.'))
        
        row_biobio = df_b[df_b['Región'] == 'Biobío'].iloc[0]
        vegetacion = {
            "plantacion_forestal_ha": limpiar_numero_chileno(row_biobio['Plantación Forestal']),
            "bosque_nativo_ha": limpiar_numero_chileno(row_biobio['Bosque Nativo']),
            "bosque_mixto_ha": limpiar_numero_chileno(row_biobio['Bosque Mixto']),
            "humedales_ha": 10172.8,
            "bosques_total_ha": limpiar_numero_chileno(row_biobio['Total'])
        }

    df_c['Región_Clean'] = df_c['Región'].astype(str).str.lower()
    df_comunas_biobio = df_c[df_c['Región_Clean'].str.contains('bio', na=False)].copy()
    
    df_comunas_biobio['comuna'] = df_comunas_biobio['Comuna'].str.strip()
    df_comunas_biobio['latitud_decimal'] = pd.to_numeric(df_comunas_biobio['Latitud (Decimal)'], errors='coerce')
    df_comunas_biobio['longitud_decimal'] = pd.to_numeric(df_comunas_biobio['Longitud (decimal)'], errors='coerce')
    
    df_comunas_biobio['poblacion_2017'] = df_comunas_biobio['Población Año 2017'].astype(str).str.replace(',', '').str.replace('.', '').astype(int)
    df_comunas_biobio = df_comunas_biobio.dropna(subset=['latitud_decimal', 'longitud_decimal'])
    
    return df_comunas_biobio, vegetacion

df_comunas, datos_biobio = inicializar_sistema()

# ==============================================================================
# 3. PANEL LATERAL: CONTROLES DE CRISIS
# ==============================================================================
st.sidebar.header("🕹️ Panel de Control del Incidente")
comuna_origen = st.sidebar.selectbox("📍 Comuna del Foco Inicial", sorted(df_comunas['comuna'].unique()))

st.sidebar.markdown("---")
st.sidebar.header("🧭 Variables Atmosféricas")
dir_viento = st.sidebar.selectbox("💨 Dirección hacia donde sopla el Viento", 
                                  ["Norte", "Sur", "Este", "Oeste", "Omnidireccional (Sin control)"])
viento = st.sidebar.slider("💨 Velocidad del Viento (km/h)", 5, 110, 35)
temperatura = st.sidebar.slider("🌡️ Temperatura (°C)", 15, 45, 34)
humedad = st.sidebar.slider("💧 Humedad Relativa (%)", 5, 95, 18)
pendiente = st.sidebar.slider("⛰️ Pendiente media del Terreno (%)", 0, 50, 12)
horas_ev = st.sidebar.slider("⏳ Ventana de Simulación (Horas)", 1, 12, 4)

# ==============================================================================
# 4. ALGORITMO MATEMÁTICO DE PROPAGACIÓN
# ==============================================================================
combustible = (
    (datos_biobio["plantacion_forestal_ha"] * 1.0) +
    (datos_biobio["bosque_mixto_ha"] * 0.8) +
    (datos_biobio["bosque_nativo_ha"] * 0.6)
) / datos_biobio["bosques_total_ha"] * 100

sequedad = 100 - humedad
ip = (0.30 * viento) + (0.30 * combustible) + (0.20 * temperatura) + (0.10 * sequedad) + (0.10 * pendiente)
ip = min(max(ip, 0), 100)

velocidad_fuego = 0.5 + ((ip / 100) * 4.0) + ((viento / 100) * 3.0)
alcance_km = velocidad_fuego * horas_ev

origen_fila = df_comunas[df_comunas['comuna'] == comuna_origen].iloc[0]
lat_o, lon_o = origen_fila['latitud_decimal'], origen_fila['longitud_decimal']

df_comunas['distancia_foco_km'] = np.sqrt((df_comunas['latitud_decimal'] - lat_o)**2 + (df_comunas['longitud_decimal'] - lon_o)**2) * 111.12
df_comunas['dif_lat'] = df_comunas['latitud_decimal'] - lat_o
df_comunas['dif_lon'] = df_comunas['longitud_decimal'] - lon_o

def evaluar_trayectoria(row):
    if row['comuna'] == comuna_origen: return True
    if dir_viento == "Norte" and row['dif_lat'] > 0: return True
    if dir_viento == "Sur" and row['dif_lat'] < 0: return True
    if dir_viento == "Este" and row['dif_lon'] > 0: return True
    if dir_viento == "Oeste" and row['dif_lon'] < 0: return True
    if dir_viento == "Omnidireccional (Sin control)": return True
    return False

df_comunas['En_Trayectoria'] = df_comunas.apply(evaluar_trayectoria, axis=1)

def calcular_probabilidad_y_rango(row):
    if row['comuna'] == comuna_origen:
        return 100.0, "🔴 Extremo (Foco)"
    if row['distancia_foco_km'] <= alcance_km and row['En_Trayectoria']:
        prob = 100 - ((row['distancia_foco_km'] / alcance_km) * 100)
        prob = min(max(prob, 0), 100)
    else:
        prob = 0.0
    if prob >= 75: return float(prob), "🔴 Extremo"
    elif prob >= 50: return float(prob), "🟠 Alto"
    elif prob >= 25: return float(prob), "🟡 Medio"
    else: return float(prob), "🟢 Bajo"

resultados = df_comunas.apply(calcular_probabilidad_y_rango, axis=1)
df_comunas['Probabilidad (%)'] = [round(r[0], 1) for r in resultados]
df_comunas['Clasificacion_Riesgo'] = [r[1] for r in resultados]

# ==============================================================================
# 5. DISEÑO DE PESTAÑAS INTERACTIVAS (UX PROFESIONAL MODULADO)
# ==============================================================================
tab_mapa, tab_tabla, tab_datos, tab_contexto, tab_prevencion = st.tabs([
    "🖥️ Simulador y Mapa de Crisis", 
    "📊 Propagación Estimada entre Comunas", 
    "💾 Descargar Resultado (CSV)",
    "🧪 Contexto y Arquitectura Científica",
    "🌲 Plan de Prevención e Interacción Comunitaria"
])

# ------------------------------------------------------------------------------
# PESTAÑA 1: MAPA Y CONTROLES OPERATIVOS
# ------------------------------------------------------------------------------
with tab_mapa:
    comunas_afectadas = df_comunas[df_comunas['Probabilidad (%)'] >= 25]
    poblacion_afectada = comunas_afectadas['poblacion_2017'].sum()
    viviendas_afectadas = poblacion_afectada / 3.2

    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("Índice de Gravedad (IP)", f"{ip:.1f} %")
    with m2: st.metric("Velocidad de Avance Frontal", f"{velocidad_fuego:.2f} km/h")
    with m3: st.metric("Población Civil en Riesgo", f"{poblacion_afectada:,.0f} hab")
    with m4: st.metric("Estimación de Viviendas en Riesgo", f"{viviendas_afectadas:,.0f} casas")

    st.markdown("---")
    col_mapa, col_graficos = st.columns([2, 1])

    with col_mapa:
        st.subheader("🗺️ Mapeo de Amenaza Territorial y Vector de Viento")
        fig_mapa = px.scatter_mapbox(
            df_comunas, lat="latitud_decimal", lon="longitud_decimal",
            color="Clasificacion_Riesgo", size="poblacion_2017",
            color_discrete_map={
                "🔴 Extremo (Foco)": "#FF0000", "🔴 Extremo": "#D32F2F",
                "🟠 Alto": "#F57C00", "🟡 Medio": "#FBC02D", "🟢 Bajo": "#388E3C"
            },
            category_orders={"Clasificacion_Riesgo": ["🔴 Extremo (Foco)", "🔴 Extremo", "🟠 Alto", "🟡 Medio", "🟢 Bajo"]},
            hover_name="comuna",
            hover_data={"Clasificacion_Riesgo": True, "distancia_foco_km": ":.2f Km", "Probabilidad (%)": True},
            zoom=7.5, center=dict(lat=lat_o, lon=lon_o),
            mapbox_style="open-street-map", height=480
        )
        fig_mapa.update_traces(hovertemplate="<b>%{hovertext}</b><br><br>Riesgo: %{customdata[0]}<br>Distancia: %{customdata[1]}<br>Probabilidad: %{customdata[2]}<br><b>Viento:</b> " + f"{viento} km/h hacia el {dir_viento}<br>")
        fig_mapa.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, legend=dict(title_text="Riesgo SENAPRED", y=0.99, x=0.01, bgcolor="rgba(255, 255, 255, 0.8)"))
        st.plotly_chart(fig_mapa, use_container_width=True, config={'displayModeBar': True, 'scrollZoom': True})

    with col_graficos:
        st.subheader("🌲 Datos forestales usados para el cálculo")
        df_veg = pd.DataFrame({
            'Tipo Cobertura': ['Plantación Forestal', 'Bosque Nativo', 'Bosque Mixto', 'Humedales'],
            'Hectáreas': [datos_biobio["plantacion_forestal_ha"], datos_biobio["bosque_nativo_ha"], datos_biobio["bosque_mixto_ha"], datos_biobio["humedales_ha"]]
        })
        fig_bar = px.bar(
            df_veg, x='Hectáreas', y='Tipo Cobertura', orientation='h',
            color='Tipo Cobertura', color_discrete_sequence=['#A12312', '#345922', '#6E8131', '#417392'],
            text='Hectáreas', height=480
        )
        fig_bar.update_traces(texttemplate='%{text:,.1f} ha', textposition='outside')
        fig_bar.update_layout(showlegend=False, xaxis_title="Superficie en Hectáreas", yaxis_title="", margin={"r":30,"t":10,"l":10,"b":10})
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")
    st.subheader("📋 Logística Operativa y Plan de Evacuación Civil")
    col_izq, col_der = st.columns(2)
    with col_izq:
        st.markdown("### 🏃‍♂️ Rutas de Evacuación Sugeridas")
        comunas_peligrosas = df_comunas[df_comunas['Probabilidad (%)'] >= 50]
        if not comunas_peligrosas.empty:
            for com in comunas_peligrosas['comuna'].unique():
                ruta_sugerida = "Eje Vial Ruta 160 Sur" if dir_viento == "Norte" else "Eje Vial Ruta 5 Sur / Autopista del Itata"
                st.markdown(f"* **{com}:** Evacuar preventivamente vía **{ruta_sugerida}**.")
        else: st.success("✓ Todos los caminos y conectividades se encuentran estables.")
    with col_der:
        st.markdown("### 🚨 Central de Comunicaciones de Emergencia")
        df_telefonos = pd.DataFrame({"Organismo": ["CONAF", "Bomberos", "SAMU", "Carabineros"], "Línea": ["130", "132", "131", "133"]})
        st.table(df_telefonos)

with tab_tabla:
    st.subheader("📊 Tabla Comparativa de Impacto Territorial")
    df_tabla_limpia = df_comunas[['comuna', 'Provincia', 'poblacion_2017', 'distancia_foco_km', 'Probabilidad (%)', 'Clasificacion_Riesgo']].sort_values(by='Probabilidad (%)', ascending=False)
    df_tabla_limpia.columns = ['Comuna', 'Provincia', 'Población (Censo)', 'Distancia al Foco (Km)', 'Probabilidad de Impacto', 'Nivel de Riesgo']
    st.dataframe(df_tabla_limpia, use_container_width=True, hide_index=True)

with tab_datos:
    st.subheader("💾 Exportación de Reportes Técnicos para Autoridades")
    csv_data = df_tabla_limpia.to_csv(index=False, sep=';').encode('utf-8-sig')
    st.download_button(
        label="📥 Descargar resultado en formato CSV para Excel",
        data=csv_data,
        file_name=f"simulacion_incendio_{comuna_origen}.csv",
        mime="text/csv"
    )

# ------------------------------------------------------------------------------
# PESTAÑA 4: CONTEXTO CIENTÍFICO Y ARQUITECTURA (MEJORADA UX PROFESIONAL)
# ------------------------------------------------------------------------------
with tab_contexto:
    st.subheader("📝 Fundamentación Estratégica y Arquitectura Lógica")
    st.info("💡 **Objetivo Institucional:** Este MVP actúa como un Simulador Predictivo de Desastres diseñado para coordinar las mesas de las centrales del COE y SENAPRED ante crisis climáticas complejas en la Región del Biobío.")
    
    # Grid de 3 Columnas dinámicas que explican los componentes científicos
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("#### 🧪 Tetraedro del Fuego")
        st.markdown("""
        Los controladores emulan las 4 caras químicas necesarias para sostener la combustión forestal:
        * **Combustible:** Carga vegetal obtenida de CONAF.
        * **Calor:** Temperatura ambiente (°C).
        * **Oxígeno:** Aporte cinético de ráfagas de viento.
        * **Reacción en Cadena:** Sequedad crítica del aire.
        """)
    with c2:
        st.markdown("#### 🔬 Modelo Rothermel (1972)")
        st.markdown("""
        Simplificación analítica de la física de fluidos. Traduce variables complejas como el contenido de humedad de extinción y la relación de empaquetamiento a una matriz lineal ponderada rápida de ejecutar en tiempo real.
        """)
    with c3:
        st.markdown("#### 📊 Datos Censales (INE)")
        st.markdown("""
        Cruza los radios geométricos de alcance del fuego con los datos demográficos reales de la población de cada comuna (Censo 2017) para calcular los vectores de vulnerabilidad civil de manera inmediata.
        """)

    st.markdown("---")
    st.markdown("### 🎛️ Simulador Químico del Impacto de Gases y Mitigación Co2")
    st.write("Selecciona un nivel estimado de hectáreas destruidas para estimar el daño a la atmósfera:")
    
    # Elemento interactivo profesional dentro de Contexto
    ha_quemadas = st.number_input("🔥 Estimación de Superficie Siniestrada (Hectáreas)", min_value=10, max_value=50000, value=1500)
    co2_emitido = ha_quemadas * 18.5  # Constante ambiental estándar de emisión de carbono forestal
    arboles_perdidos = ha_quemadas * 450
    
    res1, res2 = st.columns(2)
    with res1: st.metric("⚠️ Emisión Estimada de CO₂ al Aire", f"{co2_emitido:,.1f} Toneladas")
    with res2: st.metric("📉 Pérdida de Sumideros de Carbono (Árboles)", f"{arboles_perdidos:,.0f} ejemplares")

# ------------------------------------------------------------------------------
# PESTAÑA 5: MEDIDAS DE PREVENCIÓN (DISEÑO PROFESIONAL CON EXPANDERS E INTERACTIVIDAD)
# ------------------------------------------------------------------------------
with tab_prevencion:
    st.subheader("🌲 Plan Maestro Comunitario: Mitigación y Gestión Preventiva")
    st.warning("⚠️ **Factor Antrópico:** El 99% de los incendios forestales en Chile son causados por negligencia o intención humana. La educación y la prevención son nuestras defensas más sólidas.")
    
    # Uso de st.expander para un diseño limpio y moderno
    with st.expander("🏡 1. Protocolo de Autoprotección Residencial (Interfaz del Hogar)"):
        st.markdown("""
        * **Gestión del Entorno (Cortafuegos):** Mantener el pasto corto, seco y retirado a un mínimo de 10 metros de los cimientos de la casa.
        * **Limpieza Estructural:** Despejar techumbres, canaletas y vigas de acumulación de ramas secas, agujas de pino u hojas secas inflamables.
        * **Poda de Seguridad:** Cortar las ramas más bajas de los árboles cercanos hasta una altura de 2 metros para mitigar la continuidad vertical del fuego.
        """)
        
    with st.expander("🚜 2. Operaciones Rurales, Forestales y Agrícolas"):
        st.markdown("""
        * **Cero Quemas:** Prohibición estricta del uso del fuego para eliminación de desechos agrícolas durante la temporada estival de altas temperaturas.
        * **Faenas Seguras:** Suspender el uso de herramientas eléctricas que generen chispas (galleteras, soldadoras) en áreas rurales con presencia de pastizal seco.
        * **Patrullaje Preventivo:** Habilitar redes comunitarias de monitoreo y vigías vecinales en zonas colindantes a plantaciones forestales masivas.
        """)
        
    with st.expander("⛺ 3. Turismo Responsable y Uso del Territorio"):
        st.markdown("""
        * **Camping Consecuente:** No encender fogatas en áreas silvestres protegidas ni reservas naturales fuera de las zonas expresamente habilitadas.
        * **Gestión de Residuos:** Retirar latas, botellas y vidrios de los senderos; actúan como lupas bajo el sol, iniciando focos térmicos espontáneos.
        * **Líneas de Emergencia:** Mantener los números clave agendados: **CONAF (130)**, **Bomberos (132)**, y **Carabineros (133)**.
        """)

    st.markdown("---")
    st.markdown("### 🧠 Test Rápido de Preparación Comunitaria frente a Emergencias")
    st.write("Evalúa el nivel de preparación de tu localidad antes de la temporada de crisis:")
    
    # Encuesta interactiva interactiva que calcula un Score dinámico de prevención
    q1 = st.checkbox("¿Tu hogar cuenta con un cortafuegos perimetral libre de maleza seca de al menos 10 metros?")
    q2 = st.checkbox("¿Conoces la ubicación exacta del albergue asignado para tu comuna en el plan del COE?")
    q3 = st.checkbox("¿Tienes un kit de emergencia familiar preparado (agua, linterna, radio a pilas, documentos)?")
    
    score = sum([q1, q2, q3])
    if score == 3: st.success("🟢 **Excelente:** Tu entorno cumple con los estándares institucionales más altos de prevención forestal.")
    elif score >= 1: st.warning("🟡 **Atención:** Cuentas con nociones básicas, pero quedan brechas vulnerables que cubrir antes de un siniestro.")
    else: st.error("🔴 **Riesgo Crítico:** Tu comunidad se encuentra desprotegida. Te sugerimos revisar las guías de CONAF indicadas arriba.")
