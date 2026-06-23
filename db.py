# db.py
import os
from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING
from pymongo.errors import ServerSelectionTimeoutError

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise RuntimeError("MONGO_URI not found in .env")

# Connect quickly so startup fails fast if Atlas is unreachable
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000)
try:
    client.admin.command("ping")
except ServerSelectionTimeoutError as e:
    raise RuntimeError("Cannot connect to MongoDB Atlas. Check MONGO_URI and network access.") from e

db = client["construction_investment_db"]

# Single source of truth for collection objects (consistent names)
COLLECTIONS = {
    "users": db["users"],
    "inventory": db["inventory"],
    "warehouse": db["warehouse"],
    "builderdistributors": db["builderdistributors"],
    "transactions": db["transactions"],
    "cashbooks": db["cashbooks"],
    "transfers": db["transfers"],
}

# Simple getters
def get_collection(name: str):
    return COLLECTIONS[name]

def get_users_collection():
    return COLLECTIONS["users"]

def get_inventory_collection():
    return COLLECTIONS["inventory"]

def get_warehouse_collection():
    return COLLECTIONS["warehouse"]

def get_builderdistributors_collection():
    return COLLECTIONS["builderdistributors"]

def get_transactions_collection():
    return COLLECTIONS["transactions"]

def get_cashbooks_collection():
    return COLLECTIONS["cashbooks"]

def get_transfers_collection():
    return COLLECTIONS["transfers"]

# Create essential indexes (idempotent)
def ensure_indexes():
    # users: unique email
    get_users_collection().create_index([("email", ASCENDING)], unique=True, name="idx_users_email")

    # fast lookups by name and uniqueness for product collections
    get_inventory_collection().create_index([("name", ASCENDING)], unique=True, name="idx_inventory_name")
    get_warehouse_collection().create_index([("name", ASCENDING)], unique=True, name="idx_warehouse_name")
    get_builderdistributors_collection().create_index([("name", ASCENDING)], unique=True, name="idx_bd_name")

    # recent queries
    get_transactions_collection().create_index([("date", ASCENDING)], name="idx_transactions_date")
    get_cashbooks_collection().create_index([("date", ASCENDING)], name="idx_cashbooks_date")

