from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from pydantic import BaseModel
import httpx
import os
import pandas as pd
import io
import json

app = FastAPI()

# --- Models ---
class ChatRequest(BaseModel):
    message: str
    model: str = "mistralai/mistral-7b-instruct"
    history: list = []

class ExcelRequest(BaseModel):
    data: list
    filename: str = "report.xlsx"

# --- Endpoints ---

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/chat")
async def chat_proxy(request: ChatRequest):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="API Key not configured")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": request.model,
                    "messages": request.history + [{"role": "user", "content": request.message}]
                },
                timeout=30.0
            )
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-excel")
async def generate_excel(request: ExcelRequest):
    try:
        df = pd.DataFrame(request.data)
        
        # Create an in-memory buffer for the Excel file
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
            
            # Formatting (simple example)
            workbook = writer.book
            worksheet = writer.sheets['Sheet1']
            for cell in worksheet["1:1"]:
                cell.font = cell.font.copy(bold=True)

        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.read()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={request.filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Placeholder Auth
@app.post("/api/auth/register")
async def register(data: dict):
    # This will later integrate with Supabase
    return {"status": "success", "message": "Registration successful (Mock)"}

@app.post("/api/auth/login")
async def login(data: dict):
    return {"status": "success", "token": "mock-jwt-token"}
