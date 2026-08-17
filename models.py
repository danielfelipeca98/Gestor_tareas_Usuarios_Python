from pydantic import BaseModel,Field
from typing import Optional



class TareaCreate(BaseModel):
    titulo: str = Field(...,min_length = 3, max_length = 100, description = "Titulo de la tarrea")
    descripcion: str = Field(..., min_length=1, max_length=500)
    estado: str = Field(default="pendiente", pattern=r"^(pendiente|en progreso|completada|cancelada)$")
    usuario_id: int
    
class TareaUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=3, max_length=100)
    descripcion: Optional[str] = Field(None, min_length=1, max_length=500)
    estado: Optional[str] = Field(None, pattern=r"^(pendiente|en progreso|completada|cancelada)$")

class TareaResponse(BaseModel):
    id: int
    titulo: str
    descripcion: str
    estado: str
    usuario_id:int

