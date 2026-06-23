# app.py
# Dashboard interactivo para analizar detonantes de frustración en atención al cliente.
# Proyecto Samsung Innovation Campus 2026 - Código y Programación
#
# Este archivo debe correr con:
# streamlit run app.py
#
# Requisitos que cubre:
# - 3+ visualizaciones relevantes.
# - 2+ filtros interactivos en el sidebar.
# - 3+ KPIs visibles.
# - Uso de @st.cache_data para cargar datos.
# - Texto explicativo del hallazgo principal en lenguaje no técnico.

import os
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


# -------------------------------------------------------------------
# 1. Configuración general de la página
# -------------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard de Frustración en Clientes",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -------------------------------------------------------------------
# 2. Diccionarios de nombres legibles
# -------------------------------------------------------------------
# El dataset usa categorías con guion bajo. Este diccionario permite
# mostrarlas de una forma más clara para una audiencia no técnica.
LABELS_DETONANTES = {
    "otro_no_clasificado": "Otro / no clasificado",
    "demora_espera": "Demora o espera",
    "problema_tecnico_app_web": "Problema técnico / app / web",
    "cobro_pago_reembolso": "Cobro, pago o reembolso",
    "falta_respuesta_comunicacion": "Falta de respuesta / comunicación",
    "pedido_envio_entrega": "Pedido, envío o entrega",
    "cancelacion_reserva": "Cancelación o reserva",
    "mala_atencion_agente": "Mala atención del agente",
    "servicio_caido_calidad": "Servicio caído o baja calidad",
}

LABELS_SENTIMIENTO = {
    "negativo": "Negativo",
    "neutral": "Neutral",
    "positivo": "Positivo",
}

LABELS_PRIORIDAD = {
    "alta": "Alta",
    "media": "Media",
    "baja": "Baja",
}


def nombre_legible(valor: object, diccionario: dict) -> str:
    """Convierte códigos internos en etiquetas más fáciles de leer."""
    if pd.isna(valor):
        return "Sin dato"
    valor = str(valor)
    return diccionario.get(valor, valor.replace("_", " ").capitalize())


# -------------------------------------------------------------------
# 3. Carga de datos
# -------------------------------------------------------------------
@st.cache_data
def cargar_datos():
    """
    Carga el dataset procesado usando rutas robustas.

    Esta función permite que la app funcione tanto localmente como en Streamlit Cloud.
    El problema habitual es que localmente ejecutamos Streamlit desde proyectos/Equipo_8,
    pero Streamlit Cloud puede ejecutar desde la raíz del repositorio.
    """

    base_dir = Path(__file__).resolve().parent
    cwd = Path.cwd()

    rutas_posibles = [
        base_dir / "data" / "dataset_procesado.csv",
        base_dir / "data" / "dataset_procesado_streamlit.csv",
        base_dir / "dataset_procesado.csv",
        cwd / "proyectos" / "Equipo_8" / "data" / "dataset_procesado.csv",
        cwd / "proyectos" / "Equipo_8" / "data" / "dataset_procesado_streamlit.csv",
        cwd / "data" / "dataset_procesado.csv",
        cwd / "dataset_procesado.csv",
    ]

    for ruta in rutas_posibles:
        if ruta.exists():
            return pd.read_csv(ruta)

    st.error("No se encontró el dataset procesado. Esta es la versión corregida de carga robusta.")

    st.write("Carpeta actual de ejecución:")
    st.code(str(cwd))

    st.write("Carpeta donde está app.py:")
    st.code(str(base_dir))

    st.write("Rutas revisadas:")
    for ruta in rutas_posibles:
        st.code(str(ruta))

    data_dir = base_dir / "data"

    st.write("Archivos detectados en la carpeta data junto a app.py:")

    if data_dir.exists():
        archivos = [archivo.name for archivo in data_dir.iterdir()]
        st.write(archivos)
    else:
        st.warning("No existe carpeta data junto a app.py.")

    st.stop()

# ------------------------------------------------------------
# Carga principal del dataset
# ------------------------------------------------------------
# Esta línea ejecuta la función cargar_datos() y guarda el CSV
# como un DataFrame llamado df.
df = cargar_datos()

