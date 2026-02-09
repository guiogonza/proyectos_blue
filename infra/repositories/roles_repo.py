# infra/repositories/roles_repo.py
from typing import List, Optional, Dict, Any
from infra.db.connection import get_conn


def list_roles(solo_activos: Optional[bool] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
    sql = "SELECT id, nombre, activo, created_at FROM roles_principales"
    where: List[str] = []
    params: List[Any] = []
    if solo_activos is not None:
        where.append("activo = %s")
        params.append(1 if solo_activos else 0)
    if search:
        where.append("nombre LIKE %s")
        params.append(f"%{search}%")
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY nombre"
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()


def get_role(role_id: int) -> Optional[Dict[str, Any]]:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM roles_principales WHERE id=%s", (role_id,))
        return cur.fetchone()


def get_by_nombre(nombre: str) -> Optional[Dict[str, Any]]:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM roles_principales WHERE nombre=%s", (nombre,))
        return cur.fetchone()


def create_role(nombre: str) -> int:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO roles_principales (nombre, activo) VALUES (%s, 1)",
            (nombre,),
        )
        return cur.lastrowid


def update_role(role_id: int, nombre: str, activo: bool) -> None:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE roles_principales SET nombre=%s, activo=%s WHERE id=%s",
            (nombre, 1 if activo else 0, role_id),
        )


def delete_role(role_id: int) -> None:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM roles_principales WHERE id=%s", (role_id,))


def list_active_role_names() -> List[str]:
    """Devuelve solo los nombres de roles activos (para selectbox en Personas)."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT nombre FROM roles_principales WHERE activo=1 ORDER BY nombre"
        )
        return [r["nombre"] for r in cur.fetchall()]
