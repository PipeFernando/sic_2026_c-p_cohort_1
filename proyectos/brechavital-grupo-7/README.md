# 🏥 GESAssist: Análisis y Clasificación de Diagnósticos GES

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-green.svg)
![Plotly](https://img.shields.io/badge/Plotly-Express-orange.svg)

## 📌 Descripción del Proyecto
GESAssist es una aplicación interactiva desarrollada en **Python** con **Streamlit** que permite analizar y visualizar un conjunto de datos médicos enfocado en la clasificación de Garantías Explícitas en Salud (GES). 

El objetivo principal de este proyecto es explorar patrones en los diagnósticos para entender **qué variables (como la edad o el tipo de diagnóstico) influyen en que un caso sea clasificado como GES o No GES**. A través de visualizaciones interactivas y métricas en tiempo real, facilitamos la toma de decisiones exploratorias basadas en datos.

---

## 🚀 Aplicación en Vivo (Dashboard)
Puedes acceder y probar la aplicación directamente desde tu navegador sin instalar nada:

🌐 **[🔗 Enlace al Dashboard GESAssist en Streamlit Cloud](https://mtys24-gesassist-app-trds27.streamlit.app/)**  


---

## 📊 Dataset y Origen de los Datos

**GES Classification Dataset** — [Kaggle](https://www.kaggle.com/datasets/raviiloveyou/classification-datasetges)

In Chile, a patient needing a specialty consultation or surgery has to first be referred by a general practitioner, then placed on a waiting list. The Explicit Health Guarantees (GES in Spanish) ensure, by law, the maximum time to solve an important set of health problems. Usually, a health professional manually verifies if each referral, written in natural language, corresponds or not to a GES-covered disease. An error in this classification is catastrophic for patients, as it puts them on a non-prioritized waiting list, characterized by prolonged waiting times.

The dataset contains **~883 samples** with **3 features** (id, diagnostic, age) and **1 class label** (ges: True/False). The task is to develop a model that can linearly separate between the two classes.

* **Volumen:** 883 registros, 260 GES (27.6%), 681 No GES (72.4%)
* **Fuente:** Kaggle — [classification-datasetges](https://www.kaggle.com/datasets/raviiloveyou/classification-datasetges)

---

## 🎯 Hipótesis

**¿Puede un modelo basado en inteligencia artificial identificar correctamente los casos GES utilizando el diagnóstico y la edad del paciente?**

Creemos que sí. Dado que las enfermedades GES están definidas por ley para un conjunto específico de patologías y rangos etarios, un modelo de clasificación entrenado con datos históricos debería ser capaz de aprender estos patrones y predecir con alta precisión si un caso corresponde o no a GES, basándose únicamente en el diagnóstico (texto) y la edad del paciente.

---

## 🛠️ Instrucciones de Instalación Local
Si deseas ejecutar este proyecto en tu propia máquina, sigue estos pasos:

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/Mtys24/GESAssist.git
   cd GESAssist
   ```

2. **Crear un entorno virtual (recomendado):**
   ```bash
   python -m venv venv
   # En Windows:
   venv\Scripts\activate
   # En Mac/Linux:
   source venv/bin/activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar el Asistente de IA (Opcional pero recomendado):**
   Para habilitar la pestaña del Asistente de Inteligencia Artificial (Llama-3), debes configurar tu token gratuito de HuggingFace.
   - Crea una copia del archivo `.env.example` y renómbralo a `.env`.
   - Abre `.env` y pega tu token: `HF_TOKEN=hf_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`.
   *(Si omites este paso, el dashboard funcionará perfectamente, pero la pestaña de la IA estará desactivada).*

5. **Ejecutar la aplicación Streamlit:**
   ```bash
   streamlit run app.py
   ```

---

## 📂 Estructura del Repositorio
```
GESAssist/
├── app.py                   # Script principal del Dashboard en Streamlit
├── data/
│   ├── dataset_original.csv # Dataset crudo
│   └── dataset_limpio.csv   # Dataset procesado
├── notebooks/
│   ├── 01_eda.ipynb         # Análisis Exploratorio de Datos
│   ├── 02_limpieza.ipynb    # Pipeline de limpieza y transformación
│   └── 03_analisis.ipynb    # Respuestas a la pregunta principal
├── outputs/                 # Gráficos e imágenes exportadas
├── requirements.txt         # Dependencias del proyecto

```

---

## 🧑‍💻 Equipo de Trabajo

| Integrante                | Rol en el Proyecto                 | GitHub                                      |
|---------------------------|------------------------------------|---------------------------------------------|
| **Matías Manríquez**      | Data Scientist & Analista de Datos | [@Mtys24](https://github.com/Mtys24)        |
| **José Salgado Escalona** | Data Scientist & Analista de Datos | [@JoseRicardoSE](https://github.com/JoseRicardoSE) |
| **Ignacio Madriaga**      | Data Scientist & Analista de Datos | [@VonCreed-tech](https://github.com/VonCreed-tech) |
| **Daniel Segovia**        | Data Scientist & Analista de Datos | [@reyconker](https://github.com/reyconker)   |

---
*Desarrollado para el proyecto final de Data Science.*
