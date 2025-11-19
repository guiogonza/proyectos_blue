import bcrypt
from typing import Optional, Dict, Any
from infra.repositories import usuarios_repo

def verify_credentials(email: str, password: str) -> Optional[Dict[str, Any]]:
    user = usuarios_repo.get_by_email(email)
    if not user:
        return None
    hp_raw = user.get("hash_password")
    if not hp_raw:
        return None
    hp = str(hp_raw).strip().encode()  # ← strip defensivo
    if bcrypt.checkpw(password.encode(), hp):
        usuarios_repo.set_last_login(user["id"])
        return user
    return None