# ------------------------------------------------------------
# Creación segura de la columna fecha_dt
# ------------------------------------------------------------
# El dashboard usa fecha_dt para el filtro temporal.
# Si el CSV no trae esa columna, intentamos crearla desde otras columnas posibles.
if "fecha_dt" not in df.columns:
    columnas_fecha_posibles = [
        "created_at",
        "fecha",
        "date",
        "timestamp",
        "tweet_created_at"
    ]

    columna_fecha_detectada = None

    for columna in columnas_fecha_posibles:
        if columna in df.columns:
            columna_fecha_detectada = columna
            break

    if columna_fecha_detectada is not None:
        df["fecha_dt"] = pd.to_datetime(df[columna_fecha_detectada], errors="coerce")
    else:
        df["fecha_dt"] = pd.NaT
else:
    df["fecha_dt"] = pd.to_datetime(df["fecha_dt"], errors="coerce")

# ------------------------------------------------------------
# Creación segura de la columna mes
# ------------------------------------------------------------
# Esta columna se usa para construir el gráfico de evolución temporal.
# Si fecha_dt tiene una fecha válida, extraemos el año y mes.
# Si no tiene fecha, dejamos el valor como "Sin fecha".

df["mes"] = np.where(
    df["fecha_dt"].notna(),
    df["fecha_dt"].dt.strftime("%Y-%m"),
    "Sin fecha"
)
# ------------------------------------------------------------
# Creación segura de columnas legibles para el dashboard
# ------------------------------------------------------------
# Estas columnas se usan para mostrar nombres más claros en filtros y gráficos.
# Si el CSV no las trae, las creamos a partir de las columnas procesadas.

if "sentimiento_legible" not in df.columns:
    if "sentimiento" in df.columns:
        df["sentimiento_legible"] = (
            df["sentimiento"]
            .astype(str)
            .str.lower()
            .map({
                "negativo": "Negativo",
                "negative": "Negativo",
                "neutral": "Neutral",
                "positivo": "Positivo",
                "positive": "Positivo"
            })
            .fillna(df["sentimiento"].astype(str).str.capitalize())
        )
    else:
        df["sentimiento_legible"] = "No clasificado"


if "detonante_legible" not in df.columns:
    if "detonante_frustracion" in df.columns:
        df["detonante_legible"] = (
            df["detonante_frustracion"]
            .astype(str)
            .str.replace("_", " ", regex=False)
            .str.capitalize()
        )
    else:
        df["detonante_legible"] = "No clasificado"


if "prioridad_legible" not in df.columns:
    if "prioridad_entrenamiento" in df.columns:
        df["prioridad_legible"] = (
            df["prioridad_entrenamiento"]
            .astype(str)
            .str.replace("_", " ", regex=False)
            .str.capitalize()
        )
    elif "prioridad" in df.columns:
        df["prioridad_legible"] = (
            df["prioridad"]
            .astype(str)
            .str.replace("_", " ", regex=False)
            .str.capitalize()
        )
    else:
        df["prioridad_legible"] = "No clasificado"
