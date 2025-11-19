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
    Role
)