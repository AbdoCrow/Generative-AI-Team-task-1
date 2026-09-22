get_part_tool = {
    "type": "function",
    "name": "get_part",
    "description": "Retrieves the complete inventory record for a specific part.",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "The exact name of the inventory part."
            }
        },
        "required": ["name"]
    }
}
check_stock_tool = {
    "type": "function",
    "name": "check_stock",
    "description": "Checks the current quantity and storage location of an inventory item.",
    "parameters": {
        "type": "object",
        "properties": {
            "item_name": {
                "type": "string",
                "description": "The exact name of the inventory item."
            }
        },
        "required": ["item_name"]
    }
}
list_by_category_tool = {
    "type": "function",
    "name": "list_by_category",
    "description": "Lists all inventory items belonging to a category.",
    "parameters": {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "description": "The inventory category."
            }
        },
        "required": ["category"]
    }
}
flag_shortage_tool = {
    "type": "function",
    "name": "flag_shortage",
    "description": "Checks whether an inventory item has low stock and logs a shortage if its quantity is below the threshold.",
    "parameters": {
        "type": "object",
        "properties": {
            "item_name": {
                "type": "string",
                "description": "The exact name of the inventory item."
            }
        },
        "required": ["item_name"]
    }
}