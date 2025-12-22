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
    sql = "SELECT id FROM proyectos WHERE NOMBRE=%s"
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
               (NOMBRE, cliente, pm_id, FECHA_INICIO, FECHA_FIN_ESTIMADA, ESTADO, BUDGET, COSTO_REAL_TOTAL, baseline_fecha,
                PAIS, CATEGORIA, LIDER_BLUETAB, LIDER_CLIENTE, FECHA_FIN, MANAGER_BLUETAB)
               VALUES (%s,%s,%s,%s,%s,%s,%s,NULL,NOW(),%s,%s,%s,%s,%s,%s)""",
            (data["NOMBRE"], data.get("cliente"), data.get("pm_id"),
             data["FECHA_INICIO"], data["FECHA_FIN_ESTIMADA"],
             data["ESTADO"], data["BUDGET"],
             data.get("PAIS"), data.get("CATEGORIA"), data.get("LIDER_BLUETAB"),
             data.get("LIDER_CLIENTE"), data.get("FECHA_FIN"), data.get("MANAGER_BLUETAB"))
        )
        pid = cur.lastrowid
        _log_event(conn, "create", "proyectos", pid, {"NOMBRE": data["NOMBRE"], "ESTADO": data["ESTADO"]})
        return pid

def update_proyecto(pid: int, data: Dict[str, Any]) -> None:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """UPDATE proyectos
               SET NOMBRE=%s, cliente=%s, pm_id=%s, FECHA_INICIO=%s, FECHA_FIN_ESTIMADA=%s,
                   ESTADO=%s, BUDGET=%s, PAIS=%s, CATEGORIA=%s, LIDER_BLUETAB=%s,
                   LIDER_CLIENTE=%s, FECHA_FIN=%s, MANAGER_BLUETAB=%s
               WHERE id=%s""",
            (data["NOMBRE"], data.get("cliente"), data.get("pm_id"),
             data["FECHA_INICIO"], data["FECHA_FIN_ESTIMADA"],
             data["ESTADO"], data["BUDGET"],
             data.get("PAIS"), data.get("CATEGORIA"), data.get("LIDER_BLUETAB"),
             data.get("LIDER_CLIENTE"), data.get("FECHA_FIN"), data.get("MANAGER_BLUETAB"), pid)
        )
        _log_event(conn, "update", "proyectos", pid, {"NOMBRE": data["NOMBRE"], "ESTADO": data["ESTADO"]})

def close_proyecto(pid: int, COSTO_REAL_TOTAL: float) -> None:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE proyectos SET ESTADO='Cerrado', COSTO_REAL_TOTAL=%s WHERE id=%s",
            (COSTO_REAL_TOTAL, pid)
        )
        _log_event(conn, "close", "proyectos", pid, {"COSTO_REAL_TOTAL": COSTO_REAL_TOTAL})

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
    sql = """SELECT p.*, per.nombre as lider_nombre 
             FROM proyectos p 
             LEFT JOIN personas per ON p.pm_id = per.id"""
    where, params = [], []
    if estado: where.append("p.ESTADO=%s"); params.append(estado)
    if cliente: where.append("p.cliente=%s"); params.append(cliente)
    if search:
        where.append("(p.NOMBRE LIKE %s OR p.cliente LIKE %s)")
        like = f"%{search}%"; params.extend([like, like])
    if where: sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY p.created_at DESC, p.NOMBRE ASC"
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, tuple(params))
        return cur.fetchall()

def list_distinct_clientes() -> List[str]:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT DISTINCT cliente FROM proyectos WHERE cliente IS NOT NULL AND cliente<>'' ORDER BY cliente ASC")
        return [r["cliente"] for r in cur.fetchall()]
