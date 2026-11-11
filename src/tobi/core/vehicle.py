import uuid
from typing import Any

from pydantic import BaseModel, Field

from tobi.core.rules import Lane


def generate_license_plate() -> str:
    return f"TOBI-{uuid.uuid4().hex[:6].upper()}"


class Vehicle(BaseModel):
    license_plate: str = Field(default_factory=generate_license_plate)
    engine: str = Field(
        default="qwen2.5-coder:3b", description="Modelo de IA o motor asignado"
    )
    payload: dict[str, Any] = Field(description="Datos de entrada y tarea a realizar")
    assigned_lane: Lane = Field(default=Lane.FAST)
    output: dict[str, Any] | None = Field(
        default=None, description="Resultado estructurado"
    )
    audit_log: list[str] = Field(
        default_factory=list, description="Historial de la Caja Negra"
    )

    def log_event(self, message: str) -> None:
        self.audit_log.append(f"[{self.license_plate}] {message}")
