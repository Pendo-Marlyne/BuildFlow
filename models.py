# models.py
from datetime import datetime
from bson.objectid import ObjectId
from pymongo.errors import DuplicateKeyError
from db import (
    get_users_collection,
    get_inventory_collection,
    get_warehouse_collection,
    get_builderdistributors_collection,
    get_transfers_collection,
    get_transactions_collection,
    get_cashbooks_collection
)

# --- Helpers ---
def _now_iso():
    return datetime.utcnow().isoformat()

def _to_int(value, field_name="value"):
    try:
        return int(value)
    except Exception:
        raise ValueError(f"{field_name} must be an integer")

# --- Users ---
def add_user(fullname: str, email: str, password_hash: str, role: str = "Customer"):
    users = get_users_collection()
    doc = {
        "fullname": fullname,
        "email": email.lower(),
        "password": password_hash,
        "role": role,
        "created_at": _now_iso()
    }
    try:
        users.insert_one(doc)
    except DuplicateKeyError:
        raise ValueError("Email already exists")
    doc.pop("password", None)
    return doc

def get_user_by_email(email: str):
    return get_users_collection().find_one({"email": email.lower()})

def update_user(email: str, updates: dict):
    if "email" in updates:
        updates["email"] = updates["email"].lower()
    get_users_collection().update_one({"email": email.lower()}, {"$set": updates})
    user = get_user_by_email(updates.get("email", email))
    if user:
        user.pop("password", None)
    return user

# --- Inventory (catalog: retail / wholesale) ---
def add_inventory_item(name: str, price_ksh, stock, category: str, measurement: str):
    col = get_inventory_collection()
    if category not in ("retail", "wholesale"):
        raise ValueError("category must be 'retail' or 'wholesale'")
    price = _to_int(price_ksh, "price_ksh")
    stock = _to_int(stock, "stock")
    doc = {
        "name": name,
        "price_ksh": price,
        "stock": stock,
        "category": category,
        "measurement": measurement,
        "created_at": _now_iso()
    }
    try:
        col.insert_one(doc)
    except DuplicateKeyError:
        raise ValueError("Inventory item with this name already exists")
    return doc

def get_inventory_items():
    return list(get_inventory_collection().find())

def get_inventory_item_by_name(name: str):
    return get_inventory_collection().find_one({"name": name})

def update_inventory_item(name: str, updates: dict):
    if "price_ksh" in updates:
        updates["price_ksh"] = _to_int(updates["price_ksh"], "price_ksh")
    if "stock" in updates:
        updates["stock"] = _to_int(updates["stock"], "stock")
    get_inventory_collection().update_one({"name": name}, {"$set": updates})
    return get_inventory_item_by_name(updates.get("name", name))

def delete_inventory_item(name: str):
    res = get_inventory_collection().delete_one({"name": name})
    return {"deleted_count": res.deleted_count}

# --- Warehouse (incoming stock) ---
def add_warehouse_item(name: str, price_ksh, stock, measurement: str):
    col = get_warehouse_collection()
    price = _to_int(price_ksh, "price_ksh")
    stock = _to_int(stock, "stock")
    doc = {
        "name": name,
        "price_ksh": price,
        "stock": stock,
        "measurement": measurement,
        "created_at": _now_iso()
    }
    try:
        col.insert_one(doc)
    except DuplicateKeyError:
        raise ValueError("Warehouse item with this name already exists")
    return doc

def get_warehouse_items():
    return list(get_warehouse_collection().find())

def get_warehouse_item_by_name(name: str):
    return get_warehouse_collection().find_one({"name": name})

def update_warehouse_item(name: str, updates: dict):
    if "price_ksh" in updates:
        updates["price_ksh"] = _to_int(updates["price_ksh"], "price_ksh")
    if "stock" in updates:
        updates["stock"] = _to_int(updates["stock"], "stock")
    get_warehouse_collection().update_one({"name": name}, {"$set": updates})
    return get_warehouse_item_by_name(updates.get("name", name))

def delete_warehouse_item(name: str):
    res = get_warehouse_collection().delete_one({"name": name})
    return {"deleted_count": res.deleted_count}