# -------------------------------------------------------------------
# 4. Estilos visuales
# -------------------------------------------------------------------
# Se usa CSS simple para mejorar legibilidad y dar contraste.
# No afecta los cálculos ni la lógica del dashboard.
st.markdown(
    """
    <style>
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    div[data-testid="stMetric"] {
        background-color: #111827;
        border: 1px solid #374151;
        padding: 16px;
        border-radius: 14px;
    }
    div[data-testid="stMetric"] label {
        color: #E5E7EB !important;
    }
    div[data-testid="stMetricValue"] {
        color: #FFFFFF !important;
    }
    .small-note {
        color: #9CA3AF;
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -------------------------------------------------------------------
# 5. Encabezado
# -------------------------------------------------------------------
st.title("📊 Dashboard de detonantes de frustración en clientes")

st.markdown(
    """
    Este dashboard analiza conversaciones de atención al cliente para identificar
    **sentimientos**, **detonantes de frustración** y **escenarios de entrenamiento**
    útiles para agentes de soporte.

    **Pregunta de análisis:**  
    ¿Cuáles son los principales detonantes de frustración en clientes y cómo pueden
    utilizarse para diseñar escenarios de entrenamiento para agentes de soporte?
    """
)


# -------------------------------------------------------------------
# 6. Sidebar con filtros interactivos
# -------------------------------------------------------------------
st.sidebar.header("Filtros del análisis")

# Filtro 1: rango de fechas.
fechas_validas = df["fecha_dt"].dropna()

if len(fechas_validas) > 0:
    fecha_min = fechas_validas.min().date()
    fecha_max = fechas_validas.max().date()

    rango_fechas = st.sidebar.date_input(
        "Rango de fechas",
        value=(fecha_min, fecha_max),
        min_value=fecha_min,
        max_value=fecha_max,
    )
else:
    rango_fechas = None
    st.sidebar.info("El dataset no tiene fechas válidas para filtrar.")


# Filtro 2: sentimiento.
sentimientos_disponibles = sorted(df["sentimiento"].dropna().unique().tolist())
sentimientos_seleccionados = st.sidebar.multiselect(
    "Sentimiento",
    options=sentimientos_disponibles,
    default=sentimientos_disponibles,
    format_func=lambda x: nombre_legible(x, LABELS_SENTIMIENTO),
)


# Filtro 3: prioridad de entrenamiento.
prioridades_disponibles = sorted(df["prioridad_entrenamiento"].dropna().unique().tolist())
prioridades_seleccionadas = st.sidebar.multiselect(
    "Prioridad de entrenamiento",
    options=prioridades_disponibles,
    default=prioridades_disponibles,
    format_func=lambda x: nombre_legible(x, LABELS_PRIORIDAD),
)


# Filtro 4: detonantes.
# Decisión analítica:
# Por defecto excluimos "otro_no_clasificado" para que el análisis se concentre
# en problemas interpretables y accionables.
excluir_otro = st.sidebar.checkbox(
    "Excluir 'otro / no clasificado'",
    value=True,
    help="Recomendado para enfocarse en detonantes concretos de frustración.",
)

detonantes_disponibles = sorted(df["detonante_frustracion"].dropna().unique().tolist())

if excluir_otro:
    detonantes_disponibles = [
        d for d in detonantes_disponibles if d != "otro_no_clasificado"
    ]

detonantes_seleccionados = st.sidebar.multiselect(
    "Detonante de frustración",
    options=detonantes_disponibles,
    default=detonantes_disponibles,
    format_func=lambda x: nombre_legible(x, LABELS_DETONANTES),
)


# Filtro 5: empresa contactada.
# En el dataset hay muchos casos no identificados; por eso se entrega
# la opción de filtrar solo empresas concretas.
empresas_disponibles = sorted(df["empresa_contactada"].dropna().unique().tolist())
empresas_seleccionadas = st.sidebar.multiselect(
    "Empresa contactada",
    options=empresas_disponibles,
    default=[],
    help="Si no seleccionas empresas, se incluyen todas.",
)


# Filtro 6: largo mínimo del mensaje.
# Este filtro ayuda a separar mensajes muy cortos de casos con más contexto.
if "num_palabras" in df.columns:
    max_palabras = int(np.nanpercentile(df["num_palabras"], 95))
    min_palabras = st.sidebar.slider(
        "Mínimo de palabras por mensaje",
        min_value=0,
        max_value=max(10, max_palabras),
        value=0,
        step=1,
    )
else:
    min_palabras = 0


# -------------------------------------------------------------------
# 7. Aplicación de filtros
# -------------------------------------------------------------------
df_filtrado = df.copy()

if rango_fechas and len(rango_fechas) == 2:
    inicio, fin = rango_fechas
    fechas_comparables = df_filtrado["fecha_dt"].dt.date
    df_filtrado = df_filtrado[
        (fechas_comparables >= inicio) & (fechas_comparables <= fin)
    ]

if sentimientos_seleccionados:
    df_filtrado = df_filtrado[
        df_filtrado["sentimiento"].isin(sentimientos_seleccionados)
    ]

if prioridades_seleccionadas:
    df_filtrado = df_filtrado[
        df_filtrado["prioridad_entrenamiento"].isin(prioridades_seleccionadas)
    ]

if detonantes_seleccionados:
    df_filtrado = df_filtrado[
        df_filtrado["detonante_frustracion"].isin(detonantes_seleccionados)
    ]
else:
    # Si el usuario deja la lista vacía, se evita mostrar resultados ambiguos.
    df_filtrado = df_filtrado.iloc[0:0]

if empresas_seleccionadas:
    df_filtrado = df_filtrado[
        df_filtrado["empresa_contactada"].isin(empresas_seleccionadas)
    ]

if "num_palabras" in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado["num_palabras"] >= min_palabras]


# -------------------------------------------------------------------
# 8. Validación de datos filtrados
# -------------------------------------------------------------------
if df_filtrado.empty:
    st.warning(
        "No hay datos para los filtros seleccionados. "
        "Ajusta los filtros del sidebar para volver a mostrar resultados."
    )
    st.stop()


# -------------------------------------------------------------------
# 9. KPIs principales
# -------------------------------------------------------------------
total_mensajes = len(df_filtrado)

porcentaje_negativo = (
    (df_filtrado["sentimiento"] == "negativo").mean() * 100
    if "sentimiento" in df_filtrado.columns
    else 0
)

porcentaje_alta = (
    (df_filtrado["prioridad_entrenamiento"] == "alta").mean() * 100
    if "prioridad_entrenamiento" in df_filtrado.columns
    else 0
)

detonantes_accionables = df_filtrado[
    df_filtrado["detonante_frustracion"] != "otro_no_clasificado"
]

if len(detonantes_accionables) > 0:
    top_detonante = detonantes_accionables["detonante_frustracion"].value_counts().idxmax()
    top_detonante_legible = nombre_legible(top_detonante, LABELS_DETONANTES)
else:
    top_detonante_legible = "Sin detonante accionable"

col1, col2, col3, col4 = st.columns(4)

col1.metric("Mensajes analizados", f"{total_mensajes:,}".replace(",", "."))
col2.metric("Mensajes negativos", f"{porcentaje_negativo:.1f}%")
col3.metric("Prioridad alta", f"{porcentaje_alta:.1f}%")
col4.metric("Detonante principal", top_detonante_legible)


# -------------------------------------------------------------------
# 10. Hallazgo principal en lenguaje no técnico
# -------------------------------------------------------------------
negativos = df_filtrado[df_filtrado["sentimiento"] == "negativo"]

if len(negativos) > 0:
    negativos_accionables = negativos[
        negativos["detonante_frustracion"] != "otro_no_clasificado"
    ]

    if len(negativos_accionables) > 0:
        top_negativo = negativos_accionables["detonante_frustracion"].value_counts().idxmax()
        top_negativo_legible = nombre_legible(top_negativo, LABELS_DETONANTES)
    else:
        top_negativo_legible = top_detonante_legible
else:
    top_negativo_legible = top_detonante_legible

st.info(
    f"**Hallazgo principal:** en la selección actual, el foco más importante para "
    f"entrenamiento es **{top_negativo_legible}**. En términos prácticos, esto significa "
    f"que los agentes deberían practicar respuestas para reconocer la molestia del cliente, "
    f"explicar el siguiente paso y cerrar la conversación con un compromiso verificable."
)


# -------------------------------------------------------------------
# 11. Visualizaciones principales
# -------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📈 Resumen visual",
        "🔥 Detonantes y sentimientos",
        "🎭 Escenarios de entrenamiento",
        "🧾 Datos filtrados",
    ]
)


with tab1:
    st.subheader("Distribución general del sentimiento")

    # Visualización 1: distribución de sentimiento.
    conteo_sentimiento = (
        df_filtrado["sentimiento_legible"]
        .value_counts()
        .reset_index()
    )
    conteo_sentimiento.columns = ["Sentimiento", "Cantidad"]

    fig_sent = px.bar(
        conteo_sentimiento,
        x="Sentimiento",
        y="Cantidad",
        text="Cantidad",
        title="Cantidad de mensajes por sentimiento",
    )
    fig_sent.update_traces(textposition="outside")
    fig_sent.update_layout(yaxis_title="Cantidad de mensajes", xaxis_title="")
    st.plotly_chart(fig_sent, use_container_width=True)

    st.subheader("Evolución temporal de mensajes")

    # Visualización 2: evolución temporal por mes.
    temporal = (
        df_filtrado[df_filtrado["mes"] != "Sin fecha"]
        .groupby(["mes", "sentimiento_legible"])
        .size()
        .reset_index(name="Cantidad")
        .sort_values("mes")
    )

    if len(temporal) > 0:
        fig_temporal = px.line(
            temporal,
            x="mes",
            y="Cantidad",
            color="sentimiento_legible",
            markers=True,
            title="Evolución mensual de mensajes por sentimiento",
        )
        fig_temporal.update_layout(
            xaxis_title="Mes",
            yaxis_title="Cantidad de mensajes",
            legend_title="Sentimiento",
        )
        st.plotly_chart(fig_temporal, use_container_width=True)
    else:
        st.write("No hay fechas suficientes para construir la serie temporal.")


with tab2:
    st.subheader("Principales detonantes de frustración")

    # Visualización 3: ranking de detonantes.
    ranking_detonantes = (
        df_filtrado["detonante_legible"]
        .value_counts()
        .head(12)
        .reset_index()
    )
    ranking_detonantes.columns = ["Detonante", "Cantidad"]

    fig_det = px.bar(
        ranking_detonantes.sort_values("Cantidad", ascending=True),
        x="Cantidad",
        y="Detonante",
        orientation="h",
        text="Cantidad",
        title="Ranking de detonantes más frecuentes",
    )
    fig_det.update_layout(xaxis_title="Cantidad de mensajes", yaxis_title="")
    st.plotly_chart(fig_det, use_container_width=True)

    st.subheader("Relación entre detonantes y sentimiento")

    # Visualización 4: detonante cruzado con sentimiento.
    cruce = (
        df_filtrado
        .groupby(["detonante_legible", "sentimiento_legible"])
        .size()
        .reset_index(name="Cantidad")
    )

    # Se dejan solo los detonantes con más registros para que el gráfico sea legible.
    top_detonantes_legibles = (
        df_filtrado["detonante_legible"]
        .value_counts()
        .head(10)
        .index
        .tolist()
    )

    cruce = cruce[cruce["detonante_legible"].isin(top_detonantes_legibles)]

    fig_cruce = px.bar(
        cruce,
        x="detonante_legible",
        y="Cantidad",
        color="sentimiento_legible",
        barmode="stack",
        title="Sentimiento asociado a cada detonante",
    )
    fig_cruce.update_layout(
        xaxis_title="Detonante",
        yaxis_title="Cantidad de mensajes",
        legend_title="Sentimiento",
        xaxis_tickangle=-30,
    )
    st.plotly_chart(fig_cruce, use_container_width=True)

    st.subheader("Prioridad de entrenamiento por detonante")

    prioridad = (
        df_filtrado
        .groupby(["detonante_legible", "prioridad_legible"])
        .size()
        .reset_index(name="Cantidad")
    )
    prioridad = prioridad[prioridad["detonante_legible"].isin(top_detonantes_legibles)]

    fig_prioridad = px.bar(
        prioridad,
        x="detonante_legible",
        y="Cantidad",
        color="prioridad_legible",
        barmode="group",
        title="Prioridad sugerida para entrenamiento",
    )
    fig_prioridad.update_layout(
        xaxis_title="Detonante",
        yaxis_title="Cantidad de mensajes",
        legend_title="Prioridad",
        xaxis_tickangle=-30,
    )
    st.plotly_chart(fig_prioridad, use_container_width=True)


with tab3:
    st.subheader("Escenarios sugeridos para entrenamiento de agentes")

    # Esta tabla resume qué tipo de entrenamiento conviene diseñar según
    # los detonantes más frecuentes.
    resumen_entrenamiento = (
        df_filtrado
        .groupby(["detonante_frustracion", "detonante_legible", "escenario_sugerido"])
        .agg(
            mensajes=("tweet_id", "count"),
            porcentaje_negativo=("sentimiento", lambda s: (s == "negativo").mean() * 100),
            prioridad_alta=("prioridad_entrenamiento", lambda s: (s == "alta").sum()),
        )
        .reset_index()
        .sort_values(["prioridad_alta", "mensajes"], ascending=False)
    )

    resumen_entrenamiento["porcentaje_negativo"] = resumen_entrenamiento[
        "porcentaje_negativo"
    ].round(1)

    st.dataframe(
        resumen_entrenamiento[
            [
                "detonante_legible",
                "escenario_sugerido",
                "mensajes",
                "porcentaje_negativo",
                "prioridad_alta",
            ]
        ].rename(
            columns={
                "detonante_legible": "Detonante",
                "escenario_sugerido": "Escenario sugerido",
                "mensajes": "Mensajes",
                "porcentaje_negativo": "% negativo",
                "prioridad_alta": "Casos prioridad alta",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")
    st.subheader("Simulador simple de caso para capacitación")

    detonantes_para_simulador = resumen_entrenamiento["detonante_frustracion"].tolist()

    detonante_elegido = st.selectbox(
        "Elige un detonante para generar un caso de práctica",
        options=detonantes_para_simulador,
        format_func=lambda x: nombre_legible(x, LABELS_DETONANTES),
    )

    casos_posibles = df_filtrado[
        df_filtrado["detonante_frustracion"] == detonante_elegido
    ]

    if len(casos_posibles) > 0:
        # Se priorizan mensajes negativos porque son más útiles para practicar
        # contención, empatía y resolución.
        casos_negativos = casos_posibles[casos_posibles["sentimiento"] == "negativo"]

        if len(casos_negativos) > 0:
            caso_base = casos_negativos.sample(1, random_state=42).iloc[0]
        else:
            caso_base = casos_posibles.sample(1, random_state=42).iloc[0]

        escenario = caso_base.get("escenario_sugerido", "Sin escenario sugerido")
        texto_cliente = caso_base.get("text", "Sin texto disponible")

        c1, c2 = st.columns([1.2, 1])

        with c1:
            st.markdown("#### Mensaje real de referencia")
            st.write(texto_cliente)

        with c2:
            st.markdown("#### Objetivo del agente")
            st.write(escenario)

            st.markdown("#### Respuesta recomendada")
            st.write(
                "1. Reconocer explícitamente el problema del cliente.\n\n"
                "2. Evitar culpar al usuario o a otro equipo.\n\n"
                "3. Explicar el siguiente paso de forma concreta.\n\n"
                "4. Cerrar con plazo, responsable o canal de seguimiento."
            )


with tab4:
    st.subheader("Vista de datos filtrados")

    columnas_a_mostrar = [
        col for col in [
            "fecha",
            "empresa_contactada",
            "text",
            "sentimiento",
            "intensidad_sentimiento",
            "detonante_frustracion",
            "escenario_sugerido",
            "prioridad_entrenamiento",
            "num_palabras",
        ]
        if col in df_filtrado.columns
    ]

    st.dataframe(
        df_filtrado[columnas_a_mostrar].head(1000),
        use_container_width=True,
        hide_index=True,
    )

    csv_filtrado = df_filtrado.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Descargar datos filtrados en CSV",
        data=csv_filtrado,
        file_name="datos_filtrados_dashboard.csv",
        mime="text/csv",
    )

    st.caption(
        "Se muestran hasta 1000 filas en pantalla para mantener fluida la aplicación. "
        "El botón de descarga exporta todos los registros filtrados."
    )


# -------------------------------------------------------------------
# 12. Cierre metodológico
# -------------------------------------------------------------------
st.markdown("---")
st.markdown(
    """
    **Limitación importante:** este análisis clasifica sentimientos y detonantes a partir del texto.
    Por lo tanto, sirve para detectar patrones generales, pero no reemplaza una revisión humana
    de casos críticos o conversaciones completas.
    """
)
