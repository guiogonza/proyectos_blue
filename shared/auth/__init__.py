# shared/auth/__init__.py
# Auth module initialization

from .auth import (
    require_role,
    require_authentication,
    has_role,
    is_authenticated,
    current_user,
    start_session,
    end_session,
    Role,
    is_admin,
    is_editor,
    is_viewer,
    can_edit,
    get_user_proyectos,
    init_auth
)