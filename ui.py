# ui.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from auth import register_user, login_user, change_role
import backend

# ---------- Helpers ----------
def safe_int(val, default=0):
    try:
        return int(val)
    except Exception:
        return default

# ---------- Main Application ----------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Construction Inventory — Dashboard")
        self.geometry("1000x650")
        self.current_user = None
        self._build_ui()
        self._load_all()

    def _build_ui(self):
        # Top bar
        top = ttk.Frame(self)
        top.pack(side="top", fill="x", padx=10, pady=8)

        self.lbl_user = ttk.Label(top, text="Not logged in")
        self.lbl_user.pack(side="left")

        ttk.Button(top, text="Register", command=self._open_register).pack(side="right", padx=4)
        ttk.Button(top, text="Login", command=self._open_login).pack(side="right", padx=4)
        ttk.Button(top, text="Logout", command=self._logout).pack(side="right", padx=4)

        # Notebook
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=10, pady=10)

        # Inventory tab
        self.tab_inventory = ttk.Frame(self.nb)
        self.nb.add(self.tab_inventory, text="Inventory")
        self.inventory_tree = self._make_tree(self.tab_inventory, ["Name", "Price (KSH)", "Stock", "Category", "Measurement"])
        inv_btns = ttk.Frame(self.tab_inventory); inv_btns.pack(fill="x", pady=6)
        ttk.Button(inv_btns, text="Refresh", command=self.load_inventory).pack(side="left")
        ttk.Button(inv_btns, text="Add Item", command=self._add_inventory_item).pack(side="left", padx=4)
        ttk.Button(inv_btns, text="Buy Item", command=self._buy_item_dialog).pack(side="left", padx=4)
        ttk.Button(inv_btns, text="Promote/Demote User", command=self._open_role_manager).pack(side="right")

        # Warehouse tab
        self.tab_warehouse = ttk.Frame(self.nb)
        self.nb.add(self.tab_warehouse, text="Warehouse")
        self.warehouse_tree = self._make_tree(self.tab_warehouse, ["Name", "Price (KSH)", "Stock", "Measurement"])
        wh_btns = ttk.Frame(self.tab_warehouse); wh_btns.pack(fill="x", pady=6)
        ttk.Button(wh_btns, text="Refresh", command=self.load_warehouse).pack(side="left")
        ttk.Button(wh_btns, text="Add to Warehouse", command=self._add_warehouse_item).pack(side="left", padx=4)
        ttk.Button(wh_btns, text="Transfer to BuilderDistributors", command=self._transfer_dialog).pack(side="left", padx=4)

        # BuilderDistributors tab
        self.tab_bd = ttk.Frame(self.nb)
        self.nb.add(self.tab_bd, text="BuilderDistributors")
        self.bd_tree = self._make_tree(self.tab_bd, ["Name", "Price (KSH)", "Stock", "Measurement"])
        bd_btns = ttk.Frame(self.tab_bd); bd_btns.pack(fill="x", pady=6)
        ttk.Button(bd_btns, text="Refresh", command=self.load_bd).pack(side="left")

        # Transactions tab
        self.tab_tx = ttk.Frame(self.nb)
        self.nb.add(self.tab_tx, text="Transactions")
        self.tx_tree = self._make_tree(self.tab_tx, ["User", "Message", "Amount (KSH)", "Date"])
        ttk.Button(self.tab_tx, text="Refresh", command=self.load_transactions).pack(pady=6)

        # Footer quick actions
        footer = ttk.Frame(self)
        footer.pack(side="bottom", fill="x", padx=10, pady=6)
        ttk.Button(footer, text="Seed Demo Data", command=self._seed_demo).pack(side="left")
        ttk.Button(footer, text="Reload All", command=self._load_all).pack(side="left", padx=6)

    def _make_tree(self, parent, columns):
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True)
        tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=180, anchor="center")
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        return tree

    # ---------- Auth ----------
    def _open_register(self):
        dlg = RegisterDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            fullname, email, pw, role = dlg.result
            try:
                register_user(fullname, email, pw, role)
                messagebox.showinfo("Success", "Registered successfully")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _open_login(self):
        dlg = LoginDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            email, pw = dlg.result
            user = login_user(email, pw)
            if user:
                self.current_user = user
                self.lbl_user.config(text=f"{user['email']} ({user['role']})")
                messagebox.showinfo("Login", "Login successful")
                self._load_all()
            else:
                messagebox.showerror("Login failed", "Invalid credentials")

    def _logout(self):
        self.current_user = None
        self.lbl_user.config(text="Not logged in")
        messagebox.showinfo("Logout", "You have been logged out")
        self._load_all()

    # ---------- Inventory ----------
    def load_inventory(self):
        for r in self.inventory_tree.get_children():
            self.inventory_tree.delete(r)
        items = backend.inventory_list()
        for it in items:
            self.inventory_tree.insert("", "end", values=(it.get("name"), it.get("price_ksh"), it.get("stock"), it.get("category", ""), it.get("measurement", "")))

    def _add_inventory_item(self):
        if not self._is_admin_or_manager():
            messagebox.showwarning("Permission", "Admin or Manager required")
            return
        dlg = ItemDialog(self, title="Add Inventory Item", require_category=True)
        self.wait_window(dlg)
        if dlg.result:
            name, price, stock, category, measurement = dlg.result
            backend.inventory_add(name, price, stock, category, measurement)
            self.load_inventory()
            messagebox.showinfo("Added", f"{name} added to inventory")

    def _buy_item_dialog(self):
        if not self.current_user:
            messagebox.showwarning("Login required", "Please login to buy items")
            return
        name = simpledialog.askstring("Buy", "Item name:")
        if not name:
            return
        qty = simpledialog.askinteger("Quantity", "Quantity:", minvalue=1)
        if not qty:
            return
        res = backend.buy_item(self.current_user["email"], name, qty)
        if res.get("error"):
            messagebox.showerror("Error", res["error"])
        else:
            messagebox.showinfo("Success", f"Bought {qty} x {name} for KSH {res['cost_ksh']}")
            self.load_inventory()
            self.load_transactions()

    # ---------- Warehouse ----------
    def load_warehouse(self):
        for r in self.warehouse_tree.get_children():
            self.warehouse_tree.delete(r)
        items = backend.warehouse_list()
        for it in items:
            self.warehouse_tree.insert("", "end", values=(it.get("name"), it.get("price_ksh"), it.get("stock"), it.get("measurement", "")))

    def _add_warehouse_item(self):
        if not self._is_admin_or_manager():
            messagebox.showwarning("Permission", "Admin or Manager required")
            return
        dlg = ItemDialog(self, title="Add Warehouse Item", require_category=False)
        self.wait_window(dlg)
        if dlg.result:
            name, price, stock, _, measurement = dlg.result
            backend.warehouse_add(name, price, stock, measurement)
            self.load_warehouse()
            messagebox.showinfo("Added", f"{name} added to warehouse")

    def _transfer_dialog(self):
        if not self._is_admin_or_manager():
            messagebox.showwarning("Permission", "Manager or Admin required")
            return
        name = simpledialog.askstring("Transfer", "Item name to transfer:")
        if not name:
            return
        qty = simpledialog.askinteger("Quantity", "Quantity:", minvalue=1)
        if not qty:
            return
        try:
            t = backend.transfer_item(name, qty, initiated_by=(self.current_user or {}).get("email"))
            messagebox.showinfo("Transferred", f"Transferred {qty} x {name}")
            self.load_warehouse()
            self.load_bd()
            self.load_transactions()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------- BuilderDistributors ----------
    def load_bd(self):
        for r in self.bd_tree.get_children():
            self.bd_tree.delete(r)
        items = backend.builderdistributor_list()
        for it in items:
            self.bd_tree.insert("", "end", values=(it.get("name"), it.get("price_ksh"), it.get("stock"), it.get("measurement", "")))

    # ---------- Transactions ----------
    def load_transactions(self):
        for r in self.tx_tree.get_children():
            self.tx_tree.delete(r)
        txs = backend.recent_transactions()
        for t in txs:
            self.tx_tree.insert("", "end", values=(t.get("user_email"), t.get("message"), t.get("amount"), t.get("date")))

    # ---------- Role management ----------
    def _open_role_manager(self):
        if not self._is_admin_or_manager():
            messagebox.showwarning("Permission", "Admin or Manager required")
            return
        email = simpledialog.askstring("Change Role", "User email:")
        if not email:
            return
        new_role = simpledialog.askstring("New Role", "Enter new role (Admin/Manager/Customer):")
        if not new_role:
            return
        try:
            change_role(email, new_role)
            messagebox.showinfo("Success", f"{email} role changed to {new_role}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------- Utilities ----------
    def _is_admin_or_manager(self):
        return self.current_user and self.current_user.get("role") in ("Admin", "Manager")

    def _load_all(self):
        self.load_inventory()
        self.load_warehouse()
        self.load_bd()
        self.load_transactions()

    def _seed_demo(self):
        # lightweight seed for demo purposes only
        try:
            # Example items (KSH, category, measurement)
            demo_items = [
                ("Cement Bag", 750, 200, "retail", "50kg bag"),
                ("Steel Rod 12mm", 1500, 300, "wholesale", "meter"),
                ("Paint Bucket", 2200, 80, "retail", "20 litre"),
                ("Sand (Murram)", 1200, 50, "wholesale", "cubic meter"),
            ]
            for name, price, stock, category, measurement in demo_items:
                try:
                    backend.inventory_add(name, price, stock, category, measurement)
                except Exception:
                    pass
                try:
                    backend.warehouse_add(name, price, stock, measurement)
                except Exception:
                    pass
            messagebox.showinfo("Seed", "Demo items added (if not present)")
            self._load_all()
        except Exception as e:
            messagebox.showerror("Seed error", str(e))

# ---------- Dialogs ----------
class RegisterDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Register")
        self.result = None
        self._build()
        self.grab_set()

    def _build(self):
        frm = ttk.Frame(self, padding=12); frm.pack(fill="both", expand=True)
        ttk.Label(frm, text="Full name").grid(row=0, column=0, sticky="w")
        self.e_name = ttk.Entry(frm); self.e_name.grid(row=0, column=1)
        ttk.Label(frm, text="Email").grid(row=1, column=0, sticky="w")
        self.e_email = ttk.Entry(frm); self.e_email.grid(row=1, column=1)
        ttk.Label(frm, text="Password").grid(row=2, column=0, sticky="w")
        self.e_pw = ttk.Entry(frm, show="*"); self.e_pw.grid(row=2, column=1)
        ttk.Label(frm, text="Role").grid(row=3, column=0, sticky="w")
        self.role_var = tk.StringVar(value="Customer")
        ttk.Combobox(frm, textvariable=self.role_var, values=["Admin","Manager","Customer"]).grid(row=3, column=1)
        ttk.Button(frm, text="Register", command=self._on_register).grid(row=4, column=0, columnspan=2, pady=8)

    def _on_register(self):
        name = self.e_name.get().strip()
        email = self.e_email.get().strip()
        pw = self.e_pw.get().strip()
        role = self.role_var.get().strip() or "Customer"
        if not name or not email or not pw:
            messagebox.showwarning("Missing", "All fields required")
            return
        self.result = (name, email, pw, role)
        self.destroy()

class LoginDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Login")
        self.result = None
        self._build()
        self.grab_set()

    def _build(self):
        frm = ttk.Frame(self, padding=12); frm.pack(fill="both", expand=True)
        ttk.Label(frm, text="Email").grid(row=0, column=0, sticky="w")
        self.e_email = ttk.Entry(frm); self.e_email.grid(row=0, column=1)
        ttk.Label(frm, text="Password").grid(row=1, column=0, sticky="w")
        self.e_pw = ttk.Entry(frm, show="*"); self.e_pw.grid(row=1, column=1)
        ttk.Button(frm, text="Login", command=self._on_login).grid(row=2, column=0, columnspan=2, pady=8)

    def _on_login(self):
        email = self.e_email.get().strip()
        pw = self.e_pw.get().strip()
        if not email or not pw:
            messagebox.showwarning("Missing", "Email and password required")
            return
        self.result = (email, pw)
        self.destroy()

class ItemDialog(tk.Toplevel):
    def __init__(self, parent, title="Item", require_category=False):
        super().__init__(parent)
        self.title(title)
        self.result = None
        self.require_category = require_category
        self._build()
        self.grab_set()

    def _build(self):
        frm = ttk.Frame(self, padding=12); frm.pack(fill="both", expand=True)
        ttk.Label(frm, text="Name").grid(row=0, column=0, sticky="w")
        self.e_name = ttk.Entry(frm); self.e_name.grid(row=0, column=1)
        ttk.Label(frm, text="Price (KSH)").grid(row=1, column=0, sticky="w")
        self.e_price = ttk.Entry(frm); self.e_price.grid(row=1, column=1)
        ttk.Label(frm, text="Stock").grid(row=2, column=0, sticky="w")
        self.e_stock = ttk.Entry(frm); self.e_stock.grid(row=2, column=1)
        if self.require_category:
            ttk.Label(frm, text="Category").grid(row=3, column=0, sticky="w")
            self.e_category = ttk.Combobox(frm, values=["retail","wholesale"]); self.e_category.grid(row=3, column=1)
            row_next = 4
        else:
            self.e_category = None
            row_next = 3
        ttk.Label(frm, text="Measurement").grid(row=row_next, column=0, sticky="w")
        self.e_measure = ttk.Entry(frm); self.e_measure.grid(row=row_next, column=1)
        ttk.Button(frm, text="Save", command=self._on_save).grid(row=row_next+1, column=0, columnspan=2, pady=8)

    def _on_save(self):
        name = self.e_name.get().strip()
        try:
            price = safe_int(self.e_price.get().strip())
            stock = safe_int(self.e_stock.get().strip())
        except Exception:
            messagebox.showwarning("Invalid", "Price and stock must be numbers")
            return
        category = self.e_category.get().strip() if self.e_category else ""
        measurement = self.e_measure.get().strip()
        if not name or not measurement:
            messagebox.showwarning("Missing", "Name and measurement required")
            return
        self.result = (name, price, stock, category, measurement)
        self.destroy()

# ---------- Run ----------
if __name__ == "__main__":
    app = App()
    app.mainloop()

