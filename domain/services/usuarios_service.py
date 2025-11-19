# domain/services/usuarios_service.py
import bcrypt
from typing import List, Dict, Any
from domain.schemas.usuarios import UsuarioCreate, UsuarioUpdate, UsuarioListItem
from infra.repositories import usuarios_repo

def _hash(p: str) -> str:
    return bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()

def crear(dto: UsuarioCreate) -> int:
    if usuarios_repo.get_by_email(dto.email):
        raise ValueError("Ya existe un usuario con ese email.")
    return usuarios_repo.create_user(dto.email, _hash(dto.password_plain), dto.rol_app, dto.persona_id, True)

def actualizar(dto: UsuarioUpdate) -> None:
    current = usuarios_repo.get_by_id(dto.id)
    if not current:
        raise ValueError("Usuario no existe.")
    # si cambia email, validar que no exista duplicado
    if dto.email != current["email"]:
        if usuarios_repo.get_by_email(dto.email):
            raise ValueError("Ya existe otro usuario con ese email.")
    usuarios_repo.update_user(dto.id, dto.email, dto.rol_app, dto.persona_id, dto.activo)

def reset_password(user_id: int, new_plain: str) -> None:
    if not usuarios_repo.get_by_id(user_id):
        raise ValueError("Usuario no existe.")
    usuarios_repo.update_password(user_id, _hash(new_plain))

def listar() -> List[UsuarioListItem]:
    rows = usuarios_repo.list_users()
    return [UsuarioListItem(
        id=r["id"], email=r["email"], rol_app=r["rol_app"],
        persona_id=r.get("persona_id"), activo=bool(r["activo"])
    ) for r in rows]

def eliminar(user_id: int) -> None:
    usuario = usuarios_repo.get_by_id(user_id)
    if not usuario:
        raise ValueError("Usuario no encontrado.")
    usuarios_repo.delete_user(user_id)
