import streamlit as st
from shared.auth.auth import require_role, is_authenticated, hide_sidebar

# Ocultar sidebar y redirigir si no está autenticado
if not is_authenticated():
    hide_sidebar()
    st.switch_page("pages/00_Login.py")

require_role("admin")

from apps.sprints.main import render
render()