# --- BuilderDistributors (outgoing / retail partners) ---
def add_builderdistributor_item(name: str, price_ksh, stock, measurement: str):
    col = get_builderdistributors_collection()
    price = _to_int(price_ksh, "price_ksh")
    stock = _to_int(stock, "stock")
    doc = {
        "name": name,
        "price_ksh": price,
        "stock": stock,
        "measurement": measurement,
        "created_at": _now_iso()
    }
    try:
        col.insert_one(doc)
    except DuplicateKeyError:
        raise ValueError("BuilderDistributors item with this name already exists")
    return doc

def get_builderdistributor_items():
    return list(get_builderdistributors_collection().find())

def get_builderdistributor_item_by_name(name: str):
    return get_builderdistributors_collection().find_one({"name": name})

def update_builderdistributor_item(name: str, updates: dict):
    if "price_ksh" in updates:
        updates["price_ksh"] = _to_int(updates["price_ksh"], "price_ksh")
    if "stock" in updates:
        updates["stock"] = _to_int(updates["stock"], "stock")
    get_builderdistributors_collection().update_one({"name": name}, {"$set": updates})
    return get_builderdistributor_item_by_name(updates.get("name", name))

def delete_builderdistributor_item(name: str):
    res = get_builderdistributors_collection().delete_one({"name": name})
    return {"deleted_count": res.deleted_count}

# --- Transfers (warehouse -> builderdistributors) ---
def transfer_stock(name: str, qty, initiated_by: str = None):
    qty = _to_int(qty, "qty")
    wh_col = get_warehouse_collection()
    bd_col = get_builderdistributors_collection()
    tr_col = get_transfers_collection()

    wh = wh_col.find_one({"name": name})
    if not wh:
        raise ValueError("Item not found in warehouse")
    if wh.get("stock", 0) < qty:
        raise ValueError("Insufficient warehouse stock")

    # decrement warehouse
    wh_col.update_one({"name": name}, {"$inc": {"stock": -qty}})

    # increment or create builderdistributor record
    bd = bd_col.find_one({"name": name})
    if bd:
        bd_col.update_one({"name": name}, {"$inc": {"stock": qty}})
    else:
        bd_doc = {
            "name": name,
            "price_ksh": wh["price_ksh"],
            "stock": qty,
            "measurement": wh.get("measurement"),
            "created_at": _now_iso()
        }
        bd_col.insert_one(bd_doc)

    # log transfer
    transfer_doc = {
        "name": name,
        "qty": qty,
        "initiated_by": initiated_by,
        "date": _now_iso()
    }
    tr_col.insert_one(transfer_doc)
    return transfer_doc

def get_transfers():
    return list(get_transfers_collection().find())

def delete_transfer_record(transfer_id: str):
    try:
        oid = ObjectId(transfer_id)
    except Exception:
        raise ValueError("Invalid transfer id")
    res = get_transfers_collection().delete_one({"_id": oid})
    return {"deleted_count": res.deleted_count}

# --- Transactions & Cashbook (financial traceability) ---
def log_transaction(user_email: str, message: str, amount):
    amount = _to_int(amount, "amount")
    doc = {
        "user_email": user_email.lower() if user_email else None,
        "message": message,
        "amount": amount,
        "date": _now_iso()
    }
    get_transactions_collection().insert_one(doc)
    return doc

def get_transactions(limit: int = 50):
    return list(get_transactions_collection().find().sort("date", -1).limit(_to_int(limit, "limit")))

def log_cashbook_entry(entry_type: str, amount, note: str):
    if entry_type not in ("Income", "Expense", "income", "expense"):
        raise ValueError("entry_type must be 'Income' or 'Expense'")
    amount = _to_int(amount, "amount")
    doc = {
        "type": entry_type.title(),
        "amount": amount,
        "note": note,
        "date": _now_iso()
    }
    get_cashbooks_collection().insert_one(doc)
    return doc

def get_cashbook(limit: int = 50):
    return list(get_cashbooks_collection().find().sort("date", -1).limit(_to_int(limit, "limit")))
