# apps/dashboard/pages/01_👤_Personas.py
import streamlit as st
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from shared.auth.auth import require_authentication, require_role, is_authenticated, hide_sidebar
from apps.personas.main import render

# Ocultar sidebar y redirigir si no está autenticado
if not is_authenticated():
    hide_sidebar()
    st.switch_page("pages/00_Login.py")

require_authentication()  # Redirige al login si no está autenticado
require_role("admin")

render()
