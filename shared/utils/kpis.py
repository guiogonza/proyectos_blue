'''Cálculo de desviaciones y semáforos (placeholder)'''
# shared/utils/kpis.py
from typing import Optional

def safe_pct(numerador: float, denominador: float) -> float:
    if denominador is None or denominador == 0:
        return 0.0
    return float(numerador) / float(denominador) * 100.0

def desviacion_pct(real: Optional[float], estimado: Optional[float]) -> float:
    """ +% si real > estimado, -% si real < estimado; 0 si falta dato. """
    if real is None or estimado is None or estimado == 0:
        return 0.0
    return (float(real) - float(estimado)) / float(estimado)

def desviacion_band(desv: float, amber: float = 0.10, red: float = 0.20) -> str:
    """devuelve '🟢', '🟡', '🔴' según thresholds positivos de sobrecosto"""
    if desv >= red:
        return "🔴"
    if desv >= amber:
        return "🟡"
    return "🟢"
