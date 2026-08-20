import sqlite3
import os

# ===== RUTA CORRECTA (SIEMPRE FUNCIONA) =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("TEST_DB_PATH", os.path.join(BASE_DIR, "database_tarea.db"))


def get_db():
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    return conexion,cursor