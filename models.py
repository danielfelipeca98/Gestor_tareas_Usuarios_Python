from pydantic import BaseModel,Field
from typing import Optional



class TareaCreate(BaseModel):
    """Modelo para crear una nueva tarea"""
    titulo: str = Field(...,min_length = 3, max_length = 100, description = "Titulo de la tarrea",example="Estudiar FastApi")
    descripcion: str = Field(..., min_length=1, max_length=500,description="Descripción detallada de la tarea",example="Aprender a documentar APIs con FastAPI")
    estado: str = Field(default="pendiente", pattern=r"^(pendiente|en progreso|completada|cancelada)$",description="Estado de la tarea",example="pendiente")
    
class TareaUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=3, max_length=100,description="Nuevo título de la tarea (opcional)",example="Estudiar FastAPI avanzado")
    descripcion: Optional[str] = Field(None, min_length=1, max_length=500,description="Nueva descripción de la tarea (opcional)",example="Aprender a documentar APIs y desplegar en producción")
    estado: Optional[str] = Field(None, pattern=r"^(pendiente|en progreso|completada|cancelada)$",description="Nuevo estado de la tarea (opcional)",example="completada")

class TareaResponse(BaseModel):
    """Modelo de respuesra para una tarea"""
    id: int = Field(..., description="ID único de la tarea", example=1)
    titulo: str = Field(..., description="Título de la tarea",example="Estudiar FastAPI")
    descripcion: str = Field(..., description="Descripción de la tarea", example="Aprender a documentar APIs con FastAPI")
    estado: str = Field(..., description="Estado actual de la tarea", example="pendiente")

