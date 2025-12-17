# infra/repositories/personas_repo.py
from typing import List, Optional, Dict, Any
import json
from infra.db.connection import get_conn

def _prepare_json_payload(detalle: Dict[str, Any] | None) -> Optional[str]:
    """
    Devuelve un string JSON válido (o None).
    - Si 'detalle' ya es serializable → json.dumps(...)
    - Si no es serializable → lo guarda como {"raw": "..."} para no romper.
    """
    if detalle is None:
        return None
    try:
        return json.dumps(detalle, ensure_ascii=False)
    except Exception:
        # Fallback: algo no serializable (e.g., objetos, sets, bytes)
        return json.dumps({"raw": str(detalle)}, ensure_ascii=False)

def _log_event(conn, tipo: str, entidad: str, entidad_id: int,
               detalle: Dict[str, Any] | None = None, actor_id: int | None = None):
    """
    Inserta en event_log con columna JSON 'detalle' de forma segura.
    Usa CAST(? AS JSON) para que MySQL valide el payload. Si falla, inserta NULL.
    """
    payload = _prepare_json_payload(detalle)
    with conn.cursor() as cur:
        try:
            # CAST maneja NULL → NULL y valida el string como JSON
            cur.execute(
                "INSERT INTO event_log (actor_id, tipo, entidad, entidad_id, detalle) "
                "VALUES (%s, %s, %s, %s, CAST(%s AS JSON))",
                (actor_id, tipo, entidad, entidad_id, payload)
            )
        except Exception:
            # Último recurso: guarda sin detalle (pero no pierde el evento)
            cur.execute(
                "INSERT INTO event_log (actor_id, tipo, entidad, entidad_id, detalle) "
                "VALUES (%s, %s, %s, %s, NULL)",
                (actor_id, tipo, entidad, entidad_id)
            )

def create_persona(nombre: str, ROL_PRINCIPAL: str, COSTO_RECURSO: Optional[float], 
                  NUMERO_DOCUMENTO: Optional[str] = None, numero_contacto: Optional[str] = None,
                  correo: Optional[str] = None, PAIS: Optional[str] = None, SENIORITY: Optional[str] = None,
                  LIDER_DIRECTO: Optional[int] = None, TIPO_DOCUMENTO: Optional[str] = None, 
                  activo: bool = True) -> int:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO personas (nombre, ROL_PRINCIPAL, COSTO_RECURSO, NUMERO_DOCUMENTO, numero_contacto, correo, "
            "PAIS, SENIORITY, LIDER_DIRECTO, TIPO_DOCUMENTO, activo) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (nombre, ROL_PRINCIPAL, COSTO_RECURSO, NUMERO_DOCUMENTO, numero_contacto, correo, 
             PAIS, SENIORITY, LIDER_DIRECTO, TIPO_DOCUMENTO, 1 if activo else 0)
        )
        persona_id = cur.lastrowid
        _log_event(conn, "create", "personas", persona_id, {"nombre": nombre, "ROL_PRINCIPAL": ROL_PRINCIPAL})
        return persona_id

def update_persona(persona_id: int, nombre: str, ROL_PRINCIPAL: str, COSTO_RECURSO: Optional[float],
                  NUMERO_DOCUMENTO: Optional[str] = None, numero_contacto: Optional[str] = None,
                  correo: Optional[str] = None, PAIS: Optional[str] = None, SENIORITY: Optional[str] = None,
                  LIDER_DIRECTO: Optional[int] = None, TIPO_DOCUMENTO: Optional[str] = None,
                  activo: bool = True) -> None:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE personas SET nombre=%s, ROL_PRINCIPAL=%s, COSTO_RECURSO=%s, NUMERO_DOCUMENTO=%s, "
            "numero_contacto=%s, correo=%s, PAIS=%s, SENIORITY=%s, LIDER_DIRECTO=%s, TIPO_DOCUMENTO=%s, activo=%s WHERE id=%s",
            (nombre, ROL_PRINCIPAL, COSTO_RECURSO, NUMERO_DOCUMENTO, numero_contacto, correo,
             PAIS, SENIORITY, LIDER_DIRECTO, TIPO_DOCUMENTO, 1 if activo else 0, persona_id)
        )
        _log_event(conn, "update", "personas", persona_id, {"nombre": nombre, "ROL_PRINCIPAL": ROL_PRINCIPAL, "activo": activo})

