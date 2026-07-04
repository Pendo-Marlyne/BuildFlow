# ui.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from auth import register_user, login_user, change_role
import backend

def safe_int(val, default=0):
    try:
        return int(val)
    except Exception:
        return default

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Construction Inventory — Dashboard")
        self.geometry("1200x750")
        self.configure(bg="#f0f4f7")
        self.current_user = None
        self.style_ui()
        self._build_ui()
        self._load_all()

    def style_ui(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Segoe UI Semibold", 11),
                        background="#0078D7", foreground="white")
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=28,
                        background="#f9fbfc", fieldbackground="#f9fbfc")
        style.map("Treeview", background=[("selected", "#cce5ff")])
        style.configure("Accent.TButton", font=("Segoe UI Semibold", 10),
                        background="#0078D7", foreground="white")

    def _build_ui(self):
        # Top bar
        top = ttk.Frame(self)
        top.pack(side="top", fill="x", padx=10, pady=8)

        self.lbl_user = ttk.Label(top, text="Not logged in")
        self.lbl_user.pack(side="left")

        ttk.Button(top, text="Register", style="Accent.TButton",
                   command=self._open_register).pack(side="right", padx=4)
        ttk.Button(top, text="Login", style="Accent.TButton",
                   command=self._open_login).pack(side="right", padx=4)
        ttk.Button(top, text="Logout", style="Accent.TButton",
                   command=self._logout).pack(side="right", padx=4)

        # Notebook
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=10, pady=10)

        # Inventory tab
        self.tab_inventory = ttk.Frame(self.nb)
        self.nb.add(self.tab_inventory, text="Inventory")
        self.inventory_tree = self._make_tree(self.tab_inventory,
            ["Name", "Price (KSH)", "Stock", "Category", "Measurement", "Total Value"])
        inv_btns = ttk.Frame(self.tab_inventory); inv_btns.pack(fill="x", pady=6)
        ttk.Button(inv_btns, text="Refresh", style="Accent.TButton",
                   command=self.load_inventory).pack(side="left", padx=4)
        ttk.Button(inv_btns, text="Add Item", style="Accent.TButton",
                   command=self._add_inventory_item).pack(side="left", padx=4)
        ttk.Button(inv_btns, text="Edit Item", style="Accent.TButton",
                   command=self._edit_inventory_item).pack(side="left", padx=4)
        ttk.Button(inv_btns, text="Delete Item", style="Accent.TButton",
                   command=self._delete_inventory_item).pack(side="left", padx=4)
        ttk.Button(inv_btns, text="Buy Item", style="Accent.TButton",
                   command=self._buy_item_dialog).pack(side="left", padx=4)
        ttk.Button(inv_btns, text="Promote/Demote User", style="Accent.TButton",
                   command=self._open_role_manager).pack(side="right", padx=4)

        # Warehouse tab
        self.tab_warehouse = ttk.Frame(self.nb)
        self.nb.add(self.tab_warehouse, text="Warehouse")
        self.warehouse_tree = self._make_tree(self.tab_warehouse,
            ["Name", "Price (KSH)", "Stock", "Measurement"])
        wh_btns = ttk.Frame(self.tab_warehouse); wh_btns.pack(fill="x", pady=6)
        ttk.Button(wh_btns, text="Refresh", style="Accent.TButton",
                   command=self.load_warehouse).pack(side="left", padx=4)
        ttk.Button(wh_btns, text="Add to Warehouse", style="Accent.TButton",
                   command=self._add_warehouse_item).pack(side="left", padx=4)
        ttk.Button(wh_btns, text="Edit Warehouse Item", style="Accent.TButton",
                   command=self._edit_warehouse_item).pack(side="left", padx=4)
        ttk.Button(wh_btns, text="Delete Warehouse Item", style="Accent.TButton",
                   command=self._delete_warehouse_item).pack(side="left", padx=4)
        ttk.Button(wh_btns, text="Transfer to BuilderDistributors", style="Accent.TButton",
                   command=self._transfer_dialog).pack(side="left", padx=4)

        # BuilderDistributors tab
        self.tab_bd = ttk.Frame(self.nb)
        self.nb.add(self.tab_bd, text="BuilderDistributors")
        self.bd_tree = self._make_tree(self.tab_bd,
            ["Name", "Price (KSH)", "Stock", "Measurement"])
        bd_btns = ttk.Frame(self.tab_bd); bd_btns.pack(fill="x", pady=6)
        ttk.Button(bd_btns, text="Refresh", style="Accent.TButton",
                   command=self.load_bd).pack(side="left", padx=4)
        ttk.Button(bd_btns, text="Edit BD Item", style="Accent.TButton",
                   command=self._edit_bd_item).pack(side="left", padx=4)
        ttk.Button(bd_btns, text="Delete BD Item", style="Accent.TButton",
                   command=self._delete_bd_item).pack(side="left", padx=4)

        # Transactions tab
        self.tab_tx = ttk.Frame(self.nb)
        self.nb.add(self.tab_tx, text="Transactions")
        self.tx_tree = self._make_tree(self.tab_tx,
            ["ID", "User", "Message", "Amount (KSH)", "Date"])
        tx_btns = ttk.Frame(self.tab_tx); tx_btns.pack(fill="x", pady=6)
        ttk.Button(tx_btns, text="Refresh", style="Accent.TButton",
                   command=self.load_transactions).pack(side="left", padx=4)
        ttk.Button(tx_btns, text="Add Transaction", style="Accent.TButton",
                   command=self._add_transaction).pack(side="left", padx=4)
        ttk.Button(tx_btns, text="Edit Transaction", style="Accent.TButton",
                   command=self._edit_transaction).pack(side="left", padx=4)
        ttk.Button(tx_btns, text="Delete Transaction", style="Accent.TButton",
                   command=self._delete_transaction).pack(side="left", padx=4)

        # Footer quick actions
        footer = ttk.Frame(self)
        footer.pack(side="bottom", fill="x", padx=10, pady=6)
        ttk.Button(footer, text="Seed Demo Data", style="Accent.TButton",
                   command=self._seed_demo).pack(side="left", padx=4)
        ttk.Button(footer, text="Reload All", style="Accent.TButton",
                   command=self._load_all).pack(side="left", padx=4)

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
            total_value = it.get("price_ksh",0) * it.get("stock",0)
            self.inventory_tree.insert("", "end",
                values=(it.get("name"), it.get("price_ksh"), it.get("stock"),
                        it.get("category"), it.get("measurement"), total_value))