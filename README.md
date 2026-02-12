# Proyecto Intermodular - Grupo 1: Sistema de Detección y Análisis IA

Este proyecto implementa un sistema de detección y análisis basado en inteligencia artificial, utilizando el modelo YOLOv8 para la detección de objetos y un dashboard interactivo para la visualización de datos.

## Estructura del Proyecto

- `fase1_deteccion.py`: Script principal para la detección de objetos en tiempo real o a partir de fuentes de video/imagen usando YOLOv8.
- `fase2_dashboard.py`: Aplicación Streamlit para visualizar y analizar los resultados de la detección.
- `verificar_datos.py`: Script para la verificación y preprocesamiento de datos (posiblemente para el entrenamiento o la validación del modelo).
- `yolov8n.pt`: El modelo YOLOv8 nano pre-entrenado utilizado para la detección.
- `requirements.txt`: Lista de dependencias de Python necesarias para ejecutar el proyecto.
- `capturas/`: Directorio para almacenar imágenes o videos capturados durante el proceso de detección.

## Instalación

Para configurar el entorno de desarrollo y ejecutar el proyecto, sigue los siguientes pasos:

1.  **Clonar el repositorio:**
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd ProyectoIntermodular-Grupo1
    ```

2.  **Crear y activar un entorno virtual (recomendado):**
    ```bash
    python -m venv venv
    # En Windows
    .\venv\Scripts\activate
    # En macOS/Linux
    source venv/bin/activate
    ```

3.  **Instalar las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

## Uso

### Fase 1: Detección con IA

Para iniciar el sistema de detección, ejecuta el siguiente script:

```bash
python fase1_deteccion.py
```

Este script activará la cámara (si está configurada) o procesará la fuente de entrada especificada, mostrando las detecciones en tiempo real.

### Fase 2: Dashboard de Análisis

Una vez que tengas datos de detección, puedes iniciar el dashboard para visualizarlos:

```bash
streamlit run fase2_dashboard.py
```

Esto abrirá una aplicación web interactiva en tu navegador donde podrás explorar los resultados de la detección.

## Contribución

¡Las contribuciones son bienvenidas! Si deseas mejorar este proyecto, por favor, haz un fork del repositorio y envía tus pull requests.

## Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.
