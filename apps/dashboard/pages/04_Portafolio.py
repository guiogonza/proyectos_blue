# apps/dashboard/pages/00_📊_Portafolio.py
import streamlit as st
from domain.services import reporting_service
import pandas as pd

# apps/dashboard/pages/00_📊_Portafolio.py
from shared.auth.auth import require_authentication, require_role, is_authenticated, hide_sidebar

# Ocultar sidebar y redirigir si no está autenticado
if not is_authenticated():
    hide_sidebar()
    st.switch_page("pages/00_Login.py")

require_authentication()  # Redirige al login si no está autenticado
require_role("viewer", "admin")  # requiere sesión, cualquier rol


def _money(v: float) -> str:
    try:
        return f"${v:,.0f}"
    except Exception:
        return "-"

def render():
    st.title("📊 Portafolio de Proyectos")

    data = reporting_service.portfolio_overview()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Proyectos (totales)", data["total"])
    c2.metric("Activos", data["activos"])
    c3.metric("Cerrados", data["cerrados"])
    c4.metric("Desv. promedio", f"{data['desv_avg']*100:.1f}% {data['desv_band']}")

    st.markdown("### Estimado vs Real (agregado)")
    colm1, colm2 = st.columns(2)
    colm1.metric("Estimado total", _money(data["estimado_total"]))
    colm2.metric("Real total", _money(data["real_total"]))

    st.markdown("---")
    st.subheader("Tabla de proyectos con semáforo de desviación")
    table = reporting_service.cost_table()
    if table:
        df = pd.DataFrame(table)
        # Columnas formateadas
        df["estimado"] = df["estimado"].apply(_money)
        df["real"] = df["real"].apply(lambda x: "-" if x is None else _money(x))
        df["desviacion_pct"] = df["desviacion_pct"].apply(lambda x: f"{x*100:.1f}%")
        st.dataframe(df[["id","nombre","cliente","estado","estimado","real","desviacion_pct","semaforo"]],
                     use_container_width=True, hide_index=True)
    else:
        st.info("No hay proyectos cargados.")

    st.markdown("---")
    st.subheader("Top personas por carga activa")
    top = reporting_service.top_carga_personas(limit=10)
    if top:
        dfp = pd.DataFrame(top)
        st.dataframe(dfp, use_container_width=True, hide_index=True)
    else:
        st.info("No hay asignaciones activas.")

def main():
    render()

if __name__ == "__main__":
    main()
