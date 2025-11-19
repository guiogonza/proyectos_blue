'''Esquema/DTO Proyectos (placeholder)'''
# domain/schemas/proyectos.py
from typing import Optional
from pydantic import BaseModel, Field, validator
from datetime import date

ESTADOS_PROY = ["Borrador", "Activo", "En pausa", "Cerrado"]

class ProyectoCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=200)
    cliente: Optional[str] = Field(default=None, max_length=200)
    pm_id: Optional[int] = None
    fecha_inicio: date
    fecha_fin_planeada: date
    estado: str = "Borrador"
    costo_estimado_total: float = Field(ge=0)
    descripcion: Optional[str] = None  # opcional, si la quieres

    @validator("estado")
    def _estado(cls, v):
        if v not in ESTADOS_PROY: raise ValueError(f"Estado inválido: {v}")
        return v

    @validator("fecha_fin_planeada")
    def _fechas(cls, v, values):
        fi = values.get("fecha_inicio")
        if fi and v < fi: raise ValueError("La fecha fin planeada no puede ser anterior a inicio.")
        return v

class ProyectoUpdate(ProyectoCreate):
    id: int

class ProyectoClose(BaseModel):
    id: int
    costo_real_total: float = Field(ge=0)

class ProyectoListItem(BaseModel):
    id: int
    nombre: str
    cliente: Optional[str]
    pm_id: Optional[int]
    fecha_inicio: date
    fecha_fin_planeada: date
    estado: str
    costo_estimado_total: float
    costo_real_total: Optional[float]
