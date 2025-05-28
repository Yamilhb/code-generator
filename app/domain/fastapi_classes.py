from pydantic import BaseModel
from fastapi import File, UploadFile, Form

class GenerationRequest(BaseModel):
    prompt: str = Form(...),
    api_key: str = Form(...),
    image_file: UploadFile = File(None)

class GenerationResponse(BaseModel):
    message: str
    download_url: str