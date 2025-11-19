'''Esquema/DTO Asignaciones (placeholder)'''
# domain/schemas/asignaciones.py
from typing import Optional
from pydantic import BaseModel, Field, validator
from datetime import date

class AsignacionCreate(BaseModel):
    persona_id: int
    proyecto_id: int
    sprint_id: Optional[int] = None
    dedicacion_pct: float = Field(gt=0, le=100)
    fecha_asignacion: date
    fecha_fin: Optional[date] = None

    @validator("fecha_fin")
    def _fin_no_antes_de_inicio(cls, v, values):
        fi = values.get("fecha_asignacion")
        if v and fi and v < fi:
            raise ValueError("La fecha fin no puede ser anterior a la fecha de asignación.")
        return v

class AsignacionUpdate(AsignacionCreate):
    id: int

class AsignacionEnd(BaseModel):
    id: int
    fecha_fin: date

class AsignacionListItem(BaseModel):
    id: int
    persona_id: int
    proyecto_id: int
    sprint_id: Optional[int]
    dedicacion_pct: float
    fecha_asignacion: date
    fecha_fin: Optional[date]
    persona_nombre: str
    proyecto_nombre: str
    sprint_nombre: Optional[str]
