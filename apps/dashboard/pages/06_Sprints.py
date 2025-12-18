import streamlit as st
from shared.auth.auth import is_authenticated, hide_sidebar, require_authentication, init_auth

# IMPORTANTE: Inicializar autenticación para restaurar sesión desde cookie
init_auth()

# Ocultar sidebar y redirigir si no está autenticado
if not is_authenticated():
    hide_sidebar()
    st.switch_page("pages/00_Login.py")

require_authentication()

from apps.sprints.main import render
render()
