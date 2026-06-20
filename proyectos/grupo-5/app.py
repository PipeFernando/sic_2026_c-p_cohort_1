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

# Diccionario estratégico de albergues por comuna para la sección de logística operativa
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
# 2. CARGA Y LIMPIEZA DE DATOS AUTOMATIZADA (CON RUTAS OFICIALES REVISADAS)
# ==============================================================================
@st.cache_data
def inicializar_sistema():
    # DECISIÓN NO OBVIA: Usamos os.path para construir rutas absolutas dinámicas. 
    # Esto evita que Streamlit Cloud falle por problemas de contexto del directorio de trabajo actual (CWD).
    base_path = os.path.dirname(__file__)
    
    ruta_comunas = os.path.join(base_path, "data", "Latitud - Longitud Chile.csv")
    ruta_bosques = os.path.join(base_path, "data", "bosques_chile_excel.csv")
    
    # Lectura del dataset demográfico estructurado regional
    df_c = pd.read_csv(ruta_comunas)
    
    # Filtrado estricto por codificación invisible en strings de la base de datos original (\xa0Biobío)
    df_c = df_c[df_c['Región'].astype(str).str.contains('Biobío')]
    
    df_c['comuna'] = df_c['Comuna'].str.strip()
    df_c['latitud_decimal'] = df_c['Latitud (Decimal)']
    df_c['longitud_decimal'] = df_c['Longitud (decimal)']
    
    # DECISIÓN NO OBVIA: Formateo de tipos en población. Reemplazamos tanto comas como puntos
    # para prevenir colapsos de casting numérico debido a formatos regionales heterogéneos de Excel.
    df_c['poblacion_2017'] = df_c['Población Año 2017'].astype(str).str.replace(',', '').str.replace('.', '').astype(float).astype(int)
    
    # Lectura del inventario forestal oficial de CONAF
    df_b = pd.read_csv(ruta_bosques, sep=';')
    df_b['Región'] = df_b['Región'].str.strip()
    
    def limpiar_numero_chileno(val):
        if pd.isna(val): return 0.0
        return float(str(val).strip().replace('.', '').replace(',', '.'))
    
    row_biobio = df_b[df_b['Región'] == 'Biobío'].iloc[0]
    
    vegetacion = {
        "plantacion_forestal_ha": limpiar_numero_chileno(row_biobio['Plantación Forestal']),
        "bosque_nativo_ha": limpiar_numero_chileno(row_biobio['Bosque Nativo']),
        "bosque_mixto_ha": limpiar_numero_chileno(row_biobio['Bosque Mixto']),
        "humedales_ha": 10172.8,  # Constante ecológica regional validada en el informe base
        "bosques_total_ha": limpiar_numero_chileno(row_biobio['Total'])
    }
    
    return df_c, vegetacion

try:
    df_comunas, datos_biobio = inicializar_sistema()
except Exception as e:
    st.error(f"❌ Error crítico en el enrutamiento de archivos locales: {e}")
    st.info("Asegúrate de que tus archivos estén en la ruta: proyectos/grupo-5/data/")
    st.stop()

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
# 4. ALGORITMO MATEMÁTICO DE PROPAGACIÓN (PROS/CONTRAS ROTHERMEL SIMPLIFICADO)
# ==============================================================================
# DECISIÓN NO OBVIA: Ponderación de inflamabilidad del material forestal fino muerto.
# El pino y eucalipto (plantaciones) reciben peso 1.0 por la alta continuidad vertical del dosel.
combustible = (
    (datos_biobio["plantacion_forestal_ha"] * 1.0) +
    (datos_biobio["bosque_mixto_ha"] * 0.8) +
    (datos_biobio["bosque_nativo_ha"] * 0.6)
) / datos_biobio["bosques_total_ha"] * 100

sequedad = 100 - humedad

# Matriz lineal ponderada sustituta del modelo físico-químico complejo de fluidos
ip = (0.30 * viento) + (0.30 * combustible) + (0.20 * temperatura) + (0.10 * sequedad) + (0.10 * pendiente)
ip = min(max(ip, 0), 100)

# Ecuaciones operativas educativas de velocidad cinética y radio geodésico resultante
velocidad_fuego = 0.5 + ((ip / 100) * 4.0) + ((viento / 100) * 3.0)
alcance_km = velocidad_fuego * hours_ev

