from data_access import get_by_category, get_quantity_of_part, get_location_of_part

#I want a way to understand where is the name of the part, where is the category 
# where is the quantity and where is the location
# and what is the question the user is asking

# so type: and item:
# so  maybe I  will have a list of all the avaiable items and string match to get the item and same with type seems good

# the tricky thing is how to know what the user is asking and what he want from the data


# for a real project hardcoding those is not good at all  but for simplicty I did that 
# for a project I will add those to the database and query it 

#I didn't use get_part here as I don't know how to make a good parser without turning this into an nlp model lol
# and it's not needed from the task document given


categories = [
    "Brakes",
    "Suspension",
    "Steering",
    "Drivetrain",
    "Engine"
]

items = [
    "Brake Disc",
    "Brake Pad Set",
    "Wheel Bearing",
    "Tie Rod End",
    "Steering Rack",
    "Control Arm",
    "CV Joint",
    "Drive Shaft",
    "Spark Plug",
    "Oil Filter"
]

LOCATION_KEYWORDS = {"where", "location", "place", "shelf", "rack", "find", "stored"}
QUANTITY_KEYWORDS = {"how many", "quantity", "count", "stock", "left", "available", "units"}
CATEGORY_KEYWORDS = {"list", "show", "items in", "parts in", "category"}

def extract_category(santized_input):
    for category in categories:
        if category.lower() in santized_input:
            return category
    return None


def extract_item(santized_input):
    for item in items:
        if item.lower() in santized_input:
            return item
    return None

def fromater(parts):
    formated_string = ""
    for part in parts:
        formated_string += f"Name: {part[1]}, Quantity: {part[2]}, Location: {part[4]}\n"
    return formated_string
    

def parse_user_input(user_input):
    santized_input = user_input.lower().strip()
    item = extract_item(santized_input)
    category = extract_category(santized_input)

    if any(keyword in santized_input for keyword in QUANTITY_KEYWORDS):
        if item:
            return f"the quantity of {item} is {get_quantity_of_part(item)}"
        elif item == None:
            return "Please specify which part you would like to check the quantity for."
        else:
            return "I can't find the item you're looking for"

    elif any(keyword in santized_input for keyword in LOCATION_KEYWORDS):
        if item:
            return f"the location of {item} is {get_location_of_part(item)}"
        elif item == None:
            return "Please specify which part you would like to check the location for."
        else:
            return "I can't find the item you're looking for"
   
    elif any(keyword in santized_input for keyword in CATEGORY_KEYWORDS):
        if category:
            return f"the items in {category} are \n{fromater(get_by_category(category))}"
        elif category == None:
            return "Please specify which category you would like to check the location for."
        else:
            return "I can't find the category you're looking for"
    else:
        return "sorry I didn't understand the question"
        
        

if __name__ == "__main__":
    print(parse_user_input("where is the brake disc"))
    print(parse_user_input("how many brake discs are there"))
    print(parse_user_input("list all items in the brakes category"))
    print(parse_user_input("what is the brake disc"))

   
    