# apps/dashboard/main.py
import streamlit as st
from shared.auth.auth import (
    is_authenticated, current_user, end_session, 
    hide_sidebar, init_session_from_cookie
)

st.set_page_config(page_title="Project Ops", page_icon="📊", layout="wide")

# Intentar restaurar sesión desde cookie
init_session_from_cookie()

# Ocultar sidebar si no está autenticado
if not is_authenticated():
    hide_sidebar()

st.title("📊 Project Ops")

col1, col2 = st.columns([4,1])
with col2:
    if is_authenticated():
        u = current_user()
        if u:  # Verificar que el usuario no sea None
            st.caption(f"🔓 {u['email']} ({u['rol_app']})")
        if st.button("Cerrar sesión"):
            end_session()
            st.rerun()
    else:
        st.page_link("pages/00_Login.py", label="Iniciar sesión", icon="🔐")

st.info("Usa el menú de la izquierda para navegar: Portafolio, Personas, Proyectos, Asignaciones.")