# Extraer coordenadas del foco emisor seleccionado
origen_fila = df_comunas[df_comunas['comuna'] == comuna_origen].iloc[0]
lat_o, lon_o = origen_fila['latitud_decimal'], origen_fila['longitud_decimal']

# DECISIÓN NO OBVIA: Conversión de distancia mediante aproximación esférica simplificada.
# Multiplicar por 111.12 km aproxima de forma óptima las distancias euclidianas a kilómetros reales en Chile.
df_comunas['distancia_foco_km'] = np.sqrt((df_comunas['latitud_decimal'] - lat_o)**2 + (df_comunas['longitud_decimal'] - lon_o)**2) * 111.12
df_comunas['dif_lat'] = df_comunas['latitud_decimal'] - lat_o
df_comunas['dif_lon'] = df_comunas['longitud_decimal'] - lon_o

# DECISIÓN NO OBVIA: El filtro de trayectoria asume coordenadas cartesianas planas.
# Si el viento va al Norte, el fuego viaja al hemisferio norte (dif_lat > 0). Simplificación geométrica para UX.
def evaluar_trayectoria(row):
    if row['comuna'] == comuna_origen: return True
    if dir_viento == "Norte" and row['dif_lat'] > 0: return True
    if dir_viento == "Sur" and row['dif_lat'] < 0: return True
    if dir_viento == "Este" and row['dif_lon'] > 0: return True
    if dir_viento == "Oeste" and row['dif_lon'] < 0: return True
    if dir_viento == "Omnidireccional (Sin control)": return True
    return False

df_comunas['En_Trayectoria'] = df_comunas.apply(evaluar_trayectoria, axis=1)

# Cálculo probabilístico inverso indexado a los rangos requeridos por la pauta
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
# 5. DISEÑO DE PESTAÑAS (MÓDULOS DE INTERFAZ UX INTERACTIVOS)
# ==============================================================================
tab_mapa, tab_tabla, tab_datos, tab_contexto, tab_prevencion = st.tabs([
    "🖥️ Simulador y Mapa de Crisis", 
    "📊 Propagación Estimada entre Comunas", 
    "💾 Descargar Resultado (CSV)",
    "🧪 Contexto y Tetraedro del Fuego",
    "🌲 Medidas de Prevención"
])

# ------------------------------------------------------------------------------
# PESTAÑA 1: MAPA Y CONTROLES OPERATIVOS
# ------------------------------------------------------------------------------
with tab_mapa:
    comunas_afectadas = df_comunas[df_comunas['Probabilidad (%)'] >= 25]
    poblacion_afectada = comunas_afectadas['poblacion_2017'].sum()
    
    # DECISIÓN NO OBVIA: Constante habitacional demográfica de Chile.
    # El factor 3.2 representa la densidad habitacional urbana/rural promedio según los últimos censos del INE.
    viviendas_afectadas = poblacion_afectada / 3.2

    # Despliegue de KPIs analíticos reactivos
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
        
        # 'scrollZoom': True inyecta la capacidad de interactuar con la rueda del ratón de forma directa sin usar botones estáticos
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

# ------------------------------------------------------------------------------
# PESTAÑA 2: TABLA DE DATOS DE PROPAGACIÓN COMPARATIVA
# ------------------------------------------------------------------------------
with tab_tabla:
    st.subheader("📊 Tabla Comparativa de Impacto Territorial")
    st.write("A continuación se detallan las métricas procesadas de distancia y probabilidad para las comunas analizadas:")
    
    df_tabla_limpia = df_comunas[['comuna', 'Provincia', 'poblacion_2017', 'distancia_foco_km', 'Probabilidad (%)', 'Clasificacion_Riesgo']].sort_values(by='Probabilidad (%)', ascending=False)
    df_tabla_limpia.columns = ['Comuna', 'Provincia', 'Población (Censo)', 'Distancia al Foco (Km)', 'Probabilidad de Impacto', 'Nivel de Riesgo']
    st.dataframe(df_tabla_limpia, use_container_width=True, hide_index=True)

