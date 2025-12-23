'''Esquema/DTO Perfiles'''
# domain/schemas/perfiles.py
from typing import Optional
from pydantic import BaseModel, Field

class PerfilCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=200)

class PerfilUpdate(PerfilCreate):
    id: int
    activo: bool = True

class PerfilListItem(BaseModel):
    id: int
    nombre: str
    activo: bool
