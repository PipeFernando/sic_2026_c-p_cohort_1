import streamlit as st
import pandas as pd
import plotly.express as px

# & "C:\Users\lobot\AppData\Local\Programs\Python\Python314\python.exe" -m streamlit run vegetacion.py
# =========================================================
# CONFIGURACIÓN
# =========================================================

st.set_page_config(
    page_title="Predictor CONAF - Biobío",
    page_icon="🌲",
    layout="wide"
)

st.title("🌲 Predictor de Incendio por Combustible Vegetal CONAF")
st.markdown("### Módulo experimental de análisis territorial | Región del Biobío")

st.info("""
Esta mini app analiza la combustibilidad vegetal usando datos CONAF.
Por defecto muestra la Región del Biobío completa, pero también permite seleccionar cada comuna.
El objetivo no es predecir un incendio real exacto, sino estimar qué territorios poseen mayor carga vegetal combustible.
""")

# =========================================================
# CARGA ROBUSTA DEL EXCEL
# =========================================================

columnas_requeridas = [
    "Comuna",
    "Plantaciones_ha",
    "Bosque_Nativo_ha",
    "Bosque_Mixto_ha",
    "Matorral_ha",
    "Matorral_Arborescente_ha",
    "Matorral_Pradera_ha",
    "Praderas_ha",
    "Humedales_ha",
    "Agua_ha"
]

def cargar_excel_multihoja(archivo):
    hojas = pd.read_excel(archivo, sheet_name=None)
    lista = []

    for nombre, df in hojas.items():
        df.columns = df.columns.astype(str).str.strip()
        df = df.dropna(how="all")

        if df.empty:
            continue

        if "Región" in df.columns:
            df = df.rename(columns={"Región": "Comuna"})

        if "Comuna" in df.columns:
            lista.append(df)

    if not lista:
        return pd.DataFrame()

    df_final = pd.concat(lista, ignore_index=True)
    df_final.columns = df_final.columns.astype(str).str.strip()
    return df_final

def limpiar_numero(valor):
    if pd.isna(valor):
        return 0.0

    if isinstance(valor, (int, float)):
        return float(valor)

    valor = str(valor).strip()
    valor = valor.replace("ha", "").strip()

    if "," in valor:
        valor = valor.replace(".", "").replace(",", ".")
    else:
        valor = valor.replace(",", "")

    try:
        return float(valor)
    except:
        return 0.0

# =========================================================
# SUBIR ARCHIVO
# =========================================================

st.sidebar.header("📂 Cargar archivo CONAF")

archivo = st.sidebar.file_uploader(
    "Sube el Excel con hojas regionales/comunales",
    type=["xlsx"]
)

if archivo is None:
    st.warning("Carga el archivo Excel para iniciar.")
    st.stop()

df = cargar_excel_multihoja(archivo)

if df.empty:
    st.error("No se pudo leer información válida desde el Excel.")
    st.stop()

faltantes = [c for c in columnas_requeridas if c not in df.columns]

if faltantes:
    st.error("Faltan columnas necesarias:")
    st.write(faltantes)
    st.write("Columnas detectadas:")
    st.write(df.columns.tolist())
    st.stop()

df = df[columnas_requeridas].copy()

df["Comuna"] = df["Comuna"].astype(str).str.strip()

for col in columnas_requeridas[1:]:
    df[col] = df[col].apply(limpiar_numero)

df = df.drop_duplicates(subset=["Comuna"])

# =========================================================
# CÁLCULO DEL ÍNDICE
# =========================================================

df["Combustible_Bruto"] = (
    df["Plantaciones_ha"] * 1.00 +
    df["Matorral_ha"] * 0.80 +
    df["Matorral_Arborescente_ha"] * 0.75 +
    df["Matorral_Pradera_ha"] * 0.65 +
    df["Praderas_ha"] * 0.50 +
    df["Bosque_Mixto_ha"] * 0.60 +
    df["Bosque_Nativo_ha"] * 0.40
)

df["Barreras_Naturales"] = (
    df["Humedales_ha"] * 0.90 +
    df["Agua_ha"] * 1.00
)

df["Indice_Combustible"] = df["Combustible_Bruto"] - df["Barreras_Naturales"]
df["Indice_Combustible"] = df["Indice_Combustible"].clip(lower=0)

max_indice = df["Indice_Combustible"].max()

if max_indice > 0:
    df["Indice_Normalizado"] = (df["Indice_Combustible"] / max_indice) * 100
else:
    df["Indice_Normalizado"] = 0

def clasificar(valor):
    if valor >= 75:
        return "🔴 Muy alto"
    elif valor >= 50:
        return "🟠 Alto"
    elif valor >= 25:
        return "🟡 Medio"
    else:
        return "🟢 Bajo"

df["Nivel"] = df["Indice_Normalizado"].apply(clasificar)

# =========================================================
# SELECTOR
# =========================================================

opciones = df["Comuna"].tolist()

default_index = 0
for i, nombre in enumerate(opciones):
    if "Biobío" in nombre or "Biobio" in nombre:
        default_index = i
        break

opcion = st.sidebar.selectbox(
    "📍 Selecciona territorio",
    opciones,
    index=default_index
)

