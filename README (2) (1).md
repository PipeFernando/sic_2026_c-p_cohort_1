# 🎧 Detonantes de Frustración en Clientes de Call Center

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red?logo=streamlit)
![Pandas](https://img.shields.io/badge/Data-Pandas-green?logo=pandas)

Un sistema de análisis inteligente que clasifica conversaciones de soporte técnico para identificar patrones de insatisfacción del cliente, permitiendo transformar datos crudos en escenarios prácticos de capacitación para equipos de atención.

## 👥 Equipo
* **Felipe Laflor** - GitHub: [@PipeFernando](https://github.com/PipeFernando)
* **Pollet Vallejos** - GitHub: [@vpolletv](https://github.com/vpolletv)
* **Paloma Paredes** - GitHub: [@payioma](https://github.com/payioma)
* **Fernando Marihuen** - GitHub: [@fernandomarihuenjmv-cmyk](https://github.com/fernandomarihuenjmv-cmyk)
* **Javiera** - GitHub: [@](https://github.com/)
* **Francisco Lopez** - GitHub: [@panchorq](https://github.com/panchorq)

---

## 🎯 Pregunta de Análisis
> *¿Cuáles son los principales detonantes de frustración en clientes y cómo pueden utilizarse para diseñar escenarios de entrenamiento para agentes de soporte?*

## 💡 Hallazgo Principal
El análisis revela que la demora en los tiempos de respuesta y los fallos técnicos recurrentes son los principales detonantes de frustración en los clientes. A través de la clasificación automatizada, se identificaron patrones claros que permiten priorizar los casos negativos, facilitando el diseño de escenarios de entrenamiento específicos para que los agentes de soporte puedan manejar estas situaciones con mayor empatía y eficacia.

---

## 📊 Dataset
El proyecto utiliza datos reales de interacciones de soporte técnico en redes sociales.
* **Fuente:** [Dataset Original (TWCS)](https://drive.google.com/file/d/1BggtUCIAJ_RsZH158DiDgwqvJOjjiLBD/view?usp=drive_link)
* **Dataset Procesado:** [Dataset Limpio](https://drive.google.com/file/d/10y0VsKfzGMUftdRZr4KDelaeWS9hDhDb/view?usp=drive_link)
* **Descripción:** El dataset procesado incluye análisis de sentimiento y clasificación de detonantes de frustración, optimizado para el entrenamiento de agentes de soporte.

---

## 🏗️ Estructura del Proyecto
```text
proyectos/
└── grupo_8/
    ├── data/
    │   ├── dataset_original.csv.txt           # Dataset crudo
    │   └── dataset_limpio.csv.txt             # Dataset procesado
    ├── notebooks/
    │   ├── 01_eda_limpieza_analisis.ipynb     # Eda, limpieza y analisis, proyecto final
    │   ├── V1-proyecto.ipynb                  # Eda, limpieza y analisis, primera parte
    ├── outputs
    ├── app.py                                 # archivo app.py con dashboard en streamlit
    ├── requirements.txt                       # Dependencias del proyecto
  
  