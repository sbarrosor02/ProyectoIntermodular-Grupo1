import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
from datetime import datetime
import time

# Configuración de la página
st.set_page_config(page_title="Monitor de Aula", layout="wide", page_icon="📊")

# --- CONFIGURACIÓN BASE DE DATOS ---
DB_CONFIG = {
    "host": "localhost",
    "database": "monitor_aula",
    "user": "postgres",
    "password": "password123!",
    "port": "5432"
}

def get_data():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        query = "SELECT id, timestamp, cantidad_personas FROM ocupacion_aula ORDER BY timestamp DESC"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error al conectar con la BD: {e}")
        return pd.DataFrame()

# Título de la app
st.title("Monitorizacion de Aula en Tiempo Real")
st.markdown("Dashboard para el seguimiento de ocupacion mediante IA.")

# Configuración de auto-refresco en la barra lateral
with st.sidebar:
    st.header("Configuracion")
    auto_refresh = st.checkbox("Auto-refresco (cada 60s)", value=True)
    if st.button("Actualizar ahora"):
        st.rerun()

# Obtener datos
df = get_data()

if not df.empty:
    ultima_ocupacion = int(df.iloc[0]['cantidad_personas'])
    ultima_fecha = df.iloc[0]['timestamp']
    max_ocupacion = int(df['cantidad_personas'].max())
    promedio = df['cantidad_personas'].mean()
    total_registros = len(df)

    # --- FILA 1: MÉTRICAS CLAVE ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Ocupacion Actual", f"{ultima_ocupacion} pers.")
    col2.metric("Ocupacion Maxima", f"{max_ocupacion} pers.")
    col3.metric("Promedio", f"{promedio:.1f} pers.")
    col4.metric("Total registros", total_registros)

    st.caption(f"Ultimo dato: {ultima_fecha.strftime('%d/%m/%Y %H:%M:%S') if hasattr(ultima_fecha, 'strftime') else ultima_fecha}")

    # --- FILA 2: GRÁFICO DE LÍNEA ---
    st.subheader("Evolucion de la Ocupacion")
    df_grafico = df.sort_values('timestamp')
    fig = px.line(
        df_grafico, x='timestamp', y='cantidad_personas',
        title='Personas en el aula a lo largo del tiempo',
        labels={'timestamp': 'Fecha y Hora', 'cantidad_personas': 'N Personas'}
    )
    fig.update_layout(template="plotly_dark")
    fig.update_traces(line_color='#00d4ff')
    st.plotly_chart(fig, use_container_width=True)

    # --- FILA 3: GRÁFICO DE BARRAS (últimas 20 lecturas) ---
    st.subheader("Ultimas 20 lecturas")
    df_recientes = df.head(20).sort_values('timestamp')
    fig2 = px.bar(
        df_recientes, x='timestamp', y='cantidad_personas',
        labels={'timestamp': 'Hora', 'cantidad_personas': 'Personas'},
        color='cantidad_personas',
        color_continuous_scale='RdYlGn_r'
    )
    fig2.update_layout(template="plotly_dark", showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

    # --- FILA 4: TABLA DE DATOS ---
    with st.expander("Ver historial completo de datos"):
        st.dataframe(
            df[['id', 'timestamp', 'cantidad_personas']].rename(columns={
                'id': 'ID',
                'timestamp': 'Fecha y Hora',
                'cantidad_personas': 'Personas'
            }),
            use_container_width=True
        )

else:
    st.warning("No hay datos en la base de datos. Asegurate de que fase1_deteccion.py este funcionando.")

# Auto-refresco
if auto_refresh:
    time.sleep(60)
    st.rerun()
