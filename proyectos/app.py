"""
Sintonía Emocional - Chatbot Poético-Musical + Dashboard Analítico (Estable v1.0 - Legibilidad Perfecta)
--------------------------------------------------------------------------------------------------------
"""

# ==========================================
# IMPORTACIÓN DE LIBRERÍAS
# ==========================================
import pandas as pd                  # Para manejo, lectura y análisis de bases de datos (DataFrames).
import gradio as gr                  # Para crear la interfaz gráfica web interactiva de forma rápida.
from huggingface_hub import InferenceClient  # Para conectarnos y comunicarnos con el modelo de IA (Llama-3).
import urllib.parse                  # Para codificar textos y crear enlaces válidos para Spotify y YouTube.
import random                        # Para seleccionar aleatoriamente canciones o respuestas de emergencia.
from datetime import datetime        # Para registrar la fecha y hora exacta de cada interacción.
import os                            # Para interactuar con el sistema operativo y leer variables de entorno (seguridad).
import time                          # Para generar micro-pausas y crear el efecto visual de "escritura" del bot.

print("⏳ Iniciando el procesamiento y cruce de datos...")

print("Directorio actual:")
print(os.getcwd())

# ==========================================
# 0. BASE DE DATOS DE INTERACCIONES
# ==========================================
registro_interacciones = []

