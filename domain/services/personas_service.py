'''Reglas de negocio Personas (placeholder)'''
# domain/services/personas_service.py
from typing import List, Optional
from domain.schemas.personas import PersonaCreate, PersonaUpdate, PersonaListItem
from infra.repositories import personas_repo

def crear(dto: PersonaCreate) -> int:
    if personas_repo.exists_nombre(dto.nombre):
        raise ValueError("Ya existe una persona con ese nombre.")
    return personas_repo.create_persona(dto.nombre, dto.rol, dto.tarifa_interna, 
                                       dto.cedula, dto.numero_contacto, dto.correo, True)

def actualizar(dto: PersonaUpdate) -> None:
    if personas_repo.exists_nombre(dto.nombre, exclude_id=dto.id):
        raise ValueError("Ya existe otra persona con ese nombre.")
    personas_repo.update_persona(dto.id, dto.nombre, dto.rol, dto.tarifa_interna,
                                dto.cedula, dto.numero_contacto, dto.correo, dto.activo)

def cambiar_estado(persona_id: int, activo: bool) -> None:
    personas_repo.set_activo(persona_id, activo)

def listar(rol: Optional[str] = None, solo_activas: Optional[bool] = None, search: Optional[str] = None) -> List[PersonaListItem]:
    rows = personas_repo.list_personas(rol, solo_activas, search)
    return [PersonaListItem(**{
        "id": r["id"],
        "nombre": r["nombre"],
        "rol": r["rol"],
        "tarifa_interna": r["tarifa_interna"],
        "activo": bool(r["activo"]),
        "cedula": r.get("cedula"),
        "numero_contacto": r.get("numero_contacto"),
        "correo": r.get("correo"),
    }) for r in rows]

def eliminar(persona_id: int) -> None:
    # Verificar si tiene asignaciones o usuarios vinculados
    persona = personas_repo.get_persona(persona_id)
    if not persona:
        raise ValueError("Persona no encontrada.")
    personas_repo.delete_persona(persona_id)
