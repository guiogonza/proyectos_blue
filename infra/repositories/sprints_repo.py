'''Acceso MySQL Sprints (placeholder)'''
from typing import Optional, List, Dict, Any
import json
from infra.db.connection import get_conn

def _payload(d):
    import json
    if d is None: return None
    try: return json.dumps(d, ensure_ascii=False)
    except Exception: return json.dumps({"raw": str(d)}, ensure_ascii=False)

def _log(conn, tipo, entidad_id, detalle=None):
    with conn.cursor() as cur:
        try:
            cur.execute(
                "INSERT INTO event_log (actor_id,tipo,entidad,entidad_id,detalle) "
                "VALUES (NULL,%s,'sprints',%s,CAST(%s AS JSON))",
                (tipo, entidad_id, _payload(detalle))
            )
        except Exception:
            cur.execute(
                "INSERT INTO event_log (actor_id,tipo,entidad,entidad_id,detalle) "
                "VALUES (NULL,%s,'sprints',%s,NULL)", (tipo, entidad_id)
            )

def create_sprint(data: Dict[str, Any]) -> int:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO sprints (proyecto_id,nombre,fecha_inicio,fecha_fin,costo_estimado,estado,actividades) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (data["proyecto_id"], data["nombre"], data["fecha_inicio"], data["fecha_fin"],
             data["costo_estimado"], data["estado"], data.get("actividades"))
        )
        sid = cur.lastrowid
        _log(conn, "create", sid, {"nombre": data["nombre"]})
        return sid

def update_sprint(sid: int, data: Dict[str, Any]) -> None:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE sprints SET proyecto_id=%s,nombre=%s,fecha_inicio=%s,fecha_fin=%s,costo_estimado=%s,estado=%s,actividades=%s "
            "WHERE id=%s",
            (data["proyecto_id"], data["nombre"], data["fecha_inicio"], data["fecha_fin"],
             data["costo_estimado"], data["estado"], data.get("actividades"), sid)
        )
        _log(conn, "update", sid, {"estado": data["estado"]})

def close_sprint(sid: int, costo_real: float) -> None:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("UPDATE sprints SET estado='Cerrado', costo_real=%s WHERE id=%s", (costo_real, sid))
        _log(conn, "close", sid, {"costo_real": costo_real})

def list_sprints(proyecto_id: Optional[int] = None, estado: Optional[str] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
    sql = "SELECT s.*, p.nombre as proyecto_nombre FROM sprints s LEFT JOIN proyectos p ON s.proyecto_id = p.id"
    where, params = [], []
    if proyecto_id: where.append("s.proyecto_id=%s"); params.append(proyecto_id)
    if estado: where.append("s.estado=%s"); params.append(estado)
    if search:
        where.append("s.nombre LIKE %s"); params.append(f"%{search}%")
    if where: sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY s.fecha_inicio DESC, s.id DESC"
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, tuple(params))
        return cur.fetchall()

def get_sprint(sid: int) -> Optional[Dict[str, Any]]:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM sprints WHERE id=%s", (sid,))
        return cur.fetchone()

def delete_sprint(sid: int) -> None:
    with get_conn() as conn, conn.cursor() as cur:
        # Eliminar asignaciones relacionadas con este sprint
        cur.execute("DELETE FROM asignaciones WHERE sprint_id=%s", (sid,))
        
        # Eliminar el sprint
        cur.execute("DELETE FROM sprints WHERE id=%s", (sid,))
        _log(conn, "delete", sid)
