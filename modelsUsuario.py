from pydantic import BaseModel,Field,validator
from typing import Optional

class UsuarioRegister(BaseModel):
    "modelo para registrar un nuevo usuario"
    nombre:str = Field(...,min_length=3 , max_length=300, description="nombre Usuario",example="Ana Pérez")
    email : str = Field(...,pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$",description="Email del usuario (formato válido)",example="ana@email.com")
    password: str = Field(..., min_length=8,description="Contraseña (mínimo 8 caracteres)",example="Password123")

@validator("password")
def validar_password(cls, v):
    """Valida que la contraseña tenga mayúscula, minúscula y número"""
    if not any(c.islower() for c in v):
        raise ValueError("La contraseña debe tener al menos una minúscula")
    if not any(c.isupper() for c in v):
        raise ValueError("La contraseña debe tener al menos una mayúscula")
    if not any(c.isdigit() for c in v):
        raise ValueError("La contraseña debe tener al menos un número")
    return v

class UsuarioLogin(BaseModel):
    "Modelo para iniciar sesion"
    email : str = Field(...,pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$",description="Email del usuario",example="ana@email.com")
    password: str = Field(..., min_length=8, pattern=r"^[a-zA-Z0-9!@#$%^&*]+$",description="Contraseña del usuario",example="Password123")

class UsuarioResponse(BaseModel):
    """Modelo de respuesta para datos de usuario"""
    
    id: int = Field(..., description="ID único del usuario", example=1)
    nombre: str = Field(...,description="Nombre del usuario", example="Ana Pérez")
    email: str = Field(..., description="Email del usuario", example="ana@email.com")


class TokenResponse(BaseModel):
    """Modelo de respuesta para el token JWT"""
    
    access_token: str = Field(..., description="Token JWT para autenticación", example="eyJhbGciOiJIUzI1NiIs...")
    token_type: str = Field( default="bearer", description="Tipo de token", example="bearer")