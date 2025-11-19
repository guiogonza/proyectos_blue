'''Reglas de negocio Proyectos (placeholder)'''
# domain/services/proyectos_service.py
from typing import List, Optional, Dict, Any
from domain.schemas.proyectos import ProyectoCreate, ProyectoUpdate, ProyectoClose, ProyectoListItem, ESTADOS_PROY
from infra.repositories import proyectos_repo, personas_repo

def crear(dto: ProyectoCreate) -> int:
    if proyectos_repo.exists_nombre(dto.nombre):
        raise ValueError("Ya existe un proyecto con ese nombre.")
    return proyectos_repo.create_proyecto(dto.dict())

def actualizar(dto: ProyectoUpdate) -> None:
    if proyectos_repo.exists_nombre(dto.nombre, exclude_id=dto.id):
        raise ValueError("Ya existe otro proyecto con ese nombre.")
    proyectos_repo.update_proyecto(dto.id, dto.dict(exclude={"id"}))

def cerrar(dto: ProyectoClose) -> None:
    proyectos_repo.close_proyecto(dto.id, dto.costo_real_total)

def listar(estado: Optional[str] = None, cliente: Optional[str] = None, search: Optional[str] = None) -> List[ProyectoListItem]:
    rows = proyectos_repo.list_proyectos(estado, cliente, search)
    return [ProyectoListItem(**r) for r in rows]

def clientes() -> List[str]:
    return proyectos_repo.list_distinct_clientes()

def pms_activos() -> Dict[int, str]:
    # PMs activos para selector
    pms = personas_repo.list_personas(rol="PM", solo_activas=True, search=None)
    return {p["id"]: p["nombre"] for p in pms}

def eliminar(proyecto_id: int) -> None:
    proyecto = proyectos_repo.get_proyecto(proyecto_id)
    if not proyecto:
        raise ValueError("Proyecto no encontrado.")
    proyectos_repo.delete_proyecto(proyecto_id)
