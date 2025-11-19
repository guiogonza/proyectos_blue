# infra/repositories/usuarios_repo.py
from typing import Optional, Dict, Any, List
from infra.db.connection import get_conn

def get_by_email(email: str) -> Optional[Dict[str, Any]]:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM usuarios WHERE email=%s AND activo=1", (email,))
        return cur.fetchone()

def get_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM usuarios WHERE id=%s", (user_id,))
        return cur.fetchone()

def set_last_login(user_id: int) -> None:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("UPDATE usuarios SET ultimo_login=NOW() WHERE id=%s", (user_id,))

def create_user(email: str, hash_password: str, rol_app: str, persona_id: int | None = None, activo: bool = True) -> int:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO usuarios (email, hash_password, rol_app, persona_id, activo) VALUES (%s,%s,%s,%s,%s)",
            (email, hash_password, rol_app, persona_id, 1 if activo else 0)
        )
        return cur.lastrowid

def update_user(user_id: int, email: str, rol_app: str, persona_id: int | None, activo: bool) -> None:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE usuarios SET email=%s, rol_app=%s, persona_id=%s, activo=%s WHERE id=%s",
            (email, rol_app, persona_id, 1 if activo else 0, user_id)
        )

def update_password(user_id: int, hash_password: str) -> None:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("UPDATE usuarios SET hash_password=%s WHERE id=%s", (hash_password, user_id))

def list_users() -> List[Dict[str, Any]]:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id,email,rol_app,persona_id,activo,ultimo_login,created_at FROM usuarios ORDER BY created_at DESC")
        return cur.fetchall()

def delete_user(user_id: int) -> None:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM usuarios WHERE id=%s", (user_id,))
