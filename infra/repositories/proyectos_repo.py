'''Acceso MySQL Proyectos (placeholder)'''
# infra/repositories/proyectos_repo.py
from typing import Optional, List, Dict, Any
import json
from infra.db.connection import get_conn

def _prepare_json_payload(detalle: Dict[str, Any] | None) -> Optional[str]:
    if detalle is None: return None
    try:
        return json.dumps(detalle, ensure_ascii=False)
    except Exception:
        return json.dumps({"raw": str(detalle)}, ensure_ascii=False)

def _log_event(conn, tipo: str, entidad: str, entidad_id: int,
               detalle: Dict[str, Any] | None = None, actor_id: int | None = None):
    payload = _prepare_json_payload(detalle)
    with conn.cursor() as cur:
        try:
            cur.execute(
                "INSERT INTO event_log (actor_id, tipo, entidad, entidad_id, detalle) "
                "VALUES (%s,%s,%s,%s,CAST(%s AS JSON))",
                (actor_id, tipo, "proyectos", entidad_id, payload)
            )
        except Exception:
            cur.execute(
                "INSERT INTO event_log (actor_id, tipo, entidad, entidad_id, detalle) "
                "VALUES (%s,%s,%s,%s,NULL)",
                (actor_id, tipo, "proyectos", entidad_id)
            )

def exists_nombre(nombre: str, exclude_id: Optional[int] = None) -> bool:
    sql = "SELECT id FROM proyectos WHERE nombre=%s"
    params = [nombre]
    if exclude_id:
        sql += " AND id<>%s"; params.append(exclude_id)
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, tuple(params))
        return cur.fetchone() is not None

def create_proyecto(data: Dict[str, Any]) -> int:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO proyectos
               (nombre, cliente, pm_id, fecha_inicio, fecha_fin_planeada, estado, costo_estimado_total, costo_real_total, baseline_fecha)
               VALUES (%s,%s,%s,%s,%s,%s,%s,NULL,NOW())""",
            (data["nombre"], data.get("cliente"), data.get("pm_id"),
             data["fecha_inicio"], data["fecha_fin_planeada"],
             data["estado"], data["costo_estimado_total"])
        )
        pid = cur.lastrowid
        _log_event(conn, "create", "proyectos", pid, {"nombre": data["nombre"], "estado": data["estado"]})
        return pid

def update_proyecto(pid: int, data: Dict[str, Any]) -> None:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """UPDATE proyectos
               SET nombre=%s, cliente=%s, pm_id=%s, fecha_inicio=%s, fecha_fin_planeada=%s,
                   estado=%s, costo_estimado_total=%s
               WHERE id=%s""",
            (data["nombre"], data.get("cliente"), data.get("pm_id"),
             data["fecha_inicio"], data["fecha_fin_planeada"],
             data["estado"], data["costo_estimado_total"], pid)
        )
        _log_event(conn, "update", "proyectos", pid, {"nombre": data["nombre"], "estado": data["estado"]})

def close_proyecto(pid: int, costo_real_total: float) -> None:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE proyectos SET estado='Cerrado', costo_real_total=%s WHERE id=%s",
            (costo_real_total, pid)
        )
        _log_event(conn, "close", "proyectos", pid, {"costo_real_total": costo_real_total})

def get_proyecto(pid: int) -> Optional[Dict[str, Any]]:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM proyectos WHERE id=%s", (pid,))
        return cur.fetchone()

def delete_proyecto(pid: int) -> None:
    with get_conn() as conn, conn.cursor() as cur:
        # Eliminar asignaciones relacionadas
        cur.execute("DELETE FROM asignaciones WHERE proyecto_id=%s", (pid,))
        
        # Eliminar sprints relacionados (que a su vez eliminará asignaciones de esos sprints)
        cur.execute("SELECT id FROM sprints WHERE proyecto_id=%s", (pid,))
        sprint_ids = [row["id"] for row in cur.fetchall()]
        for sid in sprint_ids:
            cur.execute("DELETE FROM asignaciones WHERE sprint_id=%s", (sid,))
        cur.execute("DELETE FROM sprints WHERE proyecto_id=%s", (pid,))
        
        # Eliminar el proyecto
        cur.execute("DELETE FROM proyectos WHERE id=%s", (pid,))
        _log_event(conn, "delete", "proyectos", pid, {"sprints_eliminados": len(sprint_ids)})

def list_proyectos(estado: Optional[str] = None, cliente: Optional[str] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
    sql = "SELECT * FROM proyectos"
    where, params = [], []
    if estado: where.append("estado=%s"); params.append(estado)
    if cliente: where.append("cliente=%s"); params.append(cliente)
    if search:
        where.append("(nombre LIKE %s OR cliente LIKE %s)")
        like = f"%{search}%"; params.extend([like, like])
    if where: sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY created_at DESC, nombre ASC"
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, tuple(params))
        return cur.fetchall()

def list_distinct_clientes() -> List[str]:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT DISTINCT cliente FROM proyectos WHERE cliente IS NOT NULL AND cliente<>'' ORDER BY cliente ASC")
        return [r["cliente"] for r in cur.fetchall()]
