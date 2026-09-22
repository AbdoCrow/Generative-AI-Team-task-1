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

def get_by_category(category):
    with get_connection() as conn:
        result = conn.execute("SELECT * FROM parts WHERE category = ?", (category,))
        return result.fetchall()

# for those next two functions I could use get_part and then access the quantity or location by part[2] and part[4]
# I came to a tradoff not repeating the code or make the code less readable and also I would have to remember which index means what
# I think it's better to repeat a little bit and make the code more readable 

def get_quantity_of_part(name):
    with get_connection() as conn:
        result = conn.execute("SELECT quantity FROM parts WHERE name = ?", (name,))
        return result.fetchone()[0]

def get_location_of_part(name):
    with get_connection() as conn:
        result = conn.execute("SELECT location FROM parts WHERE name = ?", (name,))
        return result.fetchone()[0]