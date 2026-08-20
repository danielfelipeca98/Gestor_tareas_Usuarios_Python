from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from configAuth import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
import sqlite3
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database_tarea.db")

security = HTTPBearer()

def crear_token(data: dict) -> str:
    """
    Genera un token JWT a partir de los datos proporcionados.

    Args:
        data (dict): Datos a codificar en el token (ej: {"sub": "1", "nombre": "Ana"})

    Returns:
        str: Token JWT firmado con expiración
    """
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verificar_token(token: str) -> dict:
    """
    Decodifica y verifica un token JWT.

    Args:
        token (str): Token JWT a verificar

    Returns:
        dict: Payload del token si es válido

    Raises:
        HTTPException: Si el token es inválido o expirado
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Obtiene el usuario autenticado a partir del token JWT.

    Args:
        credentials (HTTPAuthorizationCredentials): Credenciales del token

    Returns:
        dict: Información del usuario autenticado (id, nombre)

    Raises:
        HTTPException: Si el token es inválido o el usuario no existe
    """
    token = credentials.credentials
    payload = verificar_token(token)
    
    usuario_id = payload.get("sub")
    nombre = payload.get("nombre")
    
    if not usuario_id:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre FROM usuarios WHERE id = ?", (int(usuario_id),))
    usuario = cursor.fetchone()
    conexion.close()
    
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    
    return {"id": usuario[0], "nombre": usuario[1]}