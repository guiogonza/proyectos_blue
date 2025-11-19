'''Esquema/DTO Sprints (placeholder)'''
from pydantic import BaseModel, Field, validator
from datetime import date
from typing import Optional, Literal

SprintEstado = Literal["Planificado", "En curso", "Cerrado"]

class SprintCreate(BaseModel):
    proyecto_id: int
    nombre: str = Field(min_length=2, max_length=120)
    fecha_inicio: date
    fecha_fin: date
    costo_estimado: float = Field(ge=0)
    estado: SprintEstado = "Planificado"
    actividades: Optional[str] = Field(default=None, max_length=2000)

    @validator("fecha_fin")
    def _rangos(cls, v, values):
        fi = values.get("fecha_inicio")
        if fi and v < fi:
            raise ValueError("La fecha fin no puede ser anterior a la de inicio.")
        return v

class SprintUpdate(SprintCreate):
    id: int

class SprintClose(BaseModel):
    id: int
    costo_real: float = Field(ge=0)

class SprintListItem(BaseModel):
    id: int
    proyecto_id: int
    proyecto_nombre: Optional[str] = None
    nombre: str
    fecha_inicio: date
    fecha_fin: date
    costo_estimado: float
    costo_real: Optional[float]
    estado: SprintEstado
    actividades: Optional[str]
