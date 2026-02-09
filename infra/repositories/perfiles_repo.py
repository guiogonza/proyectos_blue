# infra/repositories/perfiles_repo.py
from typing import List, Optional, Dict, Any
import json
from infra.db.connection import get_conn

def _prepare_json_payload(detalle: Dict[str, Any] | None) -> Optional[str]:
    if detalle is None:
        return None
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
                (actor_id, tipo, "perfiles", entidad_id, payload)
            )
        except Exception:
            cur.execute(
                "INSERT INTO event_log (actor_id, tipo, entidad, entidad_id, detalle) "
                "VALUES (%s,%s,%s,%s,NULL)",
                (actor_id, tipo, "perfiles", entidad_id)
            )

def create_perfil(nombre: str, tarifa_sin_iva: Optional[float] = None, vigencia=None) -> int:
    """Crea un nuevo perfil y devuelve su ID"""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO perfiles (nombre, tarifa_sin_iva, vigencia, activo) VALUES (%s, %s, %s, 1)",
            (nombre, tarifa_sin_iva, vigencia)
        )
        perfil_id = cur.lastrowid
        _log_event(conn, "create", perfil_id, {"nombre": nombre, "tarifa_sin_iva": tarifa_sin_iva, "vigencia": str(vigencia) if vigencia else None})
        return perfil_id

def update_perfil(perfil_id: int, nombre: str, activo: bool = True, tarifa_sin_iva: Optional[float] = None, vigencia=None) -> None:
    """Actualiza un perfil existente"""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE perfiles SET nombre=%s, tarifa_sin_iva=%s, vigencia=%s, activo=%s WHERE id=%s",
            (nombre, tarifa_sin_iva, vigencia, 1 if activo else 0, perfil_id)
        )
        _log_event(conn, "update", perfil_id, {"nombre": nombre, "tarifa_sin_iva": tarifa_sin_iva, "vigencia": str(vigencia) if vigencia else None, "activo": activo})

def delete_perfil(perfil_id: int) -> None:
    """Elimina un perfil verificando que no tenga asignaciones"""
    with get_conn() as conn, conn.cursor() as cur:
        # Verificar si tiene asignaciones
        cur.execute("SELECT COUNT(*) as cnt FROM asignaciones WHERE perfil_id=%s", (perfil_id,))
        asig_count = cur.fetchone()["cnt"]
        if asig_count > 0:
            raise ValueError(
                f"❌ No se puede eliminar. El perfil tiene {asig_count} asignación(es) asociada(s).\n\n"
                f"💡 **Solución:** Primero cambie el perfil en las asignaciones que lo usan."
            )
        
        cur.execute("DELETE FROM perfiles WHERE id=%s", (perfil_id,))
        _log_event(conn, "delete", perfil_id, None)

def set_activo(perfil_id: int, activo: bool) -> None:
    """Activa o desactiva un perfil"""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("UPDATE perfiles SET activo=%s WHERE id=%s", (1 if activo else 0, perfil_id))
        _log_event(conn, "status_change", perfil_id, {"activo": activo})

def get_perfil(perfil_id: int) -> Optional[Dict[str, Any]]:
    """Obtiene un perfil por ID"""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM perfiles WHERE id=%s", (perfil_id,))
        return cur.fetchone()

def list_perfiles(solo_activos: Optional[bool] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
    """Lista todos los perfiles con filtros opcionales"""
    sql = "SELECT * FROM perfiles"
    where = []
    params: List[Any] = []
    
    if solo_activos is not None:
        where.append("activo = %s")
        params.append(1 if solo_activos else 0)
    if search:
        where.append("nombre LIKE %s")
        params.append(f"%{search}%")
    
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY nombre ASC"
    
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, tuple(params))
        return cur.fetchall()

def exists_nombre(nombre: str, exclude_id: Optional[int] = None) -> bool:
    """Verifica si ya existe un perfil con el nombre dado"""
    sql = "SELECT id FROM perfiles WHERE nombre=%s"
    params: List[Any] = [nombre]
    if exclude_id:
        sql += " AND id<>%s"
        params.append(exclude_id)
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, tuple(params))
        return cur.fetchone() is not None

def get_perfiles_para_asignacion() -> List[Dict[str, Any]]:
    """Obtiene lista de perfiles activos para usar en asignaciones"""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT id, nombre FROM perfiles WHERE activo=1 ORDER BY nombre ASC"
        )
        return cur.fetchall()
