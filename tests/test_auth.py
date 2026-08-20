import pytest
from fastapi.testclient import TestClient
from main import app

test_user = {
    "nombre": "UsuarioPrueba",
    "email": "prueba@email.com",
    "password": "Password123"
}

def test_register_exitoso(client):
    response = client.post("/register", json=test_user)
    assert response.status_code == 201
    assert response.json()["email"] == test_user["email"]
    assert "id" in response.json()

def test_register_email_duplicado(client):  # ← CORREGIDO (era tesr)
    client.post("/register", json=test_user)
    response = client.post("/register", json=test_user)
    assert response.status_code == 400
    assert "Email ya registrado" in response.text

def test_register_datos_invalidos(client):  # ← AGREGAR client
    usuario_invalido = {
        "nombre": "A",
        "email": "emailinvalido",
        "password": "123"
    }
    response = client.post("/register", json=usuario_invalido)
    assert response.status_code == 422

def test_login_exitoso(client):  # ← AGREGAR client
    client.post("/register", json=test_user)
    response = client.post("/login", json={
        "email": test_user["email"],
        "password": test_user["password"]
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "bearer" in response.json()["token_type"]

def test_login_incorrecto(client):
    client.post("/register", json=test_user)
    response = client.post("/login", json={
        "email": test_user["email"],
        "password": "WrongPassword123"
    })
    assert response.status_code == 401
    assert "Contraseña incorrecta" in response.text

def test_login_usuario_inexistente(client):  # ← AGREGAR client
    response = client.post("/login", json={
        "email": "noexiste@email.com",
        "password": "Password123"
    })
    assert response.status_code == 400
    assert "Usuario no encontrado" in response.text