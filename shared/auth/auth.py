# shared/auth.py
import streamlit as st
import extra_streamlit_components as stx
import jwt
from typing import Literal, Optional, Dict, Any, List
from datetime import datetime, timedelta
from shared.config import settings

Role = Literal["admin", "editor", "viewer"]
SESSION_KEY = "auth_user"
SESSION_TIMEOUT_MINUTES = 30  # Aumentado a 30 minutos
COOKIE_NAME = "project_ops_auth"

def get_cookie_manager():
    return stx.CookieManager(key="auth_cookies")

def create_token(user: Dict[str, Any]) -> str:
    payload = {
        "sub": str(user["id"]),
        "email": user["email"],
        "rol_app": user["rol_app"],
        "proyectos": user.get("proyectos", []),
        "exp": datetime.now() + timedelta(days=7)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

def decode_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

def start_session(user: Dict[str, Any]) -> None:
    # Cargar proyectos asignados si no es admin
    proyectos = []
    if user.get("rol_app", "").lower() != "admin":
        from domain.services import usuarios_service
        proyectos = usuarios_service.get_proyectos_usuario(user["id"])
    
    st.session_state[SESSION_KEY] = {
        "id": user["id"],
        "email": user["email"],
        "rol_app": user["rol_app"],
        "proyectos": proyectos,  # Lista de IDs de proyectos asignados
        "last_activity": datetime.now().isoformat(),
    }
    
    # Guardar cookie
    try:
        token = create_token(st.session_state[SESSION_KEY])
        cm = get_cookie_manager()
        cm.set(COOKIE_NAME, token, expires_at=datetime.now() + timedelta(days=7))
    except Exception as e:
        print(f"Error setting cookie: {e}")

def end_session() -> None:
    if SESSION_KEY in st.session_state:
        del st.session_state[SESSION_KEY]
    
    # Borrar cookie
    try:
        cm = get_cookie_manager()
        cm.delete(COOKIE_NAME)
    except Exception as e:
        print(f"Error deleting cookie: {e}")

def renew_session() -> None:
    """Renueva el timestamp de última actividad."""
    if SESSION_KEY in st.session_state:
        st.session_state[SESSION_KEY]["last_activity"] = datetime.now().isoformat()

def is_session_expired() -> bool:
    """Verifica si la sesión ha expirado (más de 30 minutos de inactividad)."""
    if SESSION_KEY not in st.session_state:
        return True
    
    last_activity_str = st.session_state[SESSION_KEY].get("last_activity")
    if not last_activity_str:
        return True
    
    try:
        last_activity = datetime.fromisoformat(last_activity_str)
        time_elapsed = datetime.now() - last_activity
        return time_elapsed > timedelta(minutes=SESSION_TIMEOUT_MINUTES)
    except (ValueError, TypeError):
        return True

def current_user() -> Optional[Dict[str, Any]]:
    # 1. Verificar session_state
    if SESSION_KEY in st.session_state:
        if not is_session_expired():
             renew_session()
             return st.session_state[SESSION_KEY]
    
    # 2. Si no hay sesión válida en memoria, intentar recuperar de cookie
    try:
        cm = get_cookie_manager()
        token = cm.get(COOKIE_NAME)
        
        if token:
            payload = decode_token(token)
            if payload:
                # Restaurar sesión
                user_data = {
                    "id": payload["sub"],
                    "email": payload["email"],
                    "rol_app": payload["rol_app"],
                    "proyectos": payload.get("proyectos", []),
                    "last_activity": datetime.now().isoformat()
                }
                st.session_state[SESSION_KEY] = user_data
                return user_data
    except Exception as e:
        print(f"Error reading cookie: {e}")
            
    return None

def is_authenticated() -> bool:
    return current_user() is not None

def is_admin() -> bool:
    """Verifica si el usuario actual es admin"""
    u = current_user()
    if not u:
        return False
    return u.get("rol_app", "").lower() == "admin"

def is_editor() -> bool:
    """Verifica si el usuario actual es editor"""
    u = current_user()
    if not u:
        return False
    return u.get("rol_app", "").lower() == "editor"

def is_viewer() -> bool:
    """Verifica si el usuario actual es viewer (solo lectura)"""
    u = current_user()
    if not u:
        return False
    return u.get("rol_app", "").lower() == "viewer"

def can_edit() -> bool:
    """Verifica si el usuario puede editar (admin o editor)"""
    u = current_user()
    if not u:
        return False
    role = u.get("rol_app", "").lower()
    return role in ["admin", "editor"]

def get_user_proyectos() -> List[int]:
    """Obtiene la lista de proyectos asignados al usuario actual.
    Si es admin, retorna lista vacía (significa acceso a todos).
    """
    u = current_user()
    if not u:
        return []
    if u.get("rol_app", "").lower() == "admin":
        return []  # Admin ve todo
    return u.get("proyectos", [])

def has_role(*roles: Role) -> bool:
    u = current_user()
    if not u:
        return False
    user_role = u.get("rol_app", "").lower()
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
    Oculta completamente la página si el usuario no está autenticado o la sesión expiró.
    Redirige silenciosamente al login.
    """
    if not is_authenticated():
        end_session()
        hide_sidebar()
        st.switch_page("pages/00_Login.py")

def hide_sidebar_when_not_authenticated() -> None:
    """
    Oculta el menú lateral si el usuario no está autenticado o la sesión expiró.
    Solo debe llamarse desde páginas que requieren autenticación.
    """
    if not is_authenticated():
        end_session()
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
