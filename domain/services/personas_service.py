'''Reglas de negocio Personas (placeholder)'''
# domain/services/personas_service.py
from typing import List, Optional, Dict, Any
from domain.schemas.personas import PersonaCreate, PersonaUpdate, PersonaListItem
from infra.repositories import personas_repo

def crear(dto: PersonaCreate) -> int:
    if personas_repo.exists_nombre(dto.nombre):
        raise ValueError("Ya existe una persona con ese nombre.")
    return personas_repo.create_persona(
        dto.nombre, dto.ROL_PRINCIPAL, dto.COSTO_RECURSO, 
        dto.NUMERO_DOCUMENTO, dto.numero_contacto, dto.correo,
        dto.PAIS, dto.SENIORITY, dto.LIDER_DIRECTO, dto.TIPO_DOCUMENTO, True
    )

def actualizar(dto: PersonaUpdate) -> None:
    if personas_repo.exists_nombre(dto.nombre, exclude_id=dto.id):
        raise ValueError("Ya existe otra persona con ese nombre.")
    personas_repo.update_persona(
        dto.id, dto.nombre, dto.ROL_PRINCIPAL, dto.COSTO_RECURSO,
        dto.NUMERO_DOCUMENTO, dto.numero_contacto, dto.correo,
        dto.PAIS, dto.SENIORITY, dto.LIDER_DIRECTO, dto.TIPO_DOCUMENTO, dto.activo
    )

def cambiar_estado(persona_id: int, activo: bool) -> None:
    personas_repo.set_activo(persona_id, activo)

def listar(rol: Optional[str] = None, solo_activas: Optional[bool] = None, search: Optional[str] = None) -> List[PersonaListItem]:
    rows = personas_repo.list_personas(rol, solo_activas, search)
    return [PersonaListItem(**{
        "id": r["id"],
        "nombre": r["nombre"],
        "ROL_PRINCIPAL": r["ROL_PRINCIPAL"],
        "COSTO_RECURSO": r["COSTO_RECURSO"],
        "activo": bool(r["activo"]),
        "NUMERO_DOCUMENTO": r.get("NUMERO_DOCUMENTO"),
        "numero_contacto": r.get("numero_contacto"),
        "correo": r.get("correo"),
        "PAIS": r.get("PAIS"),
        "SENIORITY": r.get("SENIORITY"),
        "LIDER_DIRECTO": r.get("LIDER_DIRECTO"),
        "LIDER_NOMBRE": r.get("LIDER_NOMBRE"),
        "TIPO_DOCUMENTO": r.get("TIPO_DOCUMENTO"),
    }) for r in rows]

def get_personas_para_lider() -> List[Dict[str, Any]]:
    """Obtiene lista de personas que pueden ser líderes"""
    return personas_repo.get_personas_para_lider()

def eliminar(persona_id: int) -> None:
    # Verificar si tiene asignaciones o usuarios vinculados
    persona = personas_repo.get_persona(persona_id)
    if not persona:
        raise ValueError("Persona no encontrada.")
    personas_repo.delete_persona(persona_id)
