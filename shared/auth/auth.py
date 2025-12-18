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
COOKIE_MANAGER_KEY = "cookie_manager_singleton"

@st.cache_resource
def _get_cookie_manager():
    """
    Singleton del CookieManager usando cache_resource.
    Esto asegura que solo haya una instancia durante toda la sesión.
    """
    return stx.CookieManager()

def get_cookie_manager():
    return _get_cookie_manager()

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
    """
    Inicia sesión guardando en session_state y cookie.
    """
    # Cargar proyectos asignados si no es admin
    proyectos = []
    if user.get("rol_app", "").lower() != "admin":
        from domain.services import usuarios_service
        proyectos = usuarios_service.get_proyectos_usuario(user["id"])
    
    user_data = {
        "id": user["id"],
        "email": user["email"],
        "rol_app": user["rol_app"],
        "proyectos": proyectos,
        "last_activity": datetime.now().isoformat(),
    }
    
    st.session_state[SESSION_KEY] = user_data
    
    # Guardar cookie con JWT
    try:
        token = create_token(user_data)
        cm = get_cookie_manager()
        cm.set(COOKIE_NAME, token, expires_at=datetime.now() + timedelta(days=7))
    except Exception as e:
        print(f"Error setting cookie: {e}")

def end_session() -> None:
    """
    Cierra la sesión eliminando session_state y cookie.
    """
    if SESSION_KEY in st.session_state:
        del st.session_state[SESSION_KEY]
    
    # Marcar que la sesión fue cerrada explícitamente
    st.session_state["_session_ended"] = True
    
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
    """
    Obtiene el usuario actual de la sesión.
    Primero intenta session_state, luego cookie.
    
    IMPORTANTE: El CookieManager necesita renderizarse para leer cookies.
    Por eso usamos cache_resource para mantener una instancia singleton.
    """
    
    # Si la sesión fue cerrada explícitamente en este ciclo, no restaurar
    if st.session_state.get("_session_ended"):
        return None
    
    # 1. Verificar session_state primero (más rápido)
    if SESSION_KEY in st.session_state:
        if not is_session_expired():
            renew_session()
            return st.session_state[SESSION_KEY]
        else:
            # Sesión expirada, limpiar
            del st.session_state[SESSION_KEY]
    
    # 2. Intentar recuperar de cookie
    try:
        cm = get_cookie_manager()
        token = cm.get(COOKIE_NAME)
        
        if token and isinstance(token, str) and len(token) > 10:
            payload = decode_token(token)
            if payload:
                # Restaurar sesión desde cookie
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

def init_auth():
    """
    Inicializa el sistema de autenticación.
    DEBE llamarse al inicio de cada página para que el CookieManager
    pueda leer las cookies correctamente.
    
    Esta función renderiza el CookieManager (necesario para que funcione)
    y restaura la sesión si hay una cookie válida.
    """
    # Forzar la inicialización del CookieManager
    cm = get_cookie_manager()
    
    # Limpiar el flag de sesión terminada si existe de un ciclo anterior
    if "_session_ended" in st.session_state:
        del st.session_state["_session_ended"]
    
    # Intentar restaurar sesión desde cookie si no hay sesión activa
    if SESSION_KEY not in st.session_state:
        try:
            token = cm.get(COOKIE_NAME)
            if token and isinstance(token, str) and len(token) > 10:
                payload = decode_token(token)
                if payload:
                    user_data = {
                        "id": payload["sub"],
                        "email": payload["email"],
                        "rol_app": payload["rol_app"],
                        "proyectos": payload.get("proyectos", []),
                        "last_activity": datetime.now().isoformat()
                    }
                    st.session_state[SESSION_KEY] = user_data
        except Exception as e:
            print(f"Error in init_auth: {e}")

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
