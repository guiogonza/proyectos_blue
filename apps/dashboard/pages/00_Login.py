# apps/dashboard/pages/00_🔐_Login.py
import streamlit as st
st.set_page_config(page_title="Project Ops", page_icon="📊", layout="wide")
from domain.services.auth_service import verify_credentials
from shared.auth.auth import (
    start_session, end_session, is_authenticated, 
    current_user, hide_sidebar, init_auth
)

# IMPORTANTE: Inicializar autenticación para restaurar sesión desde cookie
init_auth()

# Ocultar sidebar si no está autenticado
if not is_authenticated():
    hide_sidebar()

st.title("🔐 Iniciar sesión")

if is_authenticated():
    u = current_user()
    if u:  # Verificar que el usuario no sea None
        st.success(f"Sesión iniciada como **{u['email']}** (rol: {u['rol_app']})")
        st.info("ℹ️ Tu sesión se mantiene activa mientras navegas por la aplicación. Se renovará automáticamente con cada interacción. Por seguridad, cierra sesión cuando termines.")
    if st.button("Cerrar sesión"):
        end_session()
        st.rerun()
else:
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Contraseña", type="password")
        ok = st.form_submit_button("Entrar")
        if ok:            
            user = verify_credentials(email.strip(), password)
            if user:
                start_session(user)
                st.success("Bienvenido")
                st.rerun()
            else:
                st.error("Credenciales inválidas o usuario inactivo.")
