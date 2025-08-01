# main.py

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from chatbot_api import handle_user_input_with_pelican_support

app = FastAPI()

# CORS settings (allow frontend or any client to call this API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specify frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define a global conversation state dictionary
conversation_state = {
    "awaiting_clarification": False,
    "clarification_type": "",
    "clarification_data": [],
    "original_query": "",
    "original_requested_info": [],
    "original_product": None,
}

# Request model
class ChatQuery(BaseModel):
    query: str

# API route
@app.post("/chat")
def chat_endpoint(payload: ChatQuery):
    user_query = payload.query
    response = handle_user_input_with_pelican_support(user_query, conversation_state)
    return {"response": response}
