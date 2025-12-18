# shared/auth.py
import streamlit as st
from typing import Literal, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import hashlib

try:
    from streamlit_cookies_manager import EncryptedCookieManager
except ImportError:
    EncryptedCookieManager = None

Role = Literal["admin", "viewer"]
SESSION_KEY = "auth_user"
COOKIE_KEY = "project_ops_session"
SESSION_TIMEOUT_MINUTES = 10

# Inicializar cookie manager (solo una vez)
@st.cache_resource
def get_cookie_manager():
    if EncryptedCookieManager is None:
        return None
    # Usar una clave secreta fija para encriptar cookies
    cookie_password = "project_ops_secret_key_2025"
    return EncryptedCookieManager(
        prefix="project_ops_",
        password=cookie_password
    )

def init_session_from_cookie() -> None:
    """Restaura la sesión desde la cookie si existe y es válida."""
    cookies = get_cookie_manager()
    if cookies is None:
        return
    
    try:
        if not cookies.ready():
            return
    except:
        # Si falla al verificar ready(), continuar sin cookies
        return
    
    # Si ya hay sesión en memory, no hacer nada
    if SESSION_KEY in st.session_state:
        return
    
    # Intentar restaurar desde cookie
    try:
        cookie_data = cookies.get(COOKIE_KEY)
        if cookie_data:
            user_data = json.loads(cookie_data)
            # Verificar expiración
            last_activity = datetime.fromisoformat(user_data.get("last_activity", ""))
            time_elapsed = datetime.now() - last_activity
            
            if time_elapsed <= timedelta(minutes=SESSION_TIMEOUT_MINUTES):
                # Sesión válida, restaurar
                st.session_state[SESSION_KEY] = user_data
                # Renovar timestamp
                renew_session()
                save_session_to_cookie()
    except (json.JSONDecodeError, ValueError, TypeError, KeyError, Exception):
        # Cookie corrupta o error, continuar sin cookies
        pass

def save_session_to_cookie() -> None:
    """Guarda la sesión actual en una cookie."""
    cookies = get_cookie_manager()
    if cookies is None:
        return
    
    try:
        if not cookies.ready():
            return
        
        if SESSION_KEY in st.session_state:
            cookie_data = json.dumps(st.session_state[SESSION_KEY])
            cookies[COOKIE_KEY] = cookie_data
            cookies.save()
    except:
        # Si falla, continuar sin guardar en cookie
        pass

def start_session(user: Dict[str, Any]) -> None:
    st.session_state[SESSION_KEY] = {
        "id": user["id"],
        "email": user["email"],
        "rol_app": user["rol_app"],
        "last_activity": datetime.now().isoformat(),
    }
    save_session_to_cookie()

def end_session() -> None:
    if SESSION_KEY in st.session_state:
        del st.session_state[SESSION_KEY]
    
    # Eliminar cookie
    try:
        cookies = get_cookie_manager()
        if cookies and cookies.ready():
            cookies[COOKIE_KEY] = ""
            cookies.save()
    except:
        # Si falla, continuar
        pass

def renew_session() -> None:
    """Renueva el timestamp de última actividad."""
    if SESSION_KEY in st.session_state:
        st.session_state[SESSION_KEY]["last_activity"] = datetime.now().isoformat()
        save_session_to_cookie()

def is_session_expired() -> bool:
    """Verifica si la sesión ha expirado (más de 10 minutos de inactividad)."""
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
    # Primero intentar restaurar sesión desde cookie
    init_session_from_cookie()
    
    if is_session_expired():
        end_session()
        return None
    
    # Renovar sesión en cada interacción
    renew_session()
    return st.session_state.get(SESSION_KEY)

def is_authenticated() -> bool:
    # Restaurar desde cookie si es necesario
    init_session_from_cookie()
    return current_user() is not None

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
    if is_session_expired() or not is_authenticated():
        end_session()
        hide_sidebar()
        st.switch_page("pages/00_Login.py")

def hide_sidebar_when_not_authenticated() -> None:
    """
    Oculta el menú lateral si el usuario no está autenticado o la sesión expiró.
    Solo debe llamarse desde páginas que requieren autenticación.
    """
    if is_session_expired() or not is_authenticated():
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
