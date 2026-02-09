# apps/dashboard/pages/10_Mapa_Recursos.py
import streamlit as st
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from shared.auth.auth import require_authentication, is_authenticated, hide_sidebar, init_auth
from apps.mapa_recursos.main import render

# IMPORTANTE: Inicializar autenticación para restaurar sesión desde cookie
init_auth()

# Ocultar sidebar y redirigir si no está autenticado
if not is_authenticated():
    hide_sidebar()
    st.switch_page("pages/00_Login.py")

require_authentication()

render()
