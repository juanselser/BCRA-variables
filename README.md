# Comparador de Variables Económicas Argentinas

Esta aplicación desarrollada con **Streamlit** permite comparar de forma interactiva diversas variables monetarias, cambiarias y financieras de Argentina, como:

- Reservas Internacionales
- Base Monetaria
- Tipo de cambio oficial y paralelo (blue)
- Merval en USD
- Tasa de política monetaria
- Inflación mensual

## 📊 Funcionalidades

- Seleccionar dos variables desde menús desplegables.
- Visualización de ambas en un gráfico interactivo con doble eje.
- Datos obtenidos en tiempo real desde:
  - API del BCRA
  - API de BlueLyTics
  - Yahoo Finance (para el índice Merval)

## 🚀 Cómo usar

1. Cloná este repositorio o subilo a Streamlit Cloud.
2. Asegurate de que los archivos `comparador_economico_arg.py` y `requirements.txt` estén en la misma carpeta.
3. Ejecutá localmente con:

```bash
streamlit run comparador_economico_arg.py
```

O bien, subí todo a [Streamlit Cloud](https://streamlit.io/cloud).

## 🛠 Requisitos

Las dependencias se detallan en `requirements.txt` e incluyen:

- streamlit
- pandas
- requests
- plotly
- yfinance

---

Desarrollado por Juan Ramón Selser.
