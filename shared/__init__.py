# shared/__init__.py
# Shared module initialization

# Import auth functions to make them available at the shared level
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
