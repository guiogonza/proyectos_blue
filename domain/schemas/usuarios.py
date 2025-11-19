# domain/schemas/usuarios.py
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field

Role = Literal["admin", "viewer"]

class UsuarioCreate(BaseModel):
    email: EmailStr
    rol_app: Role
    persona_id: Optional[int] = None
    password_plain: str = Field(min_length=6, max_length=128)

class UsuarioUpdate(BaseModel):
    id: int
    email: EmailStr
    rol_app: Role
    persona_id: Optional[int] = None
    activo: bool = True

class UsuarioListItem(BaseModel):
    id: int
    email: EmailStr
    rol_app: Role
    persona_id: Optional[int]
    activo: bool
