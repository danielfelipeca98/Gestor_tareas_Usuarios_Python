import pytest
from fastapi.testclient import TestClient
from main import app

test_user = {
    "nombre": "UsuarioIntegracion",
    "email": "integracion@email.com",
    "password": "Password123"
}

def test_flujo_completo_usuario(client):
    """Prueba el flujo completo: registrar → login → crear tarea → listar → actualizar → eliminar"""
    
    register = client.post("/register", json=test_user)
    assert register.status_code == 201
    
    login = client.post("/login", json={
        "email": test_user["email"],
        "password": test_user["password"]
    })
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    crear = client.post(
        "/tareas",
        json={"titulo": "Tarea integración", "descripcion": "Test completo"},
        headers=headers
    )
    assert crear.status_code == 201
    tarea_id = crear.json()["id"]
    
    listar = client.get("/tareas", headers=headers)
    assert listar.status_code == 200
    assert len(listar.json()) > 0
    
    actualizar = client.put(
        f"/tareas/{tarea_id}",
        json={"estado": "completada"},
        headers=headers
    )
    assert actualizar.status_code == 200
    assert actualizar.json()["estado"] == "completada"
    
    eliminar = client.delete(f"/tareas/{tarea_id}", headers=headers)
    assert eliminar.status_code == 200

def test_usuario_solo_ve_sus_tareas(client):
    """Prueba que un usuario solo vea sus propias tareas"""
    
    user1 = {
        "nombre": "User1",
        "email": "user1@email.com",
        "password": "Password123"
    }
    client.post("/register", json=user1)
    login1 = client.post("/login", json={
        "email": user1["email"],
        "password": user1["password"]
    })
    token1 = login1.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}
    
    client.post(
        "/tareas",
        json={"titulo": "Tarea de User1", "descripcion": "Test"},
        headers=headers1
    )
    
    user2 = {
        "nombre": "User2",
        "email": "user2@email.com",
        "password": "Password123"
    }
    client.post("/register", json=user2)
    login2 = client.post("/login", json={
        "email": user2["email"],
        "password": user2["password"]
    })
    token2 = login2.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}
    
    listar2 = client.get("/tareas", headers=headers2)
    assert listar2.status_code == 200
    
    tareas = listar2.json()
    for tarea in tareas:
        assert tarea["titulo"] != "Tarea de User1"