import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database_tarea.db")

def get_db():
    """
    Establece una conexión con la base de datos SQLite.

    Yields:
        tuple: (conexion, cursor) para ejecutar consultas

    Ejemplo:
        conexion, cursor = get_db()
        cursor.execute("SELECT * FROM tareas")
        filas = cursor.fetchall()
        conexion.close()
    """
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    try:
        yield conexion, cursor
    finally:
        conexion.close()