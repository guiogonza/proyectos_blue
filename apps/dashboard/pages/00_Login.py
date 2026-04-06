# apps/dashboard/pages/00_🔐_Login.py
import streamlit as st
st.set_page_config(page_title="Project Ops", page_icon="📊", layout="wide")
from domain.services.auth_service import verify_credentials
from shared.auth.auth import (
    start_session, end_session, is_authenticated, 
    current_user, hide_sidebar, init_auth
)
from shared.config import settings

# IMPORTANTE: Inicializar autenticación para restaurar sesión desde cookie
init_auth()

# Ocultar sidebar si no está autenticado
if not is_authenticated():
    hide_sidebar()

# --- Configuración por país ---
_COUNTRY_INFO = {
    "colombia": {
        "flag_url": "https://flagcdn.com/48x36/co.png",
        "name": "Colombia",
        "tz": "America/Bogota",
    },
    "peru": {
        "flag_url": "https://flagcdn.com/48x36/pe.png",
        "name": "Perú",
        "tz": "America/Lima",
    },
}
_country_key = settings.COUNTRY.lower()
_country = _COUNTRY_INFO.get(
    _country_key,
    {"flag_url": "", "name": _country_key.capitalize(), "tz": ""},
)

# --- Logo + encabezado ---
BLUETAB_LOGO = "https://bluetab.com/wp-content/uploads/2025/10/Bluetab-IBM-Blanco.png"

st.markdown(
    f"""
    <div style='display:flex;align-items:center;justify-content:space-between;margin-bottom:24px;'>
        <div style='display:flex;align-items:center;gap:12px;'>
            <img src='{_country["flag_url"]}' style='height:36px;border:1px solid #444;border-radius:3px;' />
            <span style='font-size:1.2rem;color:#aaa;font-weight:600;'>{_country["name"]}</span>
        </div>
        <img src='{BLUETAB_LOGO}' style='height:40px;' onerror="this.style.display='none'" />
    </div>
    """,
    unsafe_allow_html=True,
)

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
