
import bcrypt
from typing import Optional, Tuple

from models import add_user, get_user_by_email, update_user

def hash_password(plain_password: str) -> str:
    """Return bcrypt hash (utf-8 string) for a plain password."""
    if not plain_password:
        raise ValueError("Password cannot be empty")
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed: str) -> bool:
    """Verify plain password against stored bcrypt hash."""
    if not hashed:
        return False
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed.encode("utf-8"))


# -----------------------
# Public auth API
# -----------------------
def register_user(fullname: str, email: str, password: str, role: str = "Customer") -> dict:
    """
    Register a new user.
    Returns the created user document (without password).
    Raises ValueError on validation or duplicate email.
    """
    if not fullname or not email or not password:
        raise ValueError("fullname, email and password are required")
    email = email.strip().lower()
    pw_hash = hash_password(password)
    user = add_user(fullname.strip(), email, pw_hash, role.strip() or "Customer")
    # add_user returns a doc without password (models handles removal)
    return user


def login_user(email: str, password: str) -> Optional[dict]:
    """
    Authenticate a user.
    Returns a minimal user dict {fullname, email, role} on success, otherwise None.
    """
    if not email or not password:
        return None
    email = email.strip().lower()
    user = get_user_by_email(email)
    if not user:
        return None
    stored_hash = user.get("password")
    if not stored_hash:
        return None
    if verify_password(password, stored_hash):
        return {"fullname": user.get("fullname"), "email": user.get("email"), "role": user.get("role", "Customer")}
    return None


def change_role(email: str, new_role: str) -> dict:
    """
    Change a user's role. Returns the updated user document (without password).
    Raises ValueError if user not found or invalid input.
    """
    if not email or not new_role:
        raise ValueError("email and new_role are required")
    email = email.strip().lower()
    update_user(email, {"role": new_role.strip()})
    updated = get_user_by_email(email)
    if not updated:
        raise ValueError("User not found after update")
    updated.pop("password", None)
    return updated


# -----------------------
# Optional: simple Tkinter test UI
# -----------------------
if __name__ == "__main__":
    import tkinter as tk
    from tkinter import ttk, messagebox

    def on_register():
        fullname = reg_name.get().strip()
        email = reg_email.get().strip()
        pw = reg_pw.get().strip()
        role = reg_role.get().strip() or "Customer"
        try:
            register_user(fullname, email, pw, role)
            messagebox.showinfo("Success", "Registered successfully")
            reg_name.delete(0, tk.END)
            reg_email.delete(0, tk.END)
            reg_pw.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_login():
        email = login_email.get().strip()
        pw = login_pw.get().strip()
        user = login_user(email, pw)
        if user:
            messagebox.showinfo("Welcome", f"Welcome {user['fullname']} ({user['role']})")
        else:
            messagebox.showerror("Login failed", "Invalid credentials")

    root = tk.Tk()
    root.title("Auth Test")

    nb = ttk.Notebook(root)
    nb.pack(fill="both", expand=True, padx=10, pady=10)

    # Register tab
    reg_frame = ttk.Frame(nb, padding=12)
    ttk.Label(reg_frame, text="Full name").grid(row=0, column=0, sticky="w")
    reg_name = ttk.Entry(reg_frame); reg_name.grid(row=0, column=1, pady=4)
    ttk.Label(reg_frame, text="Email").grid(row=1, column=0, sticky="w")
    reg_email = ttk.Entry(reg_frame); reg_email.grid(row=1, column=1, pady=4)
    ttk.Label(reg_frame, text="Password").grid(row=2, column=0, sticky="w")
    reg_pw = ttk.Entry(reg_frame, show="*"); reg_pw.grid(row=2, column=1, pady=4)
    ttk.Label(reg_frame, text="Role").grid(row=3, column=0, sticky="w")
    reg_role = ttk.Combobox(reg_frame, values=["Admin", "Manager", "Customer"]); reg_role.grid(row=3, column=1, pady=4)
    ttk.Button(reg_frame, text="Register", command=on_register).grid(row=4, column=0, columnspan=2, pady=8)

    # Login tab
    login_frame = ttk.Frame(nb, padding=12)
    ttk.Label(login_frame, text="Email").grid(row=0, column=0, sticky="w")
    login_email = ttk.Entry(login_frame); login_email.grid(row=0, column=1, pady=4)
    ttk.Label(login_frame, text="Password").grid(row=1, column=0, sticky="w")
    login_pw = ttk.Entry(login_frame, show="*"); login_pw.grid(row=1, column=1, pady=4)
    ttk.Button(login_frame, text="Login", command=on_login).grid(row=2, column=0, columnspan=2, pady=8)

    nb.add(reg_frame, text="Register")
    nb.add(login_frame, text="Login")

    root.mainloop()
