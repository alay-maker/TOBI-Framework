from collections.abc import Callable
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Lane(str, Enum):
    FAST = "Fast Lane (100% AI)"
    MIDDLE = "Middle Lane (80% AI / 20% Human Copilot)"
    SLOW = "Slow Lane (100% Human)"


class RuleSeverity(str, Enum):
    WARN_TO_MIDDLE = "middle"
    BLOCK_TO_SLOW = "slow"


class TrafficRule(BaseModel):
    rule_id: str = Field(description="Identificador único de la regla")
    description: str = Field(description="Explicación de la política de seguridad o calidad")
    severity: RuleSeverity = Field(default=RuleSeverity.BLOCK_TO_SLOW)
    validator: Callable[[dict[str, Any]], bool] = Field(exclude=True)

    def enforce(self, payload: dict[str, Any]) -> bool:
        """Devuelve True si el vehículo cumple la norma, False si la infringe."""
        try:
            return self.validator(payload)
        except Exception as e: #noqa: BLE001
            print(f"Error en validación de regla {self.rule_id}: {e}")
            return False
