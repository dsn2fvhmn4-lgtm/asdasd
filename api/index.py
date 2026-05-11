from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
import httpx
import os
import pandas as pd
import io

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
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Backend is alive"}

@app.post("/api/chat")
@app.post("/chat")
async def chat_proxy(request: ChatRequest):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return JSONResponse(
            status_code=500, 
            content={"detail": "OPENROUTER_API_KEY is not set in Vercel Environment Variables"}
        )

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://vercel.com", # Required by some models
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
@app.post("/generate-excel")
async def generate_excel(request: ExcelRequest):
    try:
        df = pd.DataFrame(request.data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        
        output.seek(0)
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={request.filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Placeholder Auth
@app.post("/api/auth/register")
@app.post("/auth/register")
async def register(data: dict):
    return {"status": "success", "message": "User registered"}

@app.post("/api/auth/login")
@app.post("/auth/login")
async def login(data: dict):
    return {"status": "success", "token": "mock-token"}
