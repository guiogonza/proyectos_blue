# apps/dashboard/pages/03_🔗_Asignaciones.py
import streamlit as st
st.set_page_config(page_title="Project Ops", page_icon="📊", layout="wide")
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from shared.auth.auth import require_authentication, is_authenticated, hide_sidebar, init_auth
from apps.asignaciones.main import render

# IMPORTANTE: Inicializar autenticación para restaurar sesión desde cookie
init_auth()

# Ocultar sidebar y redirigir si no está autenticado
if not is_authenticated():
    hide_sidebar()
    st.switch_page("pages/00_Login.py")

require_authentication()  # Redirige al login si no está autenticado

render()
