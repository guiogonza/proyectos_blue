# apps/dashboard/pages/00_🔐_Login.py
import streamlit as st
from domain.services.auth_service import verify_credentials
from shared.auth.auth import start_session, end_session, is_authenticated, current_user, hide_sidebar, is_session_expired

# Ocultar sidebar si no está autenticado
if not is_authenticated():
    hide_sidebar()

st.title("🔐 Iniciar sesión")

if is_authenticated():
    u = current_user()
    if u:  # Verificar que el usuario no sea None
        st.success(f"Sesión iniciada como **{u['email']}** (rol: {u['rol_app']})")
        st.info("ℹ️ La sesión se mantiene activa por 10 minutos de inactividad. Se renueva automáticamente mientras interactúas con la aplicación.")
    if st.button("Cerrar sesión"):
        end_session()
        st.rerun()
else:
    # Verificar si la sesión expiró
    if is_session_expired() and "session_expired_msg" not in st.session_state:
        st.warning("⏱️ Tu sesión expiró por inactividad. Por favor, inicia sesión nuevamente.")
        st.session_state["session_expired_msg"] = True
    
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Contraseña", type="password")
        ok = st.form_submit_button("Entrar")
        if ok:
            # Limpiar mensaje de sesión expirada
            if "session_expired_msg" in st.session_state:
                del st.session_state["session_expired_msg"]
            
            user = verify_credentials(email.strip(), password)
            if user:
                start_session(user)
                st.success("Bienvenido")
                st.rerun()
            else:
                st.error("Credenciales inválidas o usuario inactivo.")
