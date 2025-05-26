from pydantic import BaseModel

class GenerationRequest(BaseModel):
    prompt: str
    api_key: str

class GenerationResponse(BaseModel):
    message: str
    download_url: str