# infra/repositories/documentos_repo.py
from typing import Optional, List, Dict, Any
from datetime import date
from infra.db.connection import get_conn

def create_documento(proyecto_id: int, nombre_archivo: str, ruta_archivo: Optional[str] = None, 
                     descripcion: Optional[str] = None, tamanio_bytes: Optional[int] = None,
                     tipo_mime: Optional[str] = None, valor: Optional[float] = None,
                     iva: Optional[float] = None, fecha_documento: Optional[date] = None) -> int:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO documentos 
               (proyecto_id, nombre_archivo, descripcion, ruta_archivo, tamanio_bytes, tipo_mime, fecha_carga, valor, iva, fecha_documento)
               VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s, %s, %s)""",
            (proyecto_id, nombre_archivo, descripcion, ruta_archivo, tamanio_bytes, tipo_mime, valor, iva, fecha_documento)
        )
        return cur.lastrowid

def update_documento(doc_id: int, nombre_archivo: str, descripcion: Optional[str] = None,
                     valor: Optional[float] = None, iva: Optional[float] = None,
                     fecha_documento: Optional[date] = None) -> None:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE documentos SET nombre_archivo=%s, descripcion=%s, valor=%s, iva=%s, fecha_documento=%s WHERE id=%s",
            (nombre_archivo, descripcion, valor, iva, fecha_documento, doc_id)
        )

def delete_documento(doc_id: int) -> None:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM documentos WHERE id=%s", (doc_id,))

def get_documento(doc_id: int) -> Optional[Dict[str, Any]]:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM documentos WHERE id=%s", (doc_id,))
        return cur.fetchone()

def list_documentos(proyecto_id: Optional[int] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
    sql = """SELECT d.*, p.NOMBRE as proyecto_nombre 
             FROM documentos d
             LEFT JOIN proyectos p ON d.proyecto_id = p.id"""
    where, params = [], []
    if proyecto_id:
        where.append("d.proyecto_id=%s")
        params.append(proyecto_id)
    if search:
        where.append("(d.nombre_archivo LIKE %s OR d.descripcion LIKE %s)")
        like = f"%{search}%"
        params.extend([like, like])
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY d.fecha_carga DESC"
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, tuple(params))
        return cur.fetchall()

def count_by_proyecto(proyecto_id: int) -> int:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) as total FROM documentos WHERE proyecto_id=%s", (proyecto_id,))
        result = cur.fetchone()
        return result["total"] if result else 0