def set_activo(persona_id: int, activo: bool) -> None:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("UPDATE personas SET activo=%s WHERE id=%s", (1 if activo else 0, persona_id))
        _log_event(conn, "status_change", "personas", persona_id, {"activo": activo})

def get_persona(persona_id: int) -> Optional[Dict[str, Any]]:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM personas WHERE id=%s", (persona_id,))
        return cur.fetchone()

def list_personas(rol: Optional[str] = None, solo_activas: Optional[bool] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
    sql = """SELECT p.*, l.nombre as LIDER_NOMBRE 
             FROM personas p 
             LEFT JOIN personas l ON p.LIDER_DIRECTO = l.id"""
    where = []
    params: List[Any] = []
    if rol:
        where.append("p.ROL_PRINCIPAL = %s")
        params.append(rol)
    if solo_activas is not None:
        where.append("p.activo = %s")
        params.append(1 if solo_activas else 0)
    if search:
        where.append("(p.nombre LIKE %s OR p.ROL_PRINCIPAL LIKE %s)")
        like = f"%{search}%"
        params.extend([like, like])
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY p.created_at DESC, p.nombre ASC"
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, tuple(params))
        rows = cur.fetchall()
    return rows

def exists_nombre(nombre: str, exclude_id: Optional[int] = None) -> bool:
    sql = "SELECT id FROM personas WHERE nombre=%s"
    params: List[Any] = [nombre]
    if exclude_id:
        sql += " AND id<>%s"
        params.append(exclude_id)
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, tuple(params))
        row = cur.fetchone()
    return row is not None

def get_personas_para_lider() -> List[Dict[str, Any]]:
    """Obtiene lista de personas activas que pueden ser líderes"""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT id, nombre, ROL_PRINCIPAL FROM personas WHERE activo=1 ORDER BY nombre ASC"
        )
        return cur.fetchall()

def delete_persona(persona_id: int) -> None:
    with get_conn() as conn, conn.cursor() as cur:
        # Verificar si tiene asignaciones
        cur.execute("SELECT COUNT(*) as cnt FROM asignaciones WHERE persona_id=%s", (persona_id,))
        asig_count = cur.fetchone()["cnt"]
        if asig_count > 0:
            raise ValueError(
                f"❌ No se puede eliminar. La persona tiene {asig_count} asignación(es) activa(s).\n\n"
                f"💡 **Solución:** Primero vaya a la sección 'Asignaciones' y elimine todas las asignaciones de esta persona."
            )
        
        # Verificar si tiene usuarios
        cur.execute("SELECT COUNT(*) as cnt FROM usuarios WHERE persona_id=%s", (persona_id,))
        user_count = cur.fetchone()["cnt"]
        if user_count > 0:
            raise ValueError(
                f"❌ No se puede eliminar. La persona tiene {user_count} usuario(s) asociado(s).\n\n"
                f"💡 **Solución:** Primero vaya a la sección 'Usuarios' y elimine o desvincula los usuarios de esta persona."
            )
        
        # Verificar si es PM de algún proyecto
        cur.execute("SELECT COUNT(*) as cnt FROM proyectos WHERE pm_id=%s", (persona_id,))
        pm_count = cur.fetchone()["cnt"]
        if pm_count > 0:
            raise ValueError(
                f"❌ No se puede eliminar. La persona es PM de {pm_count} proyecto(s).\n\n"
                f"💡 **Solución:** Primero vaya a la sección 'Proyectos' y cambie el PM de esos proyectos o elimine los proyectos."
            )
        
        cur.execute("DELETE FROM personas WHERE id=%s", (persona_id,))
        _log_event(conn, "delete", "personas", persona_id)
