# infra/repositories/sap_repo.py
from typing import Optional, List, Dict, Any
from infra.db.connection import get_conn


def list_sap_report(anio: Optional[int] = None, mes: Optional[str] = None,
                    id_sap: Optional[str] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
    sql = "SELECT * FROM sap_report"
    where, params = [], []
    if anio:
        where.append("anio=%s")
        params.append(anio)
    if mes:
        where.append("mes=%s")
        params.append(mes)
    if id_sap:
        where.append("id_sap=%s")
        params.append(id_sap)
    if search:
        where.append("(colaborador LIKE %s OR proyecto_sap LIKE %s)")
        like = f"%{search}%"
        params.extend([like, like])
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY anio, mes, id_sap, colaborador"
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, tuple(params))
        return cur.fetchall()


def get_sap_report(record_id: int) -> Optional[Dict[str, Any]]:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM sap_report WHERE id=%s", (record_id,))
        return cur.fetchone()


def create_sap_report(data: Dict[str, Any]) -> int:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO sap_report
               (nro, id_empleado_sap, colaborador, id_sap, proyecto_sap, horas_mes, mes, anio,
                tipo_novedad, tiempo_novedad_hrs, reporte_sap)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (data.get("nro"), data.get("id_empleado_sap"), data["colaborador"],
             data["id_sap"], data["proyecto_sap"], data["horas_mes"], data["mes"], data.get("anio", 2026),
             data.get("tipo_novedad"), data.get("tiempo_novedad_hrs"),
             1 if data.get("reporte_sap", True) else 0)
        )
        return cur.lastrowid


def bulk_upsert(rows: List[Dict[str, Any]]) -> int:
    """Inserta o actualiza masivamente. Retorna cantidad de filas afectadas."""
    if not rows:
        return 0
    sql = """INSERT INTO sap_report
             (nro, id_empleado_sap, colaborador, id_sap, proyecto_sap, horas_mes, mes, anio,
              tipo_novedad, tiempo_novedad_hrs, reporte_sap)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
             ON DUPLICATE KEY UPDATE
              horas_mes=VALUES(horas_mes),
              tipo_novedad=VALUES(tipo_novedad),
              tiempo_novedad_hrs=VALUES(tiempo_novedad_hrs),
              reporte_sap=VALUES(reporte_sap),
              updated_at=CURRENT_TIMESTAMP"""
    values = []
    for r in rows:
        reporte = r.get("reporte_sap", True)
        if isinstance(reporte, str):
            reporte = reporte.upper() == "TRUE"
        values.append((
            r.get("nro"), r.get("id_empleado_sap"), r["colaborador"],
            r["id_sap"], r["proyecto_sap"], r["horas_mes"], r["mes"], r.get("anio", 2026),
            r.get("tipo_novedad") or None, r.get("tiempo_novedad_hrs") or None,
            1 if reporte else 0
        ))
    with get_conn() as conn, conn.cursor() as cur:
        cur.executemany(sql, values)
        return cur.rowcount


def delete_by_anio_mes(anio: int, mes: str) -> int:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM sap_report WHERE anio=%s AND mes=%s", (anio, mes))
        return cur.rowcount


def delete_sap_report(record_id: int) -> None:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM sap_report WHERE id=%s", (record_id,))


def get_distinct_meses(anio: Optional[int] = None) -> List[str]:
    sql = "SELECT DISTINCT mes FROM sap_report"
    params = []
    if anio:
        sql += " WHERE anio=%s"
        params.append(anio)
    sql += " ORDER BY FIELD(mes, 'Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre')"
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, tuple(params))
        return [r["mes"] for r in cur.fetchall()]


def get_distinct_proyectos_sap(anio: Optional[int] = None) -> List[Dict[str, str]]:
    sql = "SELECT DISTINCT id_sap, proyecto_sap FROM sap_report"
    params = []
    if anio:
        sql += " WHERE anio=%s"
        params.append(anio)
    sql += " ORDER BY proyecto_sap"
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, tuple(params))
        return cur.fetchall()


def get_distinct_anios() -> List[int]:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT DISTINCT anio FROM sap_report ORDER BY anio DESC")
        return [r["anio"] for r in cur.fetchall()]
