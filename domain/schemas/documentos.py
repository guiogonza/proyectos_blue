# domain/schemas/documentos.py
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class DocumentoCreate(BaseModel):
    proyecto_id: int
    nombre_archivo: str = Field(min_length=1, max_length=255)
    descripcion: Optional[str] = None
    ruta_archivo: str = Field(min_length=1, max_length=500)
    tamanio_bytes: Optional[int] = Field(default=None, ge=0)
    tipo_mime: Optional[str] = Field(default=None, max_length=100)

class DocumentoUpdate(BaseModel):
    id: int
    nombre_archivo: str = Field(min_length=1, max_length=255)
    descripcion: Optional[str] = None

class DocumentoListItem(BaseModel):
    id: int
    proyecto_id: int
    proyecto_nombre: Optional[str] = None
    nombre_archivo: str
    descripcion: Optional[str]
    ruta_archivo: str
    tamanio_bytes: Optional[int]
    tipo_mime: Optional[str]
    fecha_carga: datetime