# ------------------------------------------------------------------------------
# PESTAÑA 3: DESCARGA DE RESULTADOS (CORREGIDA PARA INTEGRACIÓN CON EXCEL CHILE)
# ------------------------------------------------------------------------------
with tab_datos:
    st.subheader("💾 Exportación de Reportes Técnicos para Autoridades")
    st.write("Puedes descargar el estado actual de la simulación en un archivo perfectamente compatible con Excel:")
    
    # DECISIÓN NO OBVIA: El parámetro sep=';' combinado con encoding='utf-8-sig' fuerza a Excel
    # a procesar la delimitación estructural de celdas y acentos latinos correctamente sin requerir el asistente manual de importación.
    csv_data = df_tabla_limpia.to_csv(index=False, sep=';').encode('utf-8-sig')
    st.download_button(
        label="📥 Descargar resultado en formato CSV para Excel",
        data=csv_data,
        file_name=f"simulacion_incendio_{comuna_origen}.csv",
        mime="text/csv"
    )

# ------------------------------------------------------------------------------
# PESTAÑA 4: CONTEXTO CIENTÍFICO Y TETRAEDRO
# ------------------------------------------------------------------------------
with tab_contexto:
    st.subheader("📝 Fundamentación del Proyecto y Arquitectura Lógica")
    st.markdown("""
    Los incendios forestales constituyen una amenaza permanente en Chile. Este proyecto implementa un **Simulador Técnico de Gestión de Emergencias** como un Producto Mínimo Viable (MVP). Su objetivo es representar de forma lógica cómo ciertas condiciones ambientales y territoriales aumentan o disminuyen el riesgo de propagación entre comunas de la **Región del Biobío**.
    """)
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.markdown("### 🧪 El Tetraedro del Fuego en el Panel")
        st.markdown("""
        Los controles dinámicos de la barra lateral emulan químicamente las caras del **Tetraedro del Fuego**:
        * **Combustible:** Determinado por el inventario regional de plantaciones densas.
        * **Calor:** Modulado por la variable de *Temperatura Ambiente*.
        * **Oxígeno:** Alimentado cinéticamente por la *Velocidad del Viento*.
        * **Reacción en Cadena:** Determinada por el índice crítico de *Sequedad (100 - Humedad)*.
        """)
    with col_c2:
        st.markdown("### 🔬 Inspiración Científica (Rothermel 1972)")
        st.markdown("""
        El diseño simplifica la ecuación matemática de fluidos complejos del físico **Richard Rothermel**, reduciendo variables de laboratorio complejas (como la carga molecular o densidad de empaquetamiento) a un sistema optimizado de pesos ponderados lineales para garantizar una ejecución interactiva fluida.
        """)

# ------------------------------------------------------------------------------
# PESTAÑA 5: MEDIDAS DE PREVENCIÓN DE INCENDIOS
# ------------------------------------------------------------------------------
with tab_prevencion:
    st.subheader("🌲 Manual Comunitario: Medidas Preventivas para Evitar Incendios")
    st.write("El 99% de los incendios forestales son causados por acción humana. Conocer estas medidas puede salvar vidas:")
    
    p1, p2 = st.columns(2)
    with p1:
        st.markdown("""
        #### 🏡 Alrededor del Hogar (Espacio Autoprotegido)
        * **Manejo del Combustible:** Limpia techos y canaletas de hojas secas o ramas muertas que puedan encenderse con pavesas flotantes.
        * **Cortafuegos Perimetral:** Mantenga el pasto corto y elimine la maleza seca en un radio mínimo de 10 metros alrededor de las viviendas.
        * **Distanciamiento de Copas:** Pode los árboles del patio eliminando ramas bajas hasta los 2 metros de altura para evitar incendios de copa.
        """)
    with p2:
        st.markdown("""
        #### 🚜 En Actividades Rurales y de Camping
        * **Restricción de Quemas:** Está prohibido realizar quemas de desechos agrícolas o forestales durante toda la época de altas temperaturas.
        * **Uso del Fuego en Recreación:** No realices fogatas ni uses herramientas que generen chispas (como galleteras o soldadoras) cerca de vegetación seca.
        * **Denuncia Inmediata:** Si detectas una columna de humo sospechosa por pequeña que sea, avisa de inmediato a **CONAF (130)** o **Bomberos (132)**.
        """)
