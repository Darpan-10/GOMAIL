from fastapi import FastAPI
from google import genai
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from google.genai import types
import json

from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

class GenerateRequest(BaseModel):
    client_name: str
    company_name: str | None = None
    sender_name: str | None = None
    sender_company: str | None = None
    email_type: str
    tone: str
    instruction: str

def build_request(req: GenerateRequest) -> str:
    sender_info = ""
    if req.sender_name:
        sender_info += f"My Name: {req.sender_name}\n"
    if req.sender_company:
        sender_info += f"My Company: {req.sender_company}\n"

    return (
        f"You are a professional email writer with great skills. Generate a {req.tone} {req.email_type} email.\n"
        f"Client name: {req.client_name}\n"
        f"Company: {req.company_name or 'N/A'}\n"
        f"{sender_info}"
        f"Instructions: {req.instruction}\n\n"
        "Return JSON with keys: subject, body, closing. "
        "The closing should be formatted as 'Warmly,\\n{My Name}\\n{My Company}' (using the provided My Name and My Company if available). "
        "Do not add extra commentary."
    )

@app.post("/generate")
def generate(req: GenerateRequest):
    prompt = build_request(req)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.1

        )
    )
    response_text = response.text.strip()
    
   
    if response_text.startswith("```json"):
        response_text = response_text[7:]
    if response_text.startswith("```"):
        response_text = response_text[3:]
    if response_text.endswith("```"):
        response_text = response_text[:-3]
    
    response_text = response_text.strip()
    email_data = json.loads(response_text)
    
    return JSONResponse(content=email_data)


