import os

import instructor
from openai import OpenAI
from pydantic import BaseModel, Field


class CodeGenerationResponse(BaseModel):
    python_code: str = Field(
        description="Código Python limpio y ejecutable, sin bloques markdown"
    )
    explanation: str = Field(
        description="Breve justificación técnica de una sola frase"
    )
    confidence: float = Field(
        ge=0.0, le=1.0, description="Nivel de certeza de la solución"
    )


class LocalLLMEngine:
    def __init__(self, model_name: str = "qwen2.5-coder:3b"):
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.client = instructor.from_openai(
            OpenAI(base_url=f"{base_url}/v1", api_key="ollama"),
            mode=instructor.Mode.JSON,
        )
        self.model_name = model_name

    def generate_structured_code(self, prompt: str) -> CodeGenerationResponse:
        return self.client.chat.completions.create(
            model=self.model_name,
            response_model=CodeGenerationResponse,
            messages=[
                {
                    "role": "system",
                    "content": "Eres un motor de ingeniería de software determinista.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
        )
