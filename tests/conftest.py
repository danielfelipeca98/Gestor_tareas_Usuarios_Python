import pytest
from fastapi.testclient import TestClient
from main import app
import sqlite3
import os

@pytest.fixture(scope="function")
def client():
    # Usar base de datos en memoria
    test_db = ":memory:"
    
    # Establecer variable de entorno ANTES de importar main
    os.environ["TEST_DB_PATH"] = test_db
    
    # Forzar recarga de módulos para que usen la nueva variable
    import importlib
    import database
    import auth
    import main
    importlib.reload(database)
    importlib.reload(auth)
    importlib.reload(main)
    
    # Crear tablas
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tareas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            estado TEXT DEFAULT 'pendiente',
            usuarios_id INTEGER,
            FOREIGN KEY (usuarios_id) REFERENCES usuarios(id)
        )
    """)
    conn.commit()
    conn.close()
    
    yield TestClient(app)
    
    # Limpiar variable de entorno
    if "TEST_DB_PATH" in os.environ:
        del os.environ["TEST_DB_PATH"]