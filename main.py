from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import edge_tts
import io

app = FastAPI()

# ফ্রন্টএন্ড থেকে কানেকশন নেওয়ার অনুমতি (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TTSRequest(BaseModel):
    text: str
    voice: str = "bn-BD-NabanitaNeural"
    rate: str = "+0%"

# ৩০০+ ভয়েস মডেলের তালিকা পাওয়ার এন্ডপয়েন্ট
@app.get("/voices")
async def get_voices():
    voices = await edge_tts.VoicesManager.create()
    return voices.voices

# টেক্সট থেকে MP3 অডিও ফাইল তৈরি করার এন্ডপয়েন্ট
@app.post("/generate-tts")
async def generate_tts(req: TTSRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="টেক্সট খালি হতে পারবে না")
    
    communicate = edge_tts.Communicate(req.text, req.voice, rate=req.rate)
    
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
            
    return StreamingResponse(
        io.BytesIO(audio_data),
        media_type="audio/mpeg",
        headers={"Content-Disposition": "attachment; filename=generated_voice.mp3"}
    )
