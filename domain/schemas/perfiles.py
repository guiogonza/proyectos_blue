'''Esquema/DTO Perfiles'''
# domain/schemas/perfiles.py
from typing import Optional
from datetime import date
from pydantic import BaseModel, Field

class PerfilCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=200)
    tarifa_sin_iva: float = Field(..., gt=0, description="Tarifa sin IVA (valor monetario)")
    vigencia: date = Field(..., description="Fecha de vigencia del perfil")

class PerfilUpdate(PerfilCreate):
    id: int
    activo: bool = True

class PerfilListItem(BaseModel):
    id: int
    nombre: str
    tarifa_sin_iva: Optional[float] = None
    vigencia: Optional[date] = None
    activo: bool
