# domain/services/reporting_service.py
from typing import Dict, Any, List, Tuple
from infra.repositories import proyectos_repo, asignaciones_repo, parametros_repo
from shared.utils.kpis import safe_pct, desviacion_pct, desviacion_band

def _thresholds() -> Tuple[float, float]:
    amber = parametros_repo.get_float("DEVIATION_AMBER", 0.10)
    red   = parametros_repo.get_float("DEVIATION_RED",   0.20)
    return amber, red

def portfolio_overview() -> Dict[str, Any]:
    rows = proyectos_repo.list_proyectos(estado=None, cliente=None, search=None)
    tot = len(rows)
    activos  = sum(1 for r in rows if r["estado"] == "Activo")
    cerrados = sum(1 for r in rows if r["estado"] == "Cerrado")
    suma_est = sum(float(r["costo_estimado_total"] or 0) for r in rows)
    suma_real= sum(float(r["costo_real_total"] or 0)    for r in rows if r["costo_real_total"] is not None)
    amber, red = _thresholds()
    # desviación promedio solo sobre proyectos cerrados con real
    desv_vals = [desviacion_pct(r["costo_real_total"], r["costo_estimado_total"])
                 for r in rows if r["costo_real_total"] is not None and r["costo_estimado_total"]]
    desv_avg = sum(desv_vals)/len(desv_vals) if desv_vals else 0.0
    return {
        "total": tot,
        "activos": activos,
        "cerrados": cerrados,
        "estimado_total": suma_est,
        "real_total": suma_real,
        "desv_avg": desv_avg,
        "desv_band": desviacion_band(desv_avg, amber, red),
        "rows": rows,
        "amber": amber,
        "red": red,
    }

def cost_table() -> List[Dict[str, Any]]:
    """Tabla por proyecto con semáforo de desviación"""
    amber, red = _thresholds()
    rows = proyectos_repo.list_proyectos(estado=None, cliente=None, search=None)
    out = []
    for r in rows:
        est = float(r["costo_estimado_total"] or 0)
        real = float(r["costo_real_total"] or 0) if r["costo_real_total"] is not None else None
        desv = desviacion_pct(real, est) if real is not None else 0.0
        out.append({
            "id": r["id"],
            "nombre": r["nombre"],
            "cliente": r.get("cliente"),
            "estado": r["estado"],
            "estimado": est,
            "real": real,
            "desviacion_pct": desv,
            "semaforo": (desviacion_band(desv, amber, red) if real is not None else "⚪"),
        })
    return out

def top_carga_personas(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Top personas por % de carga activa. Para simplicidad, traemos IDs desde asignaciones y agregamos.
    """
    # No tenemos una vista agregada; iteramos sobre personas con asignaciones activas
    # Consultamos IDs únicos de persona desde asignaciones activas
    active = asignaciones_repo.list_asignaciones(persona_id=None, proyecto_id=None, solo_activas=True)
    persona_ids = sorted({r["persona_id"] for r in active})
    res: List[Dict[str, Any]] = []
    for pid in persona_ids:
        total_pct, n_proj = asignaciones_repo.carga_persona(pid)
        res.append({"persona_id": pid, "total_pct": total_pct, "proyectos_activos": n_proj})
    res.sort(key=lambda x: x["total_pct"], reverse=True)
    return res[:limit]
