# apps/dashboard/pages/05_🧾_Bitacora.py
import streamlit as st
from shared.auth.auth import require_authentication, require_role, is_authenticated, hide_sidebar

# Ocultar sidebar y redirigir si no está autenticado
if not is_authenticated():
    hide_sidebar()
    st.switch_page("pages/00_Login.py")

require_authentication()  # Redirige al login si no está autenticado
require_role("admin")  # o "viewer","admin" si quieres que todos lo vean

from apps.eventlog.main import render
render()
