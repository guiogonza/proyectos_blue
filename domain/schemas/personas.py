'''Esquema/DTO Personas (placeholder)'''
# domain/schemas/personas.py
from typing import Optional
from pydantic import BaseModel, Field, validator

ROLES_PERMITIDOS = ["PM", "Desarrollador", "Analista", "QA", "DevOps", "Data", "Soporte"]

class PersonaCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=200)
    rol: str
    tarifa_interna: Optional[float] = Field(default=None, ge=0)
    cedula: Optional[str] = Field(default=None, max_length=20)
    numero_contacto: Optional[str] = Field(default=None, max_length=15)
    correo: Optional[str] = Field(default=None, max_length=100)

    @validator("rol")
    def validar_rol(cls, v):
        if v not in ROLES_PERMITIDOS:
            raise ValueError(f"Rol inválido. Usa uno de: {', '.join(ROLES_PERMITIDOS)}")
        return v
    
    @validator("correo")
    def validar_correo(cls, v):
        if v and v.strip():
            # Validación básica de email
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, v.strip()):
                raise ValueError("Formato de correo electrónico inválido")
        return v.strip() if v else None

class PersonaUpdate(PersonaCreate):
    id: int
    activo: bool = True

class PersonaListItem(BaseModel):
    id: int
    nombre: str
    rol: str
    tarifa_interna: Optional[float]
    activo: bool
    cedula: Optional[str]
    numero_contacto: Optional[str]
    correo: Optional[str]
