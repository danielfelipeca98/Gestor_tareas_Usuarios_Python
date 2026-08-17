from pydantic import BaseModel,Field
from typing import Optional

class UsuarioRegister(BaseModel):
    nombre:str = Field(...,min_length=3 , max_length=300, description="nombre Usuario")
    email : str = Field(...,pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$")
    password: str = Field(..., min_length=8, pattern=r"^[a-zA-Z0-9!@#$%^&*]+$")

class UsuarioLogin(BaseModel):
    email : str = Field(...,pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$")
    password: str = Field(..., min_length=8, pattern=r"^[a-zA-Z0-9!@#$%^&*]+$")

class UsuarioResponse(BaseModel):
    id:int
    nombre:str = Field(...,min_length=3 , max_length=300, description="nombre Usuario")
    email : str = Field(...,pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$")
    
class TokenResponse(BaseModel):
    access_token: str
    token_type: str 
