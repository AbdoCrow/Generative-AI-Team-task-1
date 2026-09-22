# here is where the ai will understand the user message this is the parser in phase1
# I will have gemini call functions from fastAPI and excecute tools from data_acess.py

from tools import get_part_tool
from tools import flag_shortage_tool
from tools import list_by_category_tool
from tools import check_stock_tool
from data_access import check_stock
from data_access import flag_shortage
from data_access import list_by_category
from data_access import get_part
from google import genai
from dotenv import load_dotenv
from pathlib import Path
import json

ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(ENV_PATH)
load_dotenv()

# this can be done using mcp server but I don't want to add complexity to it
# will make it if I have time
client = genai.Client()

TOOLS = [
    check_stock_tool,
    list_by_category_tool,
    flag_shortage_tool,
    get_part_tool
]

SESSION_STORE: dict[str,str]={}

def ask_gemini(message: str, session_id: str):
    prev_id = SESSION_STORE.get(session_id) if session_id else None

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=message,
        tools=TOOLS,
        previous_interaction_id=prev_id
    )
    
    while interaction.status != "completed":
        if interaction.status != "requires_action":
            break
        for step in interaction.steps:
            if step.type == "function_call":
                if step.name == "check_stock":
                    result = check_stock(step.arguments["item_name"])
                elif step.name == "list_by_category":
                    result = list_by_category(step.arguments["category"])
                elif step.name == "flag_shortage":
                    result = flag_shortage(step.arguments["item_name"])
                elif step.name == "get_part":
                    part = get_part(step.arguments["name"])
                    result = {"part": part} if part else {"error": f"Part '{step.arguments['name']}' not found."}
                else:
                    result = {
                        "error": f"Unknown tool requested: {step.name}"
                    }

                interaction = client.interactions.create(
                    model="gemini-3.6-flash",
                    previous_interaction_id=interaction.id,
                    tools=TOOLS,
                    input=[
                        {
                            "type": "function_result",
                            "name": step.name,
                            "call_id": step.id,
                            "result": [
                                {
                                    "type": "text",
                                    "text": json.dumps(result)
                                }
                            ]
                        }
                    ]
                )

                break

    if session_id:
        SESSION_STORE[session_id] = interaction.id

    return interaction.output_text

if __name__ == "__main__":
    session = "test"
    
    reply1 = ask_gemini("Do we have enough brake discs?", session_id=session)
    print("AI:", reply1)
    
    reply2 = ask_gemini("Where are they?", session_id=session)
    print("AI:", reply2)

