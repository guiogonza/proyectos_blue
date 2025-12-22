'''Esquema/DTO Proyectos (placeholder)'''
# domain/schemas/proyectos.py
from typing import Optional
from pydantic import BaseModel, Field, validator
from datetime import date

ESTADOS_PROY = ["Borrador", "Activo", "En pausa", "Cerrado"]

class ProyectoCreate(BaseModel):
    NOMBRE: str = Field(min_length=2, max_length=200)
    cliente: Optional[str] = Field(default=None, max_length=200)
    pm_id: Optional[int] = None
    FECHA_INICIO: date
    FECHA_FIN_ESTIMADA: date
    ESTADO: str = "Borrador"
    BUDGET: float = Field(ge=0)
    descripcion: Optional[str] = None
    PAIS: Optional[str] = Field(default=None, max_length=100)
    CATEGORIA: Optional[str] = Field(default=None, max_length=100)
    LIDER_BLUETAB: Optional[str] = Field(default=None, max_length=200)
    LIDER_CLIENTE: Optional[str] = Field(default=None, max_length=200)
    FECHA_FIN: Optional[date] = None
    MANAGER_BLUETAB: Optional[str] = Field(default=None, max_length=200)

    @validator("ESTADO")
    def _estado(cls, v):
        if v not in ESTADOS_PROY: raise ValueError(f"Estado inválido: {v}")
        return v

    @validator("FECHA_FIN_ESTIMADA")
    def _fechas(cls, v, values):
        fi = values.get("FECHA_INICIO")
        if fi and v < fi: raise ValueError("La fecha fin estimada no puede ser anterior a inicio.")
        return v

class ProyectoUpdate(ProyectoCreate):
    id: int

class ProyectoClose(BaseModel):
    id: int
    COSTO_REAL_TOTAL: float = Field(ge=0)

class ProyectoListItem(BaseModel):
    id: int
    NOMBRE: str
    cliente: Optional[str]
    pm_id: Optional[int]
    lider_nombre: Optional[str] = None
    FECHA_INICIO: date
    FECHA_FIN_ESTIMADA: date
    ESTADO: str
    BUDGET: float
    COSTO_REAL_TOTAL: Optional[float]
    PAIS: Optional[str] = None
    CATEGORIA: Optional[str] = None
    LIDER_BLUETAB: Optional[str] = None
    LIDER_CLIENTE: Optional[str] = None
    FECHA_FIN: Optional[date] = None
    MANAGER_BLUETAB: Optional[str] = None
