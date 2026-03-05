# Proyecto Intermodular - Grupo 1: Monitor de Ocupación de Aula con IA

Sistema de detección de personas en tiempo real mediante YOLOv8 y cámara web, con almacenamiento automático en base de datos PostgreSQL y visualización en un dashboard web interactivo.

## Descripción

El sistema consta de dos componentes que funcionan en paralelo:

- **`fase1_deteccion.py`**: Captura video de la cámara, detecta personas con YOLOv8 y guarda el conteo en la base de datos cada 60 segundos.
- **`fase2_dashboard.py`**: Dashboard web (Streamlit) que muestra la ocupación en tiempo real con gráficas y métricas, actualizándose automáticamente cada 60 segundos.

## Requisitos previos

- Python 3.9 – 3.11
- PostgreSQL instalado y en ejecución
- Cámara web conectada al equipo
- (Opcional) GPU NVIDIA con CUDA 12.1 para mayor rendimiento

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/sbarrosor02/ProyectoIntermodular-Grupo1.git
cd ProyectoIntermodular-Grupo1
```

### 2. Crear y activar un entorno virtual

```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar la base de datos

Asegúrate de que PostgreSQL está en ejecución. Luego abre `fase1_deteccion.py` y `fase2_dashboard.py` y edita el bloque `DB_CONFIG` con tus credenciales:

```python
DB_CONFIG = {
    "host": "localhost",
    "database": "monitor_aula",
    "user": "postgres",
    "password": "TU_CONTRASEÑA",
    "port": "5432"
}
```

La base de datos y la tabla se crean automáticamente al lanzar `fase1_deteccion.py` por primera vez. Solo necesitas que el servidor PostgreSQL esté activo y que el usuario tenga permisos para crear bases de datos (o crearla manualmente con `CREATE DATABASE monitor_aula;`).

## Uso

Necesitas **dos terminales abiertas** simultáneamente.

### Terminal 1 — Detección con cámara

```bash
python fase1_deteccion.py
```

- Se abre una ventana con el video de la cámara y las detecciones en tiempo real
- El conteo de personas se guarda en la base de datos cada 60 segundos
- Pulsa `q` en la ventana de video para cerrar el programa

### Terminal 2 — Dashboard web

```bash
streamlit run fase2_dashboard.py
```

- Se abre el navegador automáticamente en `http://localhost:8501`
- El dashboard se actualiza solo cada 60 segundos
- Desde la barra lateral puedes desactivar el auto-refresco o actualizarlo manualmente

## Estructura del proyecto

```
ProyectoIntermodular-Grupo1/
├── fase1_deteccion.py      # Detección YOLOv8 + guardado en BD
├── fase2_dashboard.py      # Dashboard web con Streamlit
├── verificar_datos.py      # Utilidad para consultar los últimos registros en BD
├── yolov8n.pt              # Modelo YOLOv8 nano preentrenado
├── requirements.txt        # Dependencias del proyecto
└── README.md
```

## Solución de problemas

| Error | Solución |
|---|---|
| `Error al conectar con la BD` | Comprueba que PostgreSQL está activo y que la contraseña en `DB_CONFIG` es correcta |
| `No se pudo acceder a la cámara` | Cambia `CAMERA_INDEX = 0` a `1` o `2` en `fase1_deteccion.py` |
| `No hay datos en la base de datos` | Es normal al inicio — espera al primer guardado (60 segundos) |
| Error al instalar `torch` | Verifica que tienes Python 3.9–3.11 y pip actualizado (`pip install --upgrade pip`) |
| El dashboard no abre el navegador | Abre manualmente `http://localhost:8501` |

## Verificar datos en la BD

Para comprobar los últimos registros guardados sin abrir el dashboard:

```bash
python verificar_datos.py
```

## Tecnologías utilizadas

- [YOLOv8 (Ultralytics)](https://github.com/ultralytics/ultralytics) — Detección de personas
- [OpenCV](https://opencv.org/) — Captura y procesamiento de video
- [PyTorch](https://pytorch.org/) — Backend de inferencia (CPU/GPU)
- [PostgreSQL](https://www.postgresql.org/) — Base de datos
- [Streamlit](https://streamlit.io/) — Dashboard web
- [Plotly](https://plotly.com/) — Gráficas interactivas
