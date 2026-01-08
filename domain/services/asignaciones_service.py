'''Reglas de negocio Asignaciones (placeholder)'''
# domain/services/asignaciones_service.py
from typing import Optional, List, Dict, Any
from datetime import date
from domain.schemas.asignaciones import AsignacionCreate, AsignacionUpdate, AsignacionEnd, AsignacionListItem
from infra.repositories import asignaciones_repo, parametros_repo

def _validar_entidades(dto: AsignacionCreate | AsignacionUpdate):
    if not asignaciones_repo.exists_persona(dto.persona_id):
        raise ValueError("La persona no existe o está inactiva.")
    estado_proj = asignaciones_repo.exists_proyecto(dto.proyecto_id)
    if estado_proj is None:
        raise ValueError("El proyecto no existe.")
    if estado_proj == "Cerrado":
        raise ValueError("No puedes asignar personas a un proyecto cerrado.")

def _validar_carga(persona_id: int, nueva_dedicacion: float) -> Dict[str, Any]:
    total_horas, n_proj = asignaciones_repo.carga_persona(persona_id)
    total_post = total_horas + nueva_dedicacion
    overload_threshold = parametros_repo.get_int("OVERLOAD_PROJECTS_THRESHOLD", 4)

    res = {
        "total_horas_actual": total_horas,
        "total_horas_post": total_post,
        "num_proyectos_actual": n_proj,
        "over_projects": n_proj + 1 > overload_threshold,  # si añade nuevo proyecto
        "over_500": total_post > 500.0
    }
    if res["over_500"]:
        raise ValueError(f"Dedicación excede 500 horas (actual {total_horas:.2f}h + nueva {nueva_dedicacion:.2f}h).")
    return res

def crear(dto: AsignacionCreate) -> Dict[str, Any]:
    _validar_entidades(dto)
    info = _validar_carga(dto.persona_id, dto.dedicacion_horas)
    aid = asignaciones_repo.create_asignacion(dto.dict())
    info["asignacion_id"] = aid
    return info

def actualizar(dto: AsignacionUpdate) -> Dict[str, Any]:
    _validar_entidades(dto)
    # Para validar correctamente, restaríamos la dedicación previa si cambia persona; aquí simplificamos:
    info = _validar_carga(dto.persona_id, dto.dedicacion_horas)
    asignaciones_repo.update_asignacion(dto.id, dto.dict(exclude={"id"}))
    return info

def terminar(dto: AsignacionEnd) -> None:
    if dto.fecha_fin > date.today():
        # permitimos fin futuro, pero normalmente fin <= hoy es más realista
        pass
    asignaciones_repo.end_asignacion(dto.id, dto.fecha_fin)

def listar(persona_id: Optional[int] = None, proyecto_id: Optional[int] = None, solo_activas: Optional[bool] = None) -> List[AsignacionListItem]:
    rows = asignaciones_repo.list_asignaciones(persona_id, proyecto_id, solo_activas)
    return [AsignacionListItem(**r) for r in rows]

def carga(persona_id: int) -> Dict[str, Any]:
    total_horas, n_proj = asignaciones_repo.carga_persona(persona_id)
    return {"total_horas": total_horas, "num_proyectos": n_proj}

def eliminar(asignacion_id: int) -> None:
    asignaciones_repo.delete_asignacion(asignacion_id)
