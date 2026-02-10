import psycopg2
from tabulate import tabulate # Si no la tienes, usaremos print normal

DB_CONFIG = {
    "host": "localhost",
    "database": "monitor_aula",
    "user": "postgres",
    "password": "password123!",
    "port": "5432"
}

def consultar_datos():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        cur.execute("SELECT id, timestamp, cantidad_personas FROM ocupacion_aula ORDER BY timestamp DESC LIMIT 5;")
        rows = cur.fetchall()
        
        if not rows:
            print("
[!] La tabla está vacía. Espera a que el script principal haga el primer envío (cada 5 min).")
        else:
            print("
--- ÚLTIMOS 5 REGISTROS EN LA BASE DE DATOS ---")
            print(f"{'ID':<5} | {'Fecha y Hora':<20} | {'Personas':<10}")
            print("-" * 40)
            for row in rows:
                print(f"{row[0]:<5} | {str(row[1]):<20} | {row[2]:<10}")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error al conectar: {e}")

if __name__ == "__main__":
    consultar_datos()
