# shared/auth.py
import streamlit as st
from typing import Literal, Optional, Dict, Any

Role = Literal["admin", "viewer"]
SESSION_KEY = "auth_user"

def start_session(user: Dict[str, Any]) -> None:
    st.session_state[SESSION_KEY] = {
        "id": user["id"],
        "email": user["email"],
        "rol": user["rol_app"],
    }

def end_session() -> None:
    if SESSION_KEY in st.session_state:
        del st.session_state[SESSION_KEY]

def current_user() -> Optional[Dict[str, Any]]:
    return st.session_state.get(SESSION_KEY)

def is_authenticated() -> bool:
    return current_user() is not None

def has_role(*roles: Role) -> bool:
    u = current_user()
    if not u:
        return False
    user_role = u.get("rol", "").lower()
    return user_role in [r.lower() for r in roles]

def require_role(*roles: Role, login_page_name: str = "00_Login") -> None:
    if not is_authenticated():
        st.warning("Necesitas iniciar sesión.")
        st.page_link(f"pages/{login_page_name}.py", label="Ir a Login", icon="🔐")
        st.stop()
    if roles and not has_role(*roles):
        st.error("No tienes permisos para ver esta página.")
        st.stop()

def require_authentication() -> None:
    """
    Oculta completamente la página si el usuario no está autenticado.
    Redirige silenciosamente al login.
    """
    if not is_authenticated():
        hide_sidebar()
        st.switch_page("pages/00_Login.py")

def hide_sidebar_when_not_authenticated() -> None:
    """
    Oculta el menú lateral si el usuario no está autenticado.
    Solo debe llamarse desde páginas que requieren autenticación.
    """
    if not is_authenticated():
        hide_sidebar()
        st.switch_page("pages/00_Login.py")

def hide_sidebar() -> None:
    """
    Oculta la barra lateral usando CSS.
    """
    st.markdown(
        """
        <style>
            .css-1d391kg {display: none}
            .st-emotion-cache-6qob1r {display: none}
            section[data-testid="stSidebar"] {display: none}
            .css-17eq0hr {display: none}
            .st-emotion-cache-1cypcdb {display: none}
            .st-emotion-cache-1wbqy5l {display: none}
        </style>
        """, 
        unsafe_allow_html=True
    )
