from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from configAuth import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from database import get_db  # ← Usa get_db() para obtener la conexión
import sqlite3

security = HTTPBearer()

def crear_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verificar_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verificar_token(token)
    
    usuario_id = payload.get("sub")
    nombre = payload.get("nombre")
    
    if not usuario_id:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    # ✅ Usar get_db() para obtener la conexión a la base de datos
    # que conftest.py ha configurado correctamente
    conexion, cursor = get_db()
    cursor.execute("SELECT id, nombre FROM usuarios WHERE id = ?", (int(usuario_id),))
    usuario = cursor.fetchone()
    conexion.close()
    
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    
    return {"id": usuario[0], "nombre": usuario[1]}