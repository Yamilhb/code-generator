from fastapi import APIRouter, HTTPException, Query,File, UploadFile, Form
from fastapi.responses import JSONResponse, PlainTextResponse, FileResponse
from app.domain.fastapi_classes import GenerationRequest, GenerationResponse
from app.application.agent.agent import Agent
from app.infraestructure.llm.model import IA
from app.infraestructure.file_utils.utils import output_path, list_files_recursively
from pathlib import Path
import logging
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(output_path)

router = APIRouter()

# dotenv_path = Path(__file__).resolve().parent.parent.parent.parent / '.env'
# load_dotenv(dotenv_path)

prompt_path = Path(__file__).resolve().parent.parent.parent.parent / 'resources/prompts/'

@router.post("/generate_code", response_model=GenerationResponse)
#async def generate_code(request: GenerationRequest):
async def generate_code(
    prompt: str = Form(...),
    api_key: str = Form(...),
    model: str = Form(...),
    image_file: UploadFile = File(None)
):
    logger.info("Function router generate_code")


    llm = IA(api_key,model)
    image_bytes = await image_file.read() if image_file else None


    agent = Agent(llm=llm, prompt_path=str(prompt_path), image=image_bytes)

    result_state = agent.run(descripcion=prompt)

    if result_state["process_done"] and ("warning: this action could be dangerous"in result_state["feedback"].lower()):
        return GenerationResponse(
            message="Warning: The request is potentially dangerous. No code has been generated.",
            download_url="/download/project.zip"
        )
    elif result_state["process_done"] and ("request is out of context"in result_state["feedback"].lower()):
        return GenerationResponse(
            message="Warning: The request is out of context. No code has been generated. Please repeat the request.",
            download_url="/download/project.zip"
        )
    elif result_state["process_done"] and ("error in llm"in result_state["feedback"].lower()):
        return GenerationResponse(
            message="Error in LLM! No code has been generated.",
            download_url="/download/project.zip"
        )
    elif result_state["process_done"]:
        return GenerationResponse(
            message="Code generated successfully.",
            download_url="/download/project.zip"
        )
    else:
        raise HTTPException(status_code=500, detail="Code generation failed.")


@router.get("/list_project", response_class=JSONResponse)
async def list_project():
    logger.info("Function router list_project")
    if not OUTPUT_DIR.exists():
        return JSONResponse(content={"error": "No project found."}, status_code=404)
    return JSONResponse(content=list_files_recursively(OUTPUT_DIR))


@router.get("/get_file", response_class=PlainTextResponse)
async def get_file(path: str = Query(..., description="Ruta relativa del archivo dentro del proyecto generado")):
    logger.info("Function router get_file")
    # Armamos la ruta absoluta de forma segura
    base_dir = OUTPUT_DIR.resolve()
    abs_file = (OUTPUT_DIR / path).resolve()

    # Seguridad: solo permitir archivos dentro de OUTPUT_DIR
    if not abs_file.is_relative_to(base_dir):
        return PlainTextResponse("Ruta inválida", status_code=400)
    if not abs_file.is_file():
        return PlainTextResponse("Archivo no encontrado", status_code=404)

    with open(abs_file, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    return content


@router.get("/download/project.zip")
def download_zip():
    logger.info("Function router download_zip")
    base_dir = OUTPUT_DIR.resolve()
    zip_path = Path(base_dir/"project.zip")
    if zip_path.exists():
        return FileResponse(zip_path, filename="project.zip", media_type="application/zip")
    else:
        raise HTTPException(status_code=404, detail="ZIP not found")