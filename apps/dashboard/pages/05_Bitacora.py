# apps/dashboard/pages/05_🧾_Bitacora.py
import streamlit as st
st.set_page_config(page_title="Project Ops", page_icon="📊", layout="wide")
from shared.auth.auth import require_authentication, is_authenticated, hide_sidebar, init_auth

# IMPORTANTE: Inicializar autenticación para restaurar sesión desde cookie
init_auth()

# Ocultar sidebar y redirigir si no está autenticado
if not is_authenticated():
    hide_sidebar()
    st.switch_page("pages/00_Login.py")

require_authentication()  # Redirige al login si no está autenticado

from apps.eventlog.main import render
render()
