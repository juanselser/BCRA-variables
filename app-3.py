import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.title("Comparativa: Variable Monetaria vs Tipo de Cambio USD (BCRA)")

# =============================
# OBTENER VARIABLES DISPONIBLES
# =============================
# url_var_info = "https://api.bcra.gob.ar/estadisticas/v3.0/monetarias"
# res_info = requests.get(url_var_info, verify=False)

# if res_info.status_code != 200:
#     st.stop("No se pudieron obtener las variables disponibles desde la API del BCRA.")

# df_info = pd.DataFrame(res_info.json()["results"])
# df_info = df_info.sort_values("descripcion")

# # Selección de variable desde selectbox
# descripcion_seleccionada = st.selectbox("Seleccioná una variable monetaria", df_info["descripcion"])
# id_variable = df_info[df_info["descripcion"] == descripcion_seleccionada].iloc[0]["idVariable"]


# =============================
# OBTENER VARIABLES DISPONIBLES (SOLO CÓDIGOS 15 Y 1)
# =============================
url_var_info = "https://api.bcra.gob.ar/estadisticas/v3.0/monetarias"
res_info = requests.get(url_var_info, verify=False)

if res_info.status_code != 200:
    st.stop("No se pudieron obtener las variables disponibles desde la API del BCRA.")

# Filtrar solo códigos 15 y 1
df_info = pd.DataFrame(res_info.json()["results"])
df_info = df_info[df_info["idVariable"].isin([15, 1])]  # ← Filtro clave
df_info = df_info.sort_values("descripcion")


# Selección de variable desde selectbox
descripcion_seleccionada = st.selectbox("Seleccioná una variable monetaria", df_info["descripcion"])
id_variable = df_info[df_info["descripcion"] == descripcion_seleccionada].iloc[0]["idVariable"]


# =============================
# SELECCIÓN DE FECHAS
# =============================
hoy = datetime.today()
fecha_inicio = st.date_input("Fecha de inicio", datetime(2024, 1, 1))
fecha_fin = st.date_input("Fecha de fin", hoy)

if fecha_inicio > fecha_fin:
    st.warning("La fecha de inicio no puede ser posterior a la fecha de fin.")
    st.stop()

# =============================
# CARGAR VARIABLE MONETARIA
# =============================
url_data = f"https://api.bcra.gob.ar/estadisticas/v3.0/monetarias/{id_variable}"
params = {"desde": fecha_inicio.strftime("%Y-%m-%d"), "hasta": fecha_fin.strftime("%Y-%m-%d"), "limit": 3000}
r = requests.get(url_data, params=params, verify=False)

if r.status_code != 200:
    st.stop("Error al obtener los datos de la variable monetaria.")

data = r.json()["results"]
df_v = pd.DataFrame(data)
df_v["fecha"] = pd.to_datetime(df_v["fecha"])
df_v = df_v[["fecha", "valor"]].rename(columns={"valor": "valor_variable"})

# =============================
# COTIZACIÓN USD
# =============================
url_usd = "https://api.bcra.gob.ar/estadisticascambiarias/v1.0/Cotizaciones/USD"
params_usd = {
    "fechadesde": fecha_inicio.strftime("%Y-%m-%d"),
    "fechahasta": fecha_fin.strftime("%Y-%m-%d"),
    "limit": 1000
}
r_usd = requests.get(url_usd, params=params_usd, verify=False)

if r_usd.status_code != 200:
    st.stop("Error al obtener el tipo de cambio USD.")

data_usd = r_usd.json()["results"]
usd_registros = []
for dia in data_usd:
    fecha = dia["fecha"]
    for cot in dia["detalle"]:
        if isinstance(cot["tipoCotizacion"], (int, float)):
            usd_registros.append({"fecha": fecha, "tipoCotizacion": cot["tipoCotizacion"]})

df_usd = pd.DataFrame(usd_registros)
df_usd["fecha"] = pd.to_datetime(df_usd["fecha"])
df_usd = df_usd.groupby("fecha").mean(numeric_only=True).reset_index()

