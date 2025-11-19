'''Reglas de negocio Sprints (placeholder)'''
from typing import Optional, List
from domain.schemas.sprints import SprintCreate, SprintUpdate, SprintClose, SprintListItem
from infra.repositories import sprints_repo, proyectos_repo

def crear(dto: SprintCreate) -> int:
    pr = proyectos_repo.get_proyecto(dto.proyecto_id)
    if not pr: raise ValueError("Proyecto no existe.")
    if pr["estado"] == "Cerrado": raise ValueError("No puedes crear sprints en un proyecto cerrado.")
    return sprints_repo.create_sprint(dto.dict())

def actualizar(dto: SprintUpdate) -> None:
    pr = proyectos_repo.get_proyecto(dto.proyecto_id)
    if not pr: raise ValueError("Proyecto no existe.")
    sprints_repo.update_sprint(dto.id, dto.dict(exclude={"id"}))

def cerrar(dto: SprintClose) -> None:
    sprints_repo.close_sprint(dto.id, dto.costo_real)

def listar(proyecto_id: Optional[int] = None, estado: Optional[str] = None, search: Optional[str] = None) -> List[SprintListItem]:
    rows = sprints_repo.list_sprints(proyecto_id, estado, search)
    return [SprintListItem(**r) for r in rows]

def eliminar(sprint_id: int) -> None:
    sprint = sprints_repo.get_sprint(sprint_id)
    if not sprint:
        raise ValueError("Sprint no encontrado.")
    sprints_repo.delete_sprint(sprint_id)