fila = df[df["Comuna"] == opcion].iloc[0]

# =========================================================
# MÉTRICAS
# =========================================================

st.markdown("---")

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric("Índice combustible", f"{fila['Indice_Normalizado']:.1f}%")

with m2:
    st.metric("Nivel estimado", fila["Nivel"])

with m3:
    st.metric("Combustible bruto", f"{fila['Combustible_Bruto']:,.1f}")

with m4:
    st.metric("Barreras naturales", f"{fila['Barreras_Naturales']:,.1f}")

# =========================================================
# DATOS PARA GRÁFICOS
# =========================================================

datos_cobertura = pd.DataFrame({
    "Cobertura": [
        "Plantaciones",
        "Bosque Nativo",
        "Bosque Mixto",
        "Matorral",
        "Matorral Arborescente",
        "Matorral-Pradera",
        "Praderas",
        "Humedales",
        "Agua"
    ],
    "Hectáreas": [
        fila["Plantaciones_ha"],
        fila["Bosque_Nativo_ha"],
        fila["Bosque_Mixto_ha"],
        fila["Matorral_ha"],
        fila["Matorral_Arborescente_ha"],
        fila["Matorral_Pradera_ha"],
        fila["Praderas_ha"],
        fila["Humedales_ha"],
        fila["Agua_ha"]
    ]
})

# =========================================================
# PESTAÑAS
# =========================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🧪 Resumen",
    "📋 Tabla",
    "📊 Gráficos",
    "🔥 Ranking",
    "💾 Descargar"
])

with tab1:
    st.subheader(f"🧪 Interpretación técnica: {opcion}")

    if fila["Nivel"] == "🔴 Muy alto":
        st.error(f"**{opcion}** presenta combustibilidad vegetal muy alta.")
    elif fila["Nivel"] == "🟠 Alto":
        st.warning(f"**{opcion}** presenta combustibilidad vegetal alta.")
    elif fila["Nivel"] == "🟡 Medio":
        st.info(f"**{opcion}** presenta combustibilidad vegetal media.")
    else:
        st.success(f"**{opcion}** presenta combustibilidad vegetal baja.")

    st.markdown("""
El índice considera como combustibles principales las plantaciones, matorrales, praderas,
bosque mixto y bosque nativo. Los humedales y cuerpos de agua se consideran barreras naturales,
por lo que reducen el valor final.
""")

    st.code("""
Índice combustible =
Plantaciones*1.00
+ Matorral*0.80
+ Matorral Arborescente*0.75
+ Matorral-Pradera*0.65
+ Praderas*0.50
+ Bosque Mixto*0.60
+ Bosque Nativo*0.40
- Humedales*0.90
- Agua*1.00
""")

with tab2:
    st.subheader(f"📋 Tabla de coberturas: {opcion}")
    st.dataframe(datos_cobertura, use_container_width=True, hide_index=True)

    st.subheader("📋 Base completa procesada")
    st.dataframe(df, use_container_width=True, hide_index=True)

with tab3:
    st.subheader(f"📊 Gráficos de cobertura vegetal: {opcion}")

    col1, col2 = st.columns(2)

    with col1:
        fig_pie = px.pie(
            datos_cobertura,
            names="Cobertura",
            values="Hectáreas",
            hole=0.35,
            title=f"Distribución vegetal - {opcion}"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        fig_bar = px.bar(
            datos_cobertura.sort_values("Hectáreas"),
            x="Hectáreas",
            y="Cobertura",
            orientation="h",
            text="Hectáreas",
            title=f"Superficie por cobertura - {opcion}"
        )
        fig_bar.update_traces(texttemplate="%{text:,.1f}", textposition="outside")
        fig_bar.update_layout(height=500)
        st.plotly_chart(fig_bar, use_container_width=True)

with tab4:
    st.subheader("🔥 Ranking regional por combustibilidad vegetal")

    ranking = df.sort_values("Indice_Normalizado", ascending=False).copy()
    ranking["Indice_Normalizado"] = ranking["Indice_Normalizado"].round(1)

    st.dataframe(
        ranking[["Comuna", "Indice_Normalizado", "Nivel"]],
        use_container_width=True,
        hide_index=True
    )

    fig_rank = px.bar(
        ranking.sort_values("Indice_Normalizado"),
        x="Indice_Normalizado",
        y="Comuna",
        color="Nivel",
        orientation="h",
        text="Indice_Normalizado",
        color_discrete_map={
            "🔴 Muy alto": "#D32F2F",
            "🟠 Alto": "#F57C00",
            "🟡 Medio": "#FBC02D",
            "🟢 Bajo": "#388E3C"
        },
        title="Ranking de combustibilidad vegetal"
    )
    fig_rank.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig_rank.update_layout(height=900)
    st.plotly_chart(fig_rank, use_container_width=True)

with tab5:
    st.subheader("💾 Descargar datos procesados")

    csv = df.to_csv(index=False, sep=";").encode("utf-8-sig")

    st.download_button(
        label="📥 Descargar CSV procesado",
        data=csv,
        file_name="conaf_combustible_biobio_procesado.csv",
        mime="text/csv"
    )