# =============================
# COTIZACIÓN USD BLUE (Bluelytics)
# =============================
def get_usd_blue(fecha_inicio, fecha_fin):
    try:
        url = "https://api.bluelytics.com.ar/v2/evolution.json"
        r = requests.get(url)
        
        if r.status_code != 200:
            st.warning("Error al obtener datos del dólar blue")
            return None
            
        data = r.json()
        
        # Filtrar y procesar datos
        blue_data = [entry for entry in data if entry["source"] == "Blue"]
        df = pd.DataFrame(blue_data)
        
        # Convertir y filtrar fechas
        df["fecha"] = pd.to_datetime(df["date"])
        df = df[(df["fecha"] >= pd.to_datetime(fecha_inicio)) & 
                (df["fecha"] <= pd.to_datetime(fecha_fin))]
        
        # Calcular promedio blue
        df["tipoCotizacion"] = (df["value_buy"] + df["value_sell"]) / 2
        
        return df[["fecha", "tipoCotizacion"]]
        
    except Exception as e:
        st.error(f"Error al obtener dólar blue: {str(e)}")
        return None

# Uso en tu aplicación:
df_usd_blue = get_usd_blue(fecha_inicio, fecha_fin)

if df_usd_blue is not None and not df_usd_blue.empty:
    # Aquí puedes usar df_usd_blue igual que df_usd del oficial
    st.success("Datos del dólar blue obtenidos correctamente")
else:
    st.warning("No se pudieron obtener datos del dólar blue para el período seleccionado")

# UNIR DATOS
# =============================
df = pd.merge(df_v, df_usd, on="fecha", how="inner")
if df.empty:
    st.stop("No hay datos para el período seleccionado.")

# # =============================
# # GRAFICAR
# # =============================
# fig = go.Figure()

# fig.add_trace(go.Scatter(
#     x=df["fecha"],
#     y=df["valor_variable"],
#     mode='lines',
#     name=descripcion_seleccionada,
#     yaxis="y1"
# ))

# fig.add_trace(go.Scatter(
#     x=df["fecha"],
#     y=df["tipoCotizacion"],
#     mode='lines',
#     name="Tipo de Cambio USD",
#     yaxis="y2"
# ))

# try:
#     fig.update_layout(
#         title=f"{descripcion_seleccionada} vs Tipo de Cambio USD (BCRA)",
#         xaxis=dict(title="Fecha"),
#         yaxis=dict(title=descripcion_seleccionada, tickfont=dict(color="blue")),
#         yaxis2=dict(title="Tipo de Cambio USD",
#                     tickfont=dict(color="red"), overlaying="y", side="right"),
#         legend=dict(x=0.01, y=0.99),
#         height=500,
#         width=900
#     )
# except Exception as e:
#     st.error(f"Error al actualizar el layout: {e}")
#     st.stop()

# st.plotly_chart(fig, use_container_width=True)

# =============================
# GRAFICAR (CON DÓLAR BLUE)
# =============================
fig = go.Figure()

# 1. Variable monetaria seleccionada (eje Y izquierdo)
fig.add_trace(go.Scatter(
    x=df["fecha"],
    y=df["valor_variable"],
    mode='lines',
    name=descripcion_seleccionada,
    yaxis="y1",
    line=dict(color='blue')
))

# 2. Dólar Oficial (eje Y derecho)
fig.add_trace(go.Scatter(
    x=df["fecha"],
    y=df["tipoCotizacion"],
    mode='lines',
    name="Dólar Oficial",
    yaxis="y2",
    line=dict(color='green')
))

# 3. Dólar Blue (eje Y derecho)
 # Verificar si tenemos datos de blue
fig.add_trace(go.Scatter(
    x=df["fecha"],
    y=df["usd_blue"],
    mode='lines',
    name="Dólar Blue",
    yaxis="y2",
    line=dict(color='red', dash='dot')
))

# try:
#     fig.update_layout(
#         title=f"{descripcion_seleccionada} vs Tipos de Cambio USD",
#         xaxis=dict(title="Fecha"),
#         yaxis=dict(
#             title=descripcion_seleccionada, 
#             tickfont=dict(color="blue"),
#             side="left"
#         ),
#         yaxis2=dict(
#             title="Tipos de Cambio USD (Oficial y Blue)",
#             tickfont=dict(color="red"), 
#             overlaying="y", 
#             side="right",
#             showgrid=False  # Opcional: mejora la legibilidad
#         ),
#         legend=dict(
#             x=0.01, 
#             y=0.99,
#             bgcolor='rgba(255,255,255,0.5)'  # Fondo semitransparente
#         ),
#         height=500,
#         width=900,
#         hovermode="x unified"  # Muestra todos los valores al pasar el mouse
#     )
# except Exception as e:
#     st.error(f"Error al actualizar el layout: {e}")
#     st.stop()

st.plotly_chart(fig, use_container_width=True)
