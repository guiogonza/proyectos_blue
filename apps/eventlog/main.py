# apps/eventlog/main.py
import streamlit as st
import pandas as pd
from infra.repositories import eventlog_repo
from shared.utils.exports import export_csv

def render():
    st.title("🧾 Bitácora de eventos")

    colf1, colf2, colf3 = st.columns([1,1,1])
    with colf1:
        entidad = st.selectbox("Entidad", options=["(Todas)", "personas", "proyectos", "asignaciones", "usuarios"], index=0)
        entidad_val = None if entidad=="(Todas)" else entidad
    with colf2:
        tipo = st.selectbox("Tipo", options=["(Todos)", "create", "update", "delete", "status_change", "end", "close", "login", "logout"], index=0)
        tipo_val = None if tipo=="(Todos)" else tipo
    with colf3:
        limit = st.number_input("Límite", min_value=10, max_value=5000, value=200, step=10)

    rows = eventlog_repo.list_events(entidad_val, tipo_val, int(limit))

    cA, _ = st.columns([1,3])
    with cA:
        if st.button("📤 Exportar CSV"):
            path = export_csv(rows, "event_log")
            st.toast(f"Exportado a {path}", icon="✅")

    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Sin eventos para esos filtros.")
