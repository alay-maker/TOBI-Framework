import subprocess
from typing import Any


def check_encryption_compliance(payload: dict[str, Any]) -> bool:
    """Freno de emergencia si contiene datos sensibles sin cifrar."""
    if payload.get("contains_sensitive_data", False):
        return payload.get("is_encrypted", False) is True
    return True


def validate_python_code_with_ruff(payload: dict[str, Any]) -> bool:
    """Valida sintaxis y calidad de código Python a coste cero usando Ruff."""
    code = payload.get("generated_code")
    if not code:
        return True

    process = subprocess.run(
        ["ruff", "check", "--stdin-filename", "vehicle_output.py", "-"],
        input=code,
        text=True,
        capture_output=True,
        check=False,
    )
    return process.returncode == 0
