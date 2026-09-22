import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "core" / "curt_inventory.db"

def get_connection():
    if DB_PATH.exists():
        return sqlite3.connect(DB_PATH)
    return sqlite3.connect("../core/curt_inventory.db")

def get_part(name):
    with get_connection() as conn:
        result = conn.execute("SELECT * FROM parts WHERE name = ?", (name,))
        return result.fetchone()

def list_by_category(category):
    with get_connection() as conn:
        result = conn.execute("SELECT * FROM parts WHERE category = ?", (category,))
        return result.fetchall()

def get_quantity_of_part(name):
    with get_connection() as conn:
        result = conn.execute("SELECT quantity FROM parts WHERE name = ?", (name,))
        row = result.fetchone()

        if row is None:
            return None

        return row[0]

def get_location_of_part(name):
    with get_connection() as conn:
        result = conn.execute("SELECT location FROM parts WHERE name = ?", (name,))
        row = result.fetchone()

        if row is None:
            return None

        return row[0]

def check_stock(item_name):
    quantity = get_quantity_of_part(item_name)
    location = get_location_of_part(item_name)

    if quantity is None or location is None:
        return {
            "error": f"Item '{item_name}' was not found."
        }

    return {
        "item": item_name,
        "quantity": quantity,
        "location": location
    }

def flag_shortage(item_name):
    quantity = get_quantity_of_part(item_name)

    if quantity is None:
        return {
            "error": f"Item '{item_name}' was not found."
        }

    if quantity < 10:
        print(f"LOW STOCK: {item_name} has only {quantity} units left.")
        return True

    return False

def get_all_parts():
    with get_connection() as conn:
        result = conn.execute("SELECT * FROM parts")
        return result.fetchall()