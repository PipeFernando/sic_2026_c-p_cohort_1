"""
Módulo de Cuadrícula UTM para el simulador de incendios (Grupo 5)
------------------------------------------------------------------
Genera líneas de cuadrícula en UTM (zona 18S, EPSG:32718, válida para
la Región del Biobío) y las reproyecta a lat/lon para superponerlas
sobre un mapa Plotly (scatter_mapbox / Scattermapbox).

Uso típico en app.py:

    import plotly.graph_objects as go
    from utm_grid import generar_trazas_cuadricula_utm

    fig = px.scatter_mapbox(df, lat="lat", lon="lon", ...)

    for traza in generar_trazas_cuadricula_utm(
        lat_min=-38.2, lat_max=-36.5,
        lon_min=-73.5, lon_max=-71.0,
        paso_metros=10000  # cada 10 km
    ):
        fig.add_trace(traza)

    st.plotly_chart(fig, use_container_width=True)
"""

import numpy as np
import plotly.graph_objects as go
from pyproj import Transformer

# EPSG:32718 = WGS84 / UTM zona 18S (Chile centro-sur, incluye Biobío)
# Si tu zona de estudio cae en zona 19S, usa EPSG:32719
EPSG_UTM_BIOBIO = "EPSG:32718"
EPSG_WGS84 = "EPSG:4326"


def generar_trazas_cuadricula_utm(
    lat_min, lat_max, lon_min, lon_max,
    paso_metros=10000,
    epsg_utm=EPSG_UTM_BIOBIO,
    color="rgba(150,150,150,0.5)",
    ancho_linea=1,
    mostrar_etiquetas=True,
    modo_etiqueta="utm",       # "utm" -> coordenadas UTM en km | "distancia_foco" -> km al foco más cercano
    origenes=None,             # lista de tuplas [(lat, lon), ...] -- obligatorio si modo_etiqueta="distancia_foco"
):
    """
    Devuelve una lista de trazas Plotly (go.Scattermapbox) que dibujan
    una cuadrícula UTM regular sobre el área indicada en lat/lon.

    Parámetros
    ----------
    lat_min, lat_max, lon_min, lon_max : float
        Bounding box del área de interés en grados (WGS84).
    paso_metros : float
        Espaciado de la cuadrícula en metros (ej. 10000 = cada 10 km).
    epsg_utm : str
        Código EPSG de la zona UTM a usar.
    color, ancho_linea : estilo de las líneas.
    mostrar_etiquetas : bool
        Si True, agrega una traza de texto con las coordenadas UTM
        en las esquinas de cada celda.

    Retorna
    -------
    list[go.Scattermapbox]
    """
    to_utm = Transformer.from_crs(EPSG_WGS84, epsg_utm, always_xy=True)
    to_wgs84 = Transformer.from_crs(epsg_utm, EPSG_WGS84, always_xy=True)

    # Convertir el bounding box (lat/lon) a UTM (metros)
    esquinas_lon = [lon_min, lon_max, lon_min, lon_max]
    esquinas_lat = [lat_min, lat_min, lat_max, lat_max]
    xs_utm, ys_utm = to_utm.transform(esquinas_lon, esquinas_lat)

    x_min, x_max = min(xs_utm), max(xs_utm)
    y_min, y_max = min(ys_utm), max(ys_utm)

    # Redondear al múltiplo de paso_metros más cercano (líneas "limpias")
    x_inicio = np.floor(x_min / paso_metros) * paso_metros
    x_fin = np.ceil(x_max / paso_metros) * paso_metros
    y_inicio = np.floor(y_min / paso_metros) * paso_metros
    y_fin = np.ceil(y_max / paso_metros) * paso_metros

    lineas_x = np.arange(x_inicio, x_fin + paso_metros, paso_metros)
    lineas_y = np.arange(y_inicio, y_fin + paso_metros, paso_metros)

    trazas = []

    # --- Líneas verticales (Este constante, Norte variable) ---
    for x in lineas_x:
        ys = np.linspace(y_inicio, y_fin, 50)
        xs = np.full_like(ys, x)
        lons, lats = to_wgs84.transform(xs, ys)
        trazas.append(
            go.Scattermapbox(
                lat=lats, lon=lons,
                mode="lines",
                line=dict(width=ancho_linea, color=color),
                hoverinfo="skip",
                showlegend=False,
                name=f"UTM E={int(x)}",
            )
        )

    # --- Líneas horizontales (Norte constante, Este variable) ---
    for y in lineas_y:
        xs = np.linspace(x_inicio, x_fin, 50)
        ys = np.full_like(xs, y)
        lons, lats = to_wgs84.transform(xs, ys)
        trazas.append(
            go.Scattermapbox(
                lat=lats, lon=lons,
                mode="lines",
                line=dict(width=ancho_linea, color=color),
                hoverinfo="skip",
                showlegend=False,
                name=f"UTM N={int(y)}",
            )
        )

    # --- Etiquetas de coordenadas en las intersecciones (opcional) ---
    # --- Etiquetas en las intersecciones (opcional) ---
    if mostrar_etiquetas:
        usar_distancia = modo_etiqueta == "distancia_foco" and origenes
        if usar_distancia:
            focos_utm = [latlon_a_utm(lat, lon, epsg_utm) for lat, lon in origenes]

        xs_lbl, ys_lbl, textos = [], [], []
        for x in lineas_x:
            for y in lineas_y:
                xs_lbl.append(x)
                ys_lbl.append(y)
                if usar_distancia:
                    dist_min_km = min(
                        np.hypot(x - fx, y - fy) / 1000.0 for fx, fy in focos_utm
                    )
                    textos.append(f"{dist_min_km:.1f} km")
                else:
                    textos.append(f"{int(x/1000)}E / {int(y/1000)}N (km)")
        lons_lbl, lats_lbl = to_wgs84.transform(xs_lbl, ys_lbl)
        trazas.append(
            go.Scattermapbox(
                lat=lats_lbl, lon=lons_lbl,
                mode="text",
                text=textos,
                textfont=dict(size=9, color="rgba(80,80,80,0.7)"),
                hoverinfo="skip",
                showlegend=False,
                name="Etiquetas UTM",
            )
        )

    return trazas


def latlon_a_utm(lat, lon, epsg_utm=EPSG_UTM_BIOBIO):
    """Convierte un punto (o arrays) lat/lon a coordenadas UTM (x, y) en metros.
    Útil para calcular distancias reales en tu fórmula de Alcance/Probabilidad
    en vez de usar grados directamente."""
    transformer = Transformer.from_crs(EPSG_WGS84, epsg_utm, always_xy=True)
    x, y = transformer.transform(lon, lat)
    return x, y


def distancia_utm_metros(lat1, lon1, lat2, lon2, epsg_utm=EPSG_UTM_BIOBIO):
    """Distancia euclidiana real en metros entre dos puntos, usando UTM
    (más precisa para distancias cortas/medias que la fórmula haversine
    sobre lat/lon, y mucho más simple de calcular)."""
    x1, y1 = latlon_a_utm(lat1, lon1, epsg_utm)
    x2, y2 = latlon_a_utm(lat2, lon2, epsg_utm)
    return float(np.hypot(x2 - x1, y2 - y1))
