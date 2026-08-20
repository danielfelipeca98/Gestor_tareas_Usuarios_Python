import pytest
from fastapi.testclient import TestClient
from main import app

test_user = {
    "nombre": "UsuarioTareas",
    "email": "tareas@email.com",
    "password": "Password123"
}

def get_token(client):
    """Obtiene un token JWT para los tests"""
    # Registrar usuario (si falla, la prueba fallará)
    register = client.post("/register", json=test_user)
    if register.status_code != 201:
        # Si falla, intentar solo login (por si ya existe)
        pass
    
    response = client.post("/login", json={
        "email": test_user["email"],
        "password": test_user["password"]
    })
    
    # ✅ VERIFICAR QUE EL LOGIN FUNCIONÓ
    if response.status_code != 200:
        print(f"❌ Login falló: {response.text}")
        raise Exception(f"Login falló con status {response.status_code}")
    
    return response.json()["access_token"]

def get_headers(client):
    token = get_token(client)
    return {"Authorization": f"Bearer {token}"}

def test_crear_tarea(client):
    response = client.post(
        "/tareas",
        json={
            "titulo": "Tarea de prueba",
            "descripcion": "Descripción de la tarea",
            "estado": "pendiente"
        },
        headers=get_headers(client)
    )
    assert response.status_code == 201
    assert response.json()["titulo"] == "Tarea de prueba"
    assert "id" in response.json()

def test_crear_tarea_sin_autenticacion(client):
    response = client.post(
        "/tareas",
        json={
            "titulo": "Tarea sin token",
            "descripcion": "Esto debería fallar"
        }
    )
    assert response.status_code == 401

def test_listar_tareas(client):
    client.post(
        "/tareas",
        json={"titulo": "Tarea 1", "descripcion": "Test"},
        headers=get_headers(client)
    )
    
    response = client.get("/tareas", headers=get_headers(client))
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

def test_obtener_tarea_por_id(client):
    crear = client.post(
        "/tareas",
        json={"titulo": "Tarea para obtener", "descripcion": "Test"},
        headers=get_headers(client)
    )
    tarea_id = crear.json()["id"]
    
    response = client.get(f"/tareas/{tarea_id}", headers=get_headers(client))
    assert response.status_code == 200
    assert response.json()["id"] == tarea_id

def test_actualizar_tarea(client):
    crear = client.post(
        "/tareas",
        json={"titulo": "Tarea a actualizar", "descripcion": "Test"},
        headers=get_headers(client)
    )
    tarea_id = crear.json()["id"]
    
    response = client.put(
        f"/tareas/{tarea_id}",
        json={"estado": "completada"},
        headers=get_headers(client)
    )
    assert response.status_code == 200
    assert response.json()["estado"] == "completada"

def test_eliminar_tarea(client):
    crear = client.post(
        "/tareas",
        json={"titulo": "Tarea a eliminar", "descripcion": "Test"},
        headers=get_headers(client)
    )
    tarea_id = crear.json()["id"]
    
    response = client.delete(f"/tareas/{tarea_id}", headers=get_headers(client))
    assert response.status_code == 200
    assert "eliminada" in response.text

def test_tarea_no_encontrada(client):
    response = client.get("/tareas/9999", headers=get_headers(client))
    assert response.status_code == 404