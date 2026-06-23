# backend.py
from models import (
    add_warehouse_item, update_warehouse_item, delete_warehouse_item, get_warehouse_items,
    add_builderdistributor_item, update_builderdistributor_item, delete_builderdistributor_item, get_builderdistributor_items,
    transfer_stock, delete_transfer_record, get_transfers,
    add_inventory_item, get_inventory_items, update_inventory_item, delete_inventory_item,
    log_transaction, log_cashbook_entry, get_transactions, get_cashbook
)

# --- Warehouse Logic ---
def warehouse_add(name, price_ksh, stock, measurement):
    return add_warehouse_item(name, price_ksh, stock, measurement)

def warehouse_edit(name, updates):
    return update_warehouse_item(name, updates)

def warehouse_delete(name):
    delete_warehouse_item(name)
    return {"status": "deleted", "name": name}

def warehouse_list():
    return get_warehouse_items()

# --- BuilderDistributors Logic ---
def builderdistributor_add(name, price_ksh, stock, measurement):
    return add_builderdistributor_item(name, price_ksh, stock, measurement)

def builderdistributor_edit(name, updates):
    return update_builderdistributor_item(name, updates)

def builderdistributor_delete(name):
    delete_builderdistributor_item(name)
    return {"status": "deleted", "name": name}

def builderdistributor_list():
    return get_builderdistributor_items()

# --- Inventory Logic (retail/wholesale catalog) ---
def inventory_add(name, price_ksh, stock, category, measurement):
    return add_inventory_item(name, price_ksh, stock, category, measurement)

def inventory_list():
    return get_inventory_items()

def inventory_edit(name, updates):
    return update_inventory_item(name, updates)

def inventory_delete(name):
    delete_inventory_item(name)
    return {"status": "deleted", "name": name}

# --- Transfer Logic ---
def transfer_item(name, qty, initiated_by=None):
    return transfer_stock(name, qty, initiated_by=initiated_by)

def transfer_delete(transfer_id):
    delete_transfer_record(transfer_id)
    return {"status": "deleted", "id": transfer_id}

def transfer_list():
    return get_transfers()

# --- Buying Logic ---
def buy_item(user_email, item_name, qty):
    # Find item in inventory (retail/wholesale)
    items = inventory_list()
    item = next((i for i in items if i["name"] == item_name), None)
    if not item:
        return {"error": "Item not found"}
    if item.get("stock", 0) < qty:
        return {"error": "Insufficient stock"}
    # decrement stock
    inventory_edit(item_name, {"stock": item["stock"] - qty})
    cost = item["price_ksh"] * qty
    # log transaction and cashbook
    log_transaction(user_email, f"Bought {qty} x {item_name} ({item.get('measurement')})", cost)
    log_cashbook_entry("Expense", cost, f"Sale of {qty} x {item_name}")
    return {"success": True, "item": item_name, "qty": qty, "cost_ksh": cost}

# --- Reports ---
def recent_transactions(limit=50):
    return get_transactions(limit)

def recent_cashbook(limit=50):
    return get_cashbook(limit)
