# infra/repositories/eventlog_repo.py
from typing import Optional, List, Dict, Any, Tuple
from infra.db.connection import get_conn

def list_events(entidad: Optional[str] = None, tipo: Optional[str] = None, limit: int = 200) -> List[Dict[str, Any]]:
    sql = "SELECT id, actor_id, tipo, entidad, entidad_id, detalle, ts FROM event_log"
    where, params = [], []
    if entidad: 
        where.append("entidad=%s")
        params.append(entidad)
    if tipo:    
        where.append("tipo=%s")
        params.append(tipo)
    if where: sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY id DESC LIMIT %s"
    params.append(limit)
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, tuple(params))
        return list(cur.fetchall())
