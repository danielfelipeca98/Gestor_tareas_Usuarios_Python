import sqlite3
import os

# ===== RUTA CORRECTA (SIEMPRE FUNCIONA) =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database_tarea.db")

conexion = sqlite3.connect(DB_PATH)
cursor = conexion.cursor()

# usuarios
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
)
""")

# tareas
cursor.execute("""
CREATE TABLE IF NOT EXISTS tareas(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    estado TEXT DEFAULT 'pendiente',
    usuarios_id INTEGER,
    FOREIGN KEY (usuarios_id) REFERENCES usuarios(id)
)
""")

conexion.commit()
conexion.close()
print("Base de datos creada en:", DB_PATH)

def get_db():
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    try:
        yield conexion, cursor
    finally:
        conexion.close()