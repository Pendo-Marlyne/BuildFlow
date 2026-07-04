import hashlib
from models import add_user, get_user_by_email, update_user

# --- Helpers ---
def _hash_password(password: str) -> str:
    """Hash a password using SHA256 for storage."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def _verify_password(stored_hash: str, password: str) -> bool:
    """Verify a password against its stored hash."""
    return stored_hash == _hash_password(password)

# --- Registration ---
def register_user(fullname: str, email: str, password: str, role: str = "Customer"):
    """Register a new user with hashed password."""
    password_hash = _hash_password(password)
    return add_user(fullname, email, password_hash, role)

# --- Login ---
def login_user(email: str, password: str):
    """Authenticate user by email and password."""
    user = get_user_by_email(email)
    if not user:
        return None
    stored_hash = user.get("password")
    if stored_hash and _verify_password(stored_hash, password):
        # Remove password before returning
        user.pop("password", None)
        return user
    return None

# --- Role Management ---
def change_role(email: str, new_role: str):
    """Change a user's role (Admin, Manager, Customer)."""
    if new_role not in ("Admin", "Manager", "Customer"):
        raise ValueError("Role must be Admin, Manager, or Customer")
    return update_user(email, {"role": new_role})

