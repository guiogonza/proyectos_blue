# domain/services/sap_service.py
from typing import List, Optional, Dict, Any
from domain.schemas.sap import SapReportItem
from infra.repositories import sap_repo


def listar(anio: Optional[int] = None, mes: Optional[str] = None,
           id_sap: Optional[str] = None, search: Optional[str] = None) -> List[SapReportItem]:
    rows = sap_repo.list_sap_report(anio=anio, mes=mes, id_sap=id_sap, search=search)
    return [SapReportItem(**r) for r in rows]


def obtener(record_id: int) -> Optional[SapReportItem]:
    row = sap_repo.get_sap_report(record_id)
    return SapReportItem(**row) if row else None


def crear(data: Dict[str, Any]) -> int:
    return sap_repo.create_sap_report(data)


def bulk_upsert(rows: List[Dict[str, Any]]) -> int:
    return sap_repo.bulk_upsert(rows)


def eliminar_mes(anio: int, mes: str) -> int:
    return sap_repo.delete_by_anio_mes(anio, mes)


def eliminar(record_id: int) -> None:
    sap_repo.delete_sap_report(record_id)


def get_meses(anio: Optional[int] = None) -> List[str]:
    return sap_repo.get_distinct_meses(anio)


def get_proyectos_sap(anio: Optional[int] = None) -> List[Dict[str, str]]:
    return sap_repo.get_distinct_proyectos_sap(anio)


def get_anios() -> List[int]:
    return sap_repo.get_distinct_anios()


MES_MAP = {
    "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4,
    "Mayo": 5, "Junio": 6, "Julio": 7, "Agosto": 8,
    "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
}


def parse_csv_rows(csv_rows: List[Dict[str, str]], anio: int = 2026) -> List[Dict[str, Any]]:
    """Convierte filas CSV al formato esperado por bulk_upsert."""
    parsed = []
    for r in csv_rows:
        horas = r.get("HORAS MES", "0")
        try:
            horas = float(str(horas).replace(",", ".").strip())
        except (ValueError, TypeError):
            horas = 0

        tiempo_nov = r.get("TIEMPO NOVEDAD (HRS)", "")
        try:
            tiempo_nov = float(str(tiempo_nov).replace(",", ".").strip()) if tiempo_nov else None
        except (ValueError, TypeError):
            tiempo_nov = None

        reporte = r.get("REPORTE SAP", "TRUE")
        if isinstance(reporte, str):
            reporte = reporte.strip().upper() == "TRUE"

        parsed.append({
            "nro": int(r["NRO"]) if r.get("NRO") and str(r["NRO"]).strip().isdigit() else None,
            "id_empleado_sap": str(r.get("ID EMPLEADO SAP", "")).strip() or None,
            "colaborador": str(r.get("COLABORADORES", "")).strip(),
            "id_sap": str(r.get("ID SAP", "")).strip(),
            "proyecto_sap": str(r.get("PROYECTO SAP", "")).strip(),
            "horas_mes": horas,
            "mes": str(r.get("MES", "")).strip(),
            "anio": anio,
            "tipo_novedad": str(r.get("TIPO NOVEDAD", "")).strip() or None,
            "tiempo_novedad_hrs": tiempo_nov,
            "reporte_sap": reporte,
        })
    return parsed
