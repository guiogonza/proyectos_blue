# domain/schemas/sap.py
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class SapReportItem(BaseModel):
    id: int
    nro: Optional[int] = None
    id_empleado_sap: Optional[str] = None
    colaborador: str
    id_sap: str
    proyecto_sap: str
    horas_mes: float = 0
    mes: str
    anio: int = 2026
    tipo_novedad: Optional[str] = None
    tiempo_novedad_hrs: Optional[float] = None
    reporte_sap: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class SapReportCreate(BaseModel):
    nro: Optional[int] = None
    id_empleado_sap: Optional[str] = None
    colaborador: str = Field(min_length=1, max_length=200)
    id_sap: str = Field(min_length=1, max_length=50)
    proyecto_sap: str = Field(min_length=1, max_length=300)
    horas_mes: float = Field(ge=0)
    mes: str = Field(min_length=1, max_length=20)
    anio: int = Field(default=2026, ge=2020, le=2100)
    tipo_novedad: Optional[str] = None
    tiempo_novedad_hrs: Optional[float] = Field(default=None, ge=0)
    reporte_sap: bool = True
