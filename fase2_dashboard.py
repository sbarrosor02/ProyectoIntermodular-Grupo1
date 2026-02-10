import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
from datetime import datetime
import os

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
        query = "SELECT id, timestamp, cantidad_personas, foto_path FROM ocupacion_aula ORDER BY timestamp DESC"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error al conectar con la BD: {e}")
        return pd.DataFrame()

# Título de la app
st.title("📊 Monitorización de Aula en Tiempo Real")
st.markdown("Dashboard para el seguimiento de ocupación mediante IA.")

# Botón de refrescar
if st.button('🔄 Actualizar Datos'):
    st.rerun()

# Obtener datos
df = get_data()

if not df.empty:
    # --- FILA 1: MÉTRICAS CLAVE ---
    col1, col2, col3 = st.columns(3)
    
    ultima_ocupacion = df.iloc[0]['cantidad_personas']
    ultima_fecha = df.iloc[0]['timestamp']
    max_ocupacion = df['cantidad_personas'].max()
    promedio = df['cantidad_personas'].mean()

    col1.metric("Ocupación Actual", f"{ultima_ocupacion} pers.")
    col2.metric("Ocupación Máxima", f"{max_ocupacion} pers.")
    col3.metric("Promedio Diario", f"{promedio:.1f} pers.")

    # --- FILA 2: GRÁFICO ---
    st.subheader("📈 Evolución de la Ocupación")
    fig = px.line(df, x='timestamp', y='cantidad_personas', 
                 title='Personas en el aula a lo largo del tiempo',
                 labels={'timestamp': 'Fecha y Hora', 'cantidad_personas': 'Nº Personas'})
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    # --- FILA 3: ÚLTIMAS CAPTURAS ---
    st.subheader("📷 Últimas capturas de evidencia")
    
    # Mostrar las 4 últimas fotos que existan en disco
    fotos_validas = df[df['foto_path'].apply(lambda x: os.path.exists(x) if x else False)].head(4)
    
    if not fotos_validas.empty:
        cols_fotos = st.columns(len(fotos_validas))
        for i, (_, row) in enumerate(fotos_validas.iterrows()):
            with cols_fotos[i]:
                st.image(row['foto_path'], caption=f"{row['timestamp'].strftime('%H:%M:%S')} - {row['cantidad_personas']} pers.")
    else:
        st.info("No hay fotos disponibles todavía en la carpeta /capturas.")

    # --- FILA 4: TABLA DE DATOS ---
    with st.expander("📄 Ver historial completo de datos"):
        st.dataframe(df, use_container_width=True)

else:
    st.warning("No hay datos en la base de datos. Asegúrate de que fase1_deteccion.py esté funcionando.")
