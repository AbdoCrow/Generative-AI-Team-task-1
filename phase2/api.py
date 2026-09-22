from pydantic import BaseModel
from data_access import get_all_parts
from fastapi import FastAPI
from llm_service import ask_gemini

app = FastAPI()

class ChatRequest(BaseModel):
    session_id: str
    message: str

@app.get("/inventory")
def get_inventory():
    parts = get_all_parts()
    # for better json not rows 
    return [
        {
            "id": part[0],
            "name": part[1],
            "quantity": part[2],
            "category": part[3],
            "location": part[4]
        }
        for part in parts
    ]

@app.post("/chat")
def get_chat(request: ChatRequest):
    reply = ask_gemini(message=request.message, session_id=request.session_id)
    return {
        "reply": reply
    }