'''Esquema/DTO Personas (placeholder)'''
# domain/schemas/personas.py
from typing import Optional
from datetime import date
from pydantic import BaseModel, Field, validator

_ROLES_FALLBACK = [
    "Technician I",
    "Technician II",
    "Experienced Technician I",
    "Experienced Technician II",
    "Technician specialist",
    "Technician architect",
]

def get_roles_permitidos():
    """Carga roles activos desde BD. Si falla, usa fallback hardcodeado."""
    try:
        from infra.repositories import roles_repo
        roles = roles_repo.list_active_role_names()
        return roles if roles else _ROLES_FALLBACK
    except Exception:
        return _ROLES_FALLBACK

# Para compatibilidad con imports existentes
ROLES_PERMITIDOS = _ROLES_FALLBACK
SENIORITY_PERMITIDOS = ["Junior", "Semi-Senior", "Senior", "Lead", "Principal"]
TIPOS_DOCUMENTO_PERMITIDOS = ["Cédula", "Pasaporte", "DNI", "Código Bluetab", "Otro"]
PAISES_PERMITIDOS = ["Argentina", "Colombia", "España", "México", "Perú", "Uruguay"]

class PersonaCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=200)
    ROL_PRINCIPAL: str
    COSTO_RECURSO: Optional[float] = Field(default=None, ge=0)
    NUMERO_DOCUMENTO: str = Field(min_length=1, max_length=50)
    numero_contacto: Optional[str] = Field(default=None, max_length=15)
    correo: Optional[str] = Field(default=None, max_length=100)
    PAIS: str = Field(min_length=1, max_length=100)
    SENIORITY: Optional[str] = None
    LIDER_DIRECTO: Optional[int] = None
    TIPO_DOCUMENTO: str
    vigencia: date

    @validator("ROL_PRINCIPAL")
    def validar_rol(cls, v):
        roles = get_roles_permitidos()
        if v not in roles:
            raise ValueError(f"Rol inválido. Usa uno de: {', '.join(roles)}")
        return v
    
    @validator("SENIORITY")
    def validar_seniority(cls, v):
        if v and v not in SENIORITY_PERMITIDOS:
            raise ValueError(f"Seniority inválido. Usa uno de: {', '.join(SENIORITY_PERMITIDOS)}")
        return v
    
    @validator("TIPO_DOCUMENTO")
    def validar_tipo_documento(cls, v):
        if not v or v not in TIPOS_DOCUMENTO_PERMITIDOS:
            raise ValueError(f"Tipo de documento es obligatorio. Usa uno de: {', '.join(TIPOS_DOCUMENTO_PERMITIDOS)}")
        return v
    
    @validator("PAIS")
    def validar_pais(cls, v):
        if not v or v not in PAISES_PERMITIDOS:
            raise ValueError(f"País es obligatorio. Usa uno de: {', '.join(PAISES_PERMITIDOS)}")
        return v
    
    @validator("NUMERO_DOCUMENTO")
    def validar_numero_documento(cls, v):
        if not v or not v.strip():
            raise ValueError("Número de documento es obligatorio")
        return v.strip()
    
    @validator("vigencia")
    def validar_vigencia(cls, v):
        if not v:
            raise ValueError("Vigencia es obligatoria")
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
    ROL_PRINCIPAL: str
    COSTO_RECURSO: Optional[float]
    activo: bool
    NUMERO_DOCUMENTO: str
    numero_contacto: Optional[str]
    correo: Optional[str]
    PAIS: str
    SENIORITY: Optional[str]
    LIDER_DIRECTO: Optional[int]
    LIDER_NOMBRE: Optional[str] = None  # Para mostrar el nombre del líder
    TIPO_DOCUMENTO: str
    vigencia: date
