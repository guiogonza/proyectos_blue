# apps/dashboard/main.py
import streamlit as st
from shared.auth.auth import (
    is_authenticated, current_user, end_session, hide_sidebar, init_auth
)

st.set_page_config(page_title="Project Ops", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

# IMPORTANTE: Inicializar autenticación al inicio para restaurar sesión desde cookie
init_auth()

# Si no está autenticado, redirigir directamente a login
if not is_authenticated():
    hide_sidebar()
    st.switch_page("pages/00_Login.py")

st.title("📊 Project Ops")

col1, col2 = st.columns([4,1])
with col2:
    u = current_user()
    if u:
        st.caption(f"🔓 {u['email']} ({u['rol_app']})")
    if st.button("Cerrar sesión"):
        end_session()
        st.rerun()

st.info("Usa el menú de la izquierda para navegar: Portafolio, Personas, Proyectos, Asignaciones.")