# ==========================================
# 1. CARGA Y PREPROCESAMIENTO DE DATOS
# ==========================================
try:
    # Obtener la ruta absoluta donde está app.py
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # Construir rutas seguras a los CSV
    spotify_path = os.path.join(BASE_DIR, "data", "spotify_data clean.csv")
    poesia_path = os.path.join(BASE_DIR, "data", "poesia_musica_sentimientos.csv")

    # Verificación de existencia
    print(f"📂 Ruta Spotify: {spotify_path}")
    print(f"📂 Ruta Poesía: {poesia_path}")

    if not os.path.exists(spotify_path):
        raise FileNotFoundError(f"No se encontró: {spotify_path}")

    if not os.path.exists(poesia_path):
        raise FileNotFoundError(f"No se encontró: {poesia_path}")

    # Cargar archivos
    df_spotify = pd.read_csv(
        spotify_path,
        encoding="utf-8",
        on_bad_lines="skip"
    )

    df_poesia = pd.read_csv(
        poesia_path,
        encoding="utf-8",
        on_bad_lines="skip"
    )

    print(f"✅ Spotify cargado: {df_spotify.shape}")
    print(f"✅ Poesía cargado: {df_poesia.shape}")

    print("Columnas df_poesia:")
    print(df_poesia.columns.tolist())

    print("\nPrimeras filas:")
    print(df_poesia.head(5))

    print("\nShape:")
    print(df_poesia.shape)

    # Limpieza para realizar el merge
    df_spotify["track_name_clean"] = (
        df_spotify["track_name"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    df_poesia["cancion_clean"] = (
        df_poesia["cancion_recomendada"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # Cruce de información
    df_datos = pd.merge(
        df_poesia,
        df_spotify,
        left_on="cancion_clean",
        right_on="track_name_clean",
        how="inner"
    )

    print(f"🔗 Registros vinculados: {df_datos.shape}")

    if df_datos.empty:
        print("⚠️ El merge se realizó pero no encontró coincidencias.")
        print("⚠️ Revisa los nombres de canciones entre ambos CSV.")

    emociones_disponibles = (
        df_datos["emocion_tag"]
        .dropna()
        .unique()
        .tolist()
    )

    print(
        f"✅ ¡Éxito! Vinculados registros. "
        f"Cantidad de emociones únicas listas para usar: "
        f"{len(emociones_disponibles)}"
    )

except Exception as e:
    print(f"❌ Error crítico al cargar los archivos: {e}")

    df_datos = pd.DataFrame()
    df_spotify = pd.DataFrame()
    emociones_disponibles = [
        "amor",
        "fuerza",
        "introspección",
        "melancolía"
    ]

# ==========================================
# 2. CONFIGURACIÓN DEL CLIENTE IA (SEGURIDAD Y AUTENTICACIÓN)
# ==========================================
# SEGURIDAD: Usamos os.getenv("HF_TOKEN") para buscar una variable secreta guardada en el entorno.
# NUNCA debemos escribir el token en texto plano en el código. Esto evita que si compartimos 
# el archivo, alguien más robe nuestra cuota o acceso a la API.
hf_token = os.getenv("HF_TOKEN")

# AUTENTICACIÓN: El "token" funciona como una llave criptográfica que le dice a Hugging Face 
# que somos usuarios autorizados para usar su Inteligencia Artificial.
client = InferenceClient(token=hf_token)

# ==========================================
# 3. LÓGICA PRINCIPAL DEL CHATBOT
# ==========================================
def chatbot_emocional(mensaje, historial):
    if df_datos.empty or df_spotify.empty:
        texto_error = "Lo siento, la base de datos no está disponible en este momento."
        for i in range(1, len(texto_error) + 1):
            time.sleep(0.01)
            yield texto_error[:i]
        return

    prompt_clasificacion = (
        f"El usuario dice: '{mensaje}'. "
        f"Clasifica su estado de ánimo seleccionando la palabra que MEJOR encaje ÚNICAMENTE de esta lista: {', '.join(emociones_disponibles)}. "
        f"Si la emoción exacta no está en la lista, elige la que tenga un sentimiento más parecido o sirva de apoyo. "
        f"Responde ESTRICTAMENTE con esa palabra elegida de la lista, sin texto extra ni puntos."
    )
    
    try:
        resp_clasif = client.chat_completion(
            model="meta-llama/Meta-Llama-3-8B-Instruct",
            messages=[{"role": "user", "content": prompt_clasificacion}],
            max_tokens=15, 
            temperature=0.1 
        )
        respuesta_bruta = resp_clasif.choices[0].message["content"].strip().lower()
        
        emocion_detectada = ""
        for emocion in emociones_disponibles:
            if str(emocion).lower() in respuesta_bruta:
                emocion_detectada = str(emocion).lower()
                break
                
    except Exception as e:
        print(f"⚠️ Alerta API (Clasificación): Servidor saturado. ({e})")
        emocion_detectada = "" 

    if emocion_detectada not in emociones_disponibles:
        comodines_neutrales = ["fuerza", "introspección", "melancolía", "sanación", "amor"]
        comodines_presentes = [c for c in comodines_neutrales if c in emociones_disponibles]
        
        if comodines_presentes:
            emocion_detectada = random.choice(comodines_presentes)
        else:
            emocion_detectada = random.choice(emociones_disponibles)

    dataset_filtrado = df_datos[df_datos['emocion_tag'] == emocion_detectada]
    if dataset_filtrado.empty:
        dataset_filtrado = df_datos

    cantidad_exactas = min(3, len(dataset_filtrado))
    playlist_exacta = dataset_filtrado.sample(n=cantidad_exactas)
    
    poema_base = playlist_exacta.iloc[0]
    autor = poema_base['autor']
    frase = poema_base['frase_motivacional']
    cancion_principal = str(poema_base['track_name'])
    artista_principal = str(poema_base['artist_name'])

    now = datetime.now()
    registro_interacciones.append({
        "Fecha": now.strftime("%Y-%m-%d"),
        "Año_Mes": now.strftime("%Y-%m"),
        "Hora": now.strftime("%H:%M:%S"),
        "Emocion_Clave": emocion_detectada.capitalize(),
        "Cancion_Recomendada": cancion_principal,
        "Artista_Asociado": artista_principal
    })

    prompt_ia = (
        f"El usuario expresó: '{mensaje}'. (Emoción clasificada: '{emocion_detectada}'). "
        f"Poema de {autor}: '{frase}'. "
        f"Escribe una respuesta MUY BREVE (máximo 2 líneas), empática y poética en español. "
        f"Menciona al autor y cierra diciendo que le preparaste música acorde."
    )
    
    try:
        response = client.chat_completion(
            model="meta-llama/Meta-Llama-3-8B-Instruct",
            messages=[{"role": "user", "content": prompt_ia}],
            max_tokens=100
        )
        respuesta_ia = response.choices[0].message["content"]
    except Exception as e:
        print(f"⚠️ Alerta API (Generación): Servidor saturado. ({e})")
        mensajes_emergencia = [
            f"Aquí tienes unas profundas palabras de {autor}: '{frase}'. Espero que esta selección musical acompañe tu sentir.",
            f"A veces la mejor respuesta está en la poesía. Como dice {autor}: '{frase}'. Te he preparado esta música.",
            f"Escucha esta reflexión de {autor}: '{frase}'. Que estas melodías te sirvan de refugio."
        ]
        respuesta_ia = random.choice(mensajes_emergencia)
    
    texto_playlist = f"───────────────\n🎧 **Tu Playlist de '{emocion_detectada.capitalize()}':**\n\n"
    contador = 1
    
    for _, row in playlist_exacta.iterrows():
        cancion = str(row['track_name'])
        artista = str(row['artist_name'])
        query_busqueda = f"{cancion} {artista}"
        link_spotify = f"https://open.spotify.com/search/{urllib.parse.quote(query_busqueda)}"
        link_youtube = f"https://www.youtube.com/results?search_query={urllib.parse.quote_plus(query_busqueda)}"
        
        texto_playlist += f"**{contador}. {cancion}** — {artista} *(Conecta con el poema)*\n"
        texto_playlist += f"  ↳ 🎵 [Spotify]({link_spotify}) | 📺 [YouTube]({link_youtube})\n\n"
        contador += 1

    canciones_faltantes = 5 - len(playlist_exacta) 
    if canciones_faltantes > 0:
        extras = df_spotify.sample(n=canciones_faltantes) 
        for _, row in extras.iterrows():
            cancion = str(row['track_name'])
            artista = str(row['artist_name'])
            query_busqueda = f"{cancion} {artista}"
            link_spotify = f"https://open.spotify.com/search/{urllib.parse.quote(query_busqueda)}"
            link_youtube = f"https://www.youtube.com/results?search_query={urllib.parse.quote_plus(query_busqueda)}"
            
            texto_playlist += f"**{contador}. {cancion}** — {artista} *(Recomendación extra)*\n"
            texto_playlist += f"  ↳ 🎵 [Spotify]({link_spotify}) | 📺 [YouTube]({link_youtube})\n\n"
            contador += 1

    link_playlist_global = f"https://open.spotify.com/search/{urllib.parse.quote(emocion_detectada)}/playlists"
    texto_playlist += f"✨ **[Explorar más playlists de '{emocion_detectada}' en Spotify]({link_playlist_global})**"

    texto_final = f"{respuesta_ia}\n\n{texto_playlist}"

    for i in range(1, len(texto_final) + 1, 4):
        time.sleep(0.01)
        yield texto_final[:i]
    yield texto_final

# ==========================================
# 4. FUNCIÓN DEL DASHBOARD 
# ==========================================
def actualizar_dashboard():
    if not registro_interacciones:
        df_vacio_emo = pd.DataFrame({"Emocion": ["Sin interacciones"], "Cantidad": [0]})
        df_vacio_top = pd.DataFrame({"Información": ["Esperando registros en el chat..."]})
        return gr.BarPlot(value=df_vacio_emo), df_vacio_top, df_vacio_top, gr.DownloadButton(interactive=False)
    
    df_registro = pd.DataFrame(registro_interacciones)
    
    df_conteo = df_registro['Emocion_Clave'].value_counts().reset_index()
    df_conteo.columns = ['Emocion', 'Cantidad']
    df_conteo['Cantidad'] = df_conteo['Cantidad'].astype(int)
    
    grafico_actualizado = gr.BarPlot(
        value=df_conteo,
        x="Emocion",
        y="Cantidad",
        title="Frecuencia de Emociones Detectadas",
        color="Emocion"
    )
    
    top_canciones = df_registro['Cancion_Recomendada'].value_counts().reset_index().head(5)
    top_canciones.columns = ['Canción Recomendada (Top)', 'Veces Enviada']
    
    top_artistas = df_registro['Artista_Asociado'].value_counts().reset_index().head(5)
    top_artistas.columns = ['Artista Frecuente', 'Apariciones']
    
    ruta_archivo = "analisis_tiempo_sintonia.csv"
    df_registro.to_csv(ruta_archivo, index=False, encoding="utf-8-sig")
    
    return grafico_actualizado, top_canciones, top_artistas, gr.DownloadButton(value=ruta_archivo, interactive=True)

# ==========================================
# 5. INTERFAZ DE USUARIO (GRADIO)
# ==========================================
frutiger_css = """
/* Fondo general */
body, .gradio-container { 
    background: linear-gradient(135deg, #a1e2f5 0%, #e2fcd6 50%, #85d8f0 100%) !important; 
    font-family: 'Arial Rounded MT Bold', 'Trebuchet MS', 'Segoe UI', sans-serif !important; 
}

/* Forzar TODOS los textos principales e instrucciones a NEGRO */
.gradio-container h1, .gradio-container h2, .gradio-container h3, .gradio-container p, .gradio-container span, .gradio-container label, .prose * { 
    color: #000000 !important; 
}

/* Forzar los botones de EJEMPLOS a tener texto negro y fondo visible */
.gradio-container button.example {
    color: #000000 !important;
    border: 1px solid #5bb2e6 !important;
    background: rgba(255, 255, 255, 0.8) !important;
}
.gradio-container button.example:hover {
    background: #d9f8ff !important;
}

/* Burbuja de los mensajes que escribe el USUARIO (Se mantiene texto BLANCO) */
.message-wrap .message.user { 
    background: linear-gradient(180deg, #2087eb 0%, #1a6abf 100%) !important; 
    border-radius: 20px 20px 0px 20px !important; 
    border: none !important; 
}
.message-wrap .message.user p, .message-wrap .message.user span { 
    color: #ffffff !important; 
}

/* Burbuja de las respuestas del BOT */
.message-wrap .message.bot { 
    background: #ffffff !important; 
    border-radius: 20px 20px 20px 0px !important; 
    border: 2px solid #a8dbff !important; 
}
.message-wrap .message.bot p { 
    color: #000000 !important; 
}
.message-wrap .message.bot a { 
    color: #0088cc !important; 
    font-weight: bold !important; 
    text-decoration: underline !important; 
}

/* Caja de texto (Donde se escribe) */
.textbox-container textarea { 
    background: #ffffff !important; 
    border: 2px solid #5bb2e6 !important; 
    color: #000000 !important; 
    font-weight: 500 !important; 
}
.textbox-container textarea::placeholder {
    color: #555555 !important;
}

/* Estilo de los botones principales (Enviar, Limpiar, Actualizar) */
button { 
    background: linear-gradient(180deg, #b3f0ff 0%, #4dc4ff 100%) !important; 
    border: 1px solid #0088cc !important; 
    border-radius: 25px !important; 
    color: #000000 !important; 
    font-weight: bold !important; 
}
button:hover { 
    background: linear-gradient(180deg, #d9f8ff 0%, #7accff 100%) !important; 
}
"""

with gr.Blocks(css=frutiger_css, theme=gr.themes.Base()) as demo:
    gr.Markdown("# 🫧 Sintonía Emocional: IA & Analítica Musical")
    
    with gr.Tabs():
        # PESTAÑA CHATBOT
        with gr.TabItem("💬 Chatbot Poético"):
            gr.Markdown("### Cuéntame cómo te sientes. Encontraré las palabras y la música perfecta para ti.")
            
            gr.Markdown(
                "💡 **¿No sabes qué decir?** Puedes guiar a la inteligencia artificial usando palabras clave. "
                "Por ejemplo, puedes escribir: *«Siento que estoy un poco perdido, busco **sanación**»*, "
                "o *«Me siento con mucha **melancolía**»*, o *«Necesito **fuerza** para el día de hoy»*."
            )
            
            gr.ChatInterface(
                fn=chatbot_emocional,
                textbox=gr.Textbox(placeholder="Hoy me siento...", container=False, scale=7),
                examples=[
                    "🕰️ Me siento con mucha nostalgia recordando el pasado...",
                    "🌧️ Hoy tuve un día muy pesado, busco algo de sanación.",
                    "💔 Tengo el corazón roto y siento demasiada tristeza...",
                    "✨ ¡Me siento increíblemente bien! Lleno de energía y amor."
                ]
            )
            
        # PESTAÑA DASHBOARD AVANZADO
        with gr.TabItem("📊 Dashboard Analítico (En Vivo)"):
            gr.Markdown(
                "### Panel de Control de Inteligencia de Negocios (BI)\n"
                "Mapeo estratégico en tiempo real de interacciones analíticas, métricas de frecuencia y descargas históricas."
            )
            
            with gr.Row():
                btn_actualizar = gr.Button("🔄 Actualizar Dashboard")
                btn_descargar = gr.DownloadButton("📥 Exportar Datos Analíticos (CSV)", interactive=False)
            
            df_inicial = pd.DataFrame({"Emocion": ["Esperando datos..."], "Cantidad": [0]})
            grafico_barras = gr.BarPlot(
                value=df_inicial, 
                x="Emocion", 
                y="Cantidad", 
                title="Frecuencia de Emociones Detectadas", 
                tooltip=["Emocion", "Cantidad"],
                color="Emocion"
            )
            
            with gr.Row():
                tabla_canciones = gr.Dataframe(label="🏆 Top Canciones Más Recomendadas (Dataset)")
                tabla_artistas = gr.Dataframe(label="🎤 Top Artistas Frecuentes Asociados")
            
            btn_actualizar.click(
                fn=actualizar_dashboard, 
                outputs=[grafico_barras, tabla_canciones, tabla_artistas, btn_descargar]
            )

if __name__ == "__main__":
    print("🚀 Lanzando la aplicación con Chatbot y Dashboard...")
    demo.launch(css=frutiger_css, theme=gr.themes.Base())
