# infra/repositories/parametros_repo.py
from typing import Optional
from infra.db.connection import get_conn

def get_param(clave: str) -> Optional[str]:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT valor FROM parametros WHERE clave=%s", (clave,))
        row = cur.fetchone()
        return row["valor"] if row else None

def get_int(clave: str, default: int) -> int:
    v = get_param(clave)
    try:
        return int(v) if v is not None else default
    except Exception:
        return default

def get_float(clave: str, default: float) -> float:
    v = get_param(clave)
    try:
        return float(v) if v is not None else default
    except Exception:
        return default
