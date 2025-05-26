from fastapi import APIRouter, HTTPException
from app.domain.fastapi_classes import GenerationRequest, GenerationResponse
from app.application.agent.agent import Agent
from app.infraestructure.llm.model import IA
from dotenv import load_dotenv
from pathlib import Path

router = APIRouter()

# dotenv_path = Path(__file__).resolve().parent.parent.parent.parent / '.env'
# load_dotenv(dotenv_path)

prompt_path = Path(__file__).resolve().parent.parent.parent.parent / 'resources/prompts/'

@router.post("/generate_code", response_model=GenerationResponse)
async def generate_code(request: GenerationRequest):

    llm = IA(request.api_key)
    agent = Agent(llm=llm, prompt_path=str(prompt_path))

    result_state = agent.run(descripcion=request.prompt)

    if result_state["process_done"]:
        return GenerationResponse(
            message="Code generated successfully.",
            download_url="/download/project.zip"
        )
    else:
        raise HTTPException(status_code=500, detail="Code generation failed.")
