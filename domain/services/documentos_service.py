# domain/services/documentos_service.py
from typing import List, Optional
from domain.schemas.documentos import DocumentoCreate, DocumentoUpdate, DocumentoListItem
from infra.repositories import documentos_repo
import os

def crear(dto: DocumentoCreate) -> int:
    return documentos_repo.create_documento(
        dto.proyecto_id, dto.nombre_archivo, dto.ruta_archivo,
        dto.descripcion, dto.tamanio_bytes, dto.tipo_mime,
        dto.valor, dto.iva, dto.fecha_documento
    )

def actualizar(dto: DocumentoUpdate) -> None:
    documentos_repo.update_documento(dto.id, dto.nombre_archivo, dto.descripcion,
                                     dto.valor, dto.iva, dto.fecha_documento)

def eliminar(doc_id: int) -> None:
    # Obtener documento para eliminar archivo físico
    doc = documentos_repo.get_documento(doc_id)
    if doc:
        # Intentar eliminar archivo físico
        try:
            if os.path.exists(doc["ruta_archivo"]):
                os.remove(doc["ruta_archivo"])
        except Exception:
            pass  # Continuar aunque falle eliminar el archivo
    documentos_repo.delete_documento(doc_id)

def listar(proyecto_id: Optional[int] = None, search: Optional[str] = None) -> List[DocumentoListItem]:
    rows = documentos_repo.list_documentos(proyecto_id, search)
    return [DocumentoListItem(**r) for r in rows]

def obtener(doc_id: int) -> Optional[DocumentoListItem]:
    doc = documentos_repo.get_documento(doc_id)
    if doc:
        return DocumentoListItem(**doc)
    return None

def contar_por_proyecto(proyecto_id: int) -> int:
    return documentos_repo.count_by_proyecto(proyecto_id)
