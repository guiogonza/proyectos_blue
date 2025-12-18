# apps/dashboard/pages/04_🔑_Usuarios.py
import streamlit as st
from shared.auth.auth import require_authentication, require_role, is_authenticated, hide_sidebar, init_auth

# IMPORTANTE: Inicializar autenticación para restaurar sesión desde cookie
init_auth()

# Ocultar sidebar y redirigir si no está autenticado
if not is_authenticated():
    hide_sidebar()
    st.switch_page("pages/00_Login.py")

require_authentication()  # Redirige al login si no está autenticado
require_role("admin")

from apps.usuarios.main import render
render()
