import threading
import cv2
from ultralytics import YOLO
import sys
import torch
import psycopg2
from datetime import datetime
import time
import os

# Configuración
print("Programa Funcionando")

CAMERA_INDEX = 0  # 0 para webcam integrada, 1 para externa
CONFIDENCE_THRESHOLD = 0.5 # Solo mostrar detecciones con >50% de probabilidad
SEND_INTERVAL = 10  # Segundos (para pruebas rápidas)

# --- CONFIGURACIÓN BASE DE DATOS (¡EDITAR ESTO!) ---
DB_CONFIG = {
    "host": "localhost",
    "database": "monitor_aula",
    "user": "postgres",
    "password": "password123!",
    "port": "5432"
}

def init_db():
    """Inicializa la tabla en la base de datos si no existe."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        # Modificamos la tabla para usar BYTEA para los datos de la imagen en lugar de una ruta de texto
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ocupacion_aula (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                cantidad_personas INTEGER,
                foto_data BYTEA
            );
        """)
        # Comprobar si la columna 'foto_path' existe y eliminarla si es necesario
        cur.execute("""
            DO $$
            BEGIN
                IF EXISTS(SELECT 1 FROM information_schema.columns WHERE table_name='ocupacion_aula' AND column_name='foto_path') THEN
                    ALTER TABLE ocupacion_aula DROP COLUMN foto_path;
                END IF;
            END $$;
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("Base de datos verificada/inicializada correctamente.")
    except Exception as e:
        print(f"Error al conectar con la base de datos: {e}")

def save_to_db(count, frame):
    """Guarda el conteo y los bytes de la imagen directamente en la BD."""
    try:
        # 1. Codificar la imagen a formato JPG en memoria
        success, encoded_image = cv2.imencode('.jpg', frame)
        if not success:
            print("\n[Error] No se pudo codificar la imagen a JPG.")
            return
        
        image_bytes = encoded_image.tobytes()

        # 2. Guardar registro y bytes de la imagen en BD
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        query = "INSERT INTO ocupacion_aula (cantidad_personas, timestamp, foto_data) VALUES (%s, %s, %s)"
        # psycopg2 convierte automáticamente el objeto 'bytes' de Python a BYTEA de PostgreSQL
        cur.execute(query, (count, datetime.now(), image_bytes))
        conn.commit()
        cur.close()
        conn.close()
        print(f"\n[BD] Guardado registro: {count} personas y la imagen en la base de datos.")
    except Exception as e:
        print(f"\n[Error BD] No se pudo guardar el dato: {e}")

def main():
    # Selección de dispositivo (GPU si está disponible, si no CPU)
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Cargando modelo en: {device.upper()}")
    if device == 'cuda':
        print(f"CUDA está disponible. Usando GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("CUDA no está disponible. Usando CPU.")

    # Intentar inicializar la BD al arranque
    init_db()

    # Cargamos el modelo YOLOv8 nano
    try:
        model = YOLO('yolov8n.pt')
        model.to(device)
    except Exception as e:
        print(f"Error al cargar el modelo: {e}")
        return

    # Inicializamos la captura de video
    cap = cv2.VideoCapture(CAMERA_INDEX)

    # --- OPTIMIZACIÓN: Establecer una resolución más baja ---
    # Forzamos la captura a 1280x720 para reducir la carga de la CPU/GPU.
    # Esto previene "congelamientos" al procesar video de alta resolución por defecto.
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    # ----------------------------------------------------

    if not cap.isOpened():
        print(f"Error: No se pudo acceder a la cámara con índice {CAMERA_INDEX}.")
        print("Prueba cambiando 'CAMERA_INDEX' a 0, 1 o 2 en el script.")
        return

    # Configuración de ventana
    window_name = "Monitorizacion de Aula - Deteccion en Tiempo Real"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 800, 600) # Tamaño inicial razonable

    print(f"Iniciando detección... Presiona 'q' en la ventana de video para salir.")

    last_sent_time = 0 # Forzar captura inmediata al arrancar

    while True:
        ret, frame = cap.read()
        if not ret:
            print("No se pudo recibir fotograma (fin del stream o error).")
            break

        # Detección
        # stream=True hace que use un generador, más eficiente para video
        results = model(frame, conf=CONFIDENCE_THRESHOLD, classes=[0], verbose=False, stream=True, device=device)

        # Procesamos los resultados (como stream=True, iteramos)
        for result in results:
            num_personas = len(result.boxes)
            
            # Dibujamos las cajas en la imagen
            annotated_frame = result.plot()

            # Texto en pantalla
            text = f"Ocupacion: {num_personas}"
            color = (0, 255, 0) if num_personas < 5 else (0, 0, 255) # Verde si hay pocos, rojo si hay muchos
            
            cv2.putText(annotated_frame, text, (20, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

            # --- LOGICA DE ENVIO A BASE DE DATOS ---
            current_time = time.time()
            if current_time - last_sent_time >= SEND_INTERVAL:
                # Ejecutar la operación de guardado en un hilo separado para no bloquear el bucle principal
                save_thread = threading.Thread(target=save_to_db, args=(num_personas, annotated_frame.copy()))
                save_thread.daemon = True # Permite que el programa se cierre aunque el hilo esté activo
                save_thread.start()
                last_sent_time = current_time
            # ---------------------------------------

            # Imprimir en consola (sobrescribiendo la línea para no llenar el log)
            sys.stdout.write(f"\r[En vivo] {text}     ")
            sys.stdout.flush()

            # Mostrar video
            cv2.imshow(window_name, annotated_frame)

        # Salir con 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    print("\nDeteniendo sistema...")
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()