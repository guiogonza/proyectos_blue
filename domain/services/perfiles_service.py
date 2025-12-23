'''Reglas de negocio Perfiles'''
# domain/services/perfiles_service.py
from typing import Optional, List
from domain.schemas.perfiles import PerfilCreate, PerfilUpdate, PerfilListItem
from infra.repositories import perfiles_repo

def crear(dto: PerfilCreate) -> int:
    """Crea un nuevo perfil"""
    # Validar que no exista el nombre
    if perfiles_repo.exists_nombre(dto.nombre):
        raise ValueError(f"Ya existe un perfil con el nombre '{dto.nombre}'")
    
    return perfiles_repo.create_perfil(dto.nombre)

def actualizar(dto: PerfilUpdate) -> None:
    """Actualiza un perfil existente"""
    # Validar que no exista otro perfil con el mismo nombre
    if perfiles_repo.exists_nombre(dto.nombre, exclude_id=dto.id):
        raise ValueError(f"Ya existe otro perfil con el nombre '{dto.nombre}'")
    
    perfiles_repo.update_perfil(dto.id, dto.nombre, dto.activo)

def eliminar(perfil_id: int) -> None:
    """Elimina un perfil"""
    perfiles_repo.delete_perfil(perfil_id)

def listar(solo_activos: Optional[bool] = None, search: Optional[str] = None) -> List[PerfilListItem]:
    """Lista perfiles con filtros"""
    rows = perfiles_repo.list_perfiles(solo_activos, search)
    return [PerfilListItem(**r) for r in rows]

def obtener(perfil_id: int) -> Optional[PerfilListItem]:
    """Obtiene un perfil por ID"""
    row = perfiles_repo.get_perfil(perfil_id)
    return PerfilListItem(**row) if row else None

def cambiar_estado(perfil_id: int, activo: bool) -> None:
    """Activa o desactiva un perfil"""
    perfiles_repo.set_activo(perfil_id, activo)
