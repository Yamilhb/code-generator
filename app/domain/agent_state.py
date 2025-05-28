from dataclasses import dataclass, field
from typing import Optional

@dataclass
class AgentState:
    descripcion: str
    image:Optional[str] = None
    n_iterations: int = 0
    generated_code_1: str = ""
    generated_code_2: str = ""
    generated_code_3: str = ""
    feedback: str = ""
    generated_code: str = ""
    process_done: bool = False
    prompt_tokens: int = 0
    completion_tokens: int = 0
    history: list[dict] = field(default_factory=lambda: [{"START": "OK"}])