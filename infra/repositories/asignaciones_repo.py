'''Acceso MySQL Asignaciones (placeholder)'''
# infra/repositories/asignaciones_repo.py
from typing import Optional, List, Dict, Any, Tuple
import json
from infra.db.connection import get_conn

def _prepare_json_payload(detalle: Dict[str, Any] | None) -> Optional[str]:
    if detalle is None: return None
    try:
        return json.dumps(detalle, ensure_ascii=False)
    except Exception:
        return json.dumps({"raw": str(detalle)}, ensure_ascii=False)

def _log_event(conn, tipo: str, entidad_id: int, detalle: Dict[str, Any] | None = None, actor_id: int | None = None):
    payload = _prepare_json_payload(detalle)
    with conn.cursor() as cur:
        try:
            cur.execute(
                "INSERT INTO event_log (actor_id, tipo, entidad, entidad_id, detalle) "
                "VALUES (%s,%s,%s,%s,CAST(%s AS JSON))",
                (actor_id, tipo, "asignaciones", entidad_id, payload)
            )
        except Exception:
            cur.execute(
                "INSERT INTO event_log (actor_id, tipo, entidad, entidad_id, detalle) "
                "VALUES (%s,%s,%s,%s,NULL)",
                (actor_id, tipo, "asignaciones", entidad_id)
            )

# ---- Existence helpers ----
def exists_persona(persona_id: int) -> bool:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT 1 FROM personas WHERE id=%s AND activo=1", (persona_id,))
        return cur.fetchone() is not None

def exists_proyecto(proyecto_id: int) -> Optional[str]:
    """Devuelve estado del proyecto si existe, None si no existe"""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT estado FROM proyectos WHERE id=%s", (proyecto_id,))
        row = cur.fetchone()
        return row["estado"] if row else None

# ---- CRUD ----
def create_asignacion(data: Dict[str, Any]) -> int:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO asignaciones (persona_id, proyecto_id, sprint_id, perfil_id, dedicacion_horas, tarifa, fecha_asignacion, fecha_fin) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
            (data["persona_id"], data["proyecto_id"], data.get("sprint_id"), data.get("perfil_id"),
             data["dedicacion_horas"], data.get("tarifa"), data["fecha_asignacion"], data.get("fecha_fin"))
        )
        aid = cur.lastrowid
        _log_event(conn, "create", aid, {"persona_id": data["persona_id"], "proyecto_id": data["proyecto_id"], "perfil_id": data.get("perfil_id"), "dedicacion_horas": data["dedicacion_horas"], "tarifa": data.get("tarifa")})
        return aid

def update_asignacion(aid: int, data: Dict[str, Any]) -> None:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE asignaciones SET persona_id=%s, proyecto_id=%s, sprint_id=%s, perfil_id=%s, dedicacion_horas=%s, tarifa=%s, fecha_asignacion=%s, fecha_fin=%s WHERE id=%s",
            (data["persona_id"], data["proyecto_id"], data.get("sprint_id"), data.get("perfil_id"),
             data["dedicacion_horas"], data.get("tarifa"), data["fecha_asignacion"], data.get("fecha_fin"), aid)
        )
        _log_event(conn, "update", aid, {"perfil_id": data.get("perfil_id"), "dedicacion_horas": data["dedicacion_horas"], "tarifa": data.get("tarifa")})

def end_asignacion(aid: int, fecha_fin) -> None:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("UPDATE asignaciones SET fecha_fin=%s WHERE id=%s", (fecha_fin, aid))
        _log_event(conn, "end", aid, {"fecha_fin": str(fecha_fin)})

def delete_asignacion(aid: int) -> None:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM asignaciones WHERE id=%s", (aid,))
        _log_event(conn, "delete", aid, None)

# ---- Listados ----
def list_asignaciones(persona_id: Optional[int] = None, proyecto_id: Optional[int] = None, solo_activas: Optional[bool] = None) -> List[Dict[str, Any]]:
    sql = ( "SELECT a.*, p.nombre AS persona_nombre, pr.nombre AS proyecto_nombre, s.nombre AS sprint_nombre, pf.nombre AS perfil_nombre "
            "FROM asignaciones a "
            "JOIN personas p ON p.id=a.persona_id "
            "JOIN proyectos pr ON pr.id=a.proyecto_id "
            "LEFT JOIN sprints s ON s.id=a.sprint_id "
            "LEFT JOIN perfiles pf ON pf.id=a.perfil_id " )
    where, params = [], []
    if persona_id:
        where.append("a.persona_id=%s"); params.append(persona_id)
    if proyecto_id:
        where.append("a.proyecto_id=%s"); params.append(proyecto_id)
    if solo_activas is not None:
        if solo_activas:
            where.append("(a.fecha_fin IS NULL OR a.fecha_fin >= CURDATE())")
        else:
            where.append("(a.fecha_fin IS NOT NULL AND a.fecha_fin < CURDATE())")
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY a.fecha_asignacion DESC, a.id DESC"
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, tuple(params))
        return cur.fetchall()

# ---- Métricas de carga ----
def carga_persona(persona_id: int) -> Tuple[float, int]:
    """
    Devuelve (suma_dedicacion_horas_activa, num_proyectos_activos) para la persona.
    Activo = asignación sin fecha_fin o con fecha_fin >= hoy y proyecto != 'Cerrado'.
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT COALESCE(SUM(a.dedicacion_horas),0) AS total_horas, COUNT(DISTINCT a.proyecto_id) AS n_proj
               FROM asignaciones a
               JOIN proyectos pr ON pr.id = a.proyecto_id
               WHERE a.persona_id=%s
                 AND (a.fecha_fin IS NULL OR a.fecha_fin >= CURDATE())
                 AND pr.estado <> 'Cerrado'""",
            (persona_id,)
        )
        row = cur.fetchone()
        return float(row["total_horas"]), int(row["n_proj"])
