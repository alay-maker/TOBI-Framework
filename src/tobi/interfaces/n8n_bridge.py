import json
import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from tobi.core.vehicle import Vehicle
from tobi.tower.blackbox import BlackBox, DrivingSchoolRecord


class ReviewResolution(BaseModel):
    license_plate: str
    reviewer: str = Field(default="human_operator")
    approved: bool
    corrected_code: str = Field(default="")
    feedback_notes: str = Field(default="")


class N8nBridge:
    def __init__(self, shared_dir: str | Path | None = None):
        if shared_dir is None:
            shared_dir = os.getenv(
                "TOBI_N8N_SHARED_PATH",
                os.path.expanduser("~/lab/n8n-stack/shared/tobi-middle-lane"),
            )

        self.base_path = Path(shared_dir)
        self.pending_dir = self.base_path / "pending"
        self.resolved_dir = self.base_path / "resolved"
        self.pending_dir.mkdir(parents=True, exist_ok=True)
        self.resolved_dir.mkdir(parents=True, exist_ok=True)

    def dispatch_for_review(self, vehicle: Vehicle, road_name: str) -> Path:
        """Escribe un ticket JSON en la carpeta compartida con n8n (/data/shared)."""
        ticket_path = self.pending_dir / f"{vehicle.license_plate}.json"
        ticket_data: dict[str, Any] = {
            "license_plate": vehicle.license_plate,
            "road_name": road_name,
            "assigned_lane": vehicle.assigned_lane.value,
            "engine": vehicle.engine,
            "payload": vehicle.payload,
            "output": vehicle.output,
            "audit_log": vehicle.audit_log,
            "container_internal_path": (
                f"/data/shared/tobi-middle-lane/pending/{vehicle.license_plate}.json"
            ),
        }
        ticket_path.write_text(
            json.dumps(ticket_data, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8",
        )
        return ticket_path

    def count_pending_reviews(self) -> int:
        """Devuelve el número de vehículos esperando revisión humana en el Carril Medio."""
        return len(list(self.pending_dir.glob("*.json")))

    def ingest_resolution(
        self,
        resolution: ReviewResolution,
        blackbox: BlackBox | None = None,
    ) -> Path:
        """Procesa la decisión humana, la archiva en resolved/ y la guarda en DuckDB."""
        pending_file = self.pending_dir / f"{resolution.license_plate}.json"
        ai_draft = ""

        if pending_file.exists():
            raw_ticket = json.loads(pending_file.read_text(encoding="utf-8"))
            ai_draft = str(raw_ticket.get("payload", {}).get("generated_code", ""))
            pending_file.unlink()

        resolved_file = self.resolved_dir / f"{resolution.license_plate}.json"
        resolved_file.write_text(
            resolution.model_dump_json(indent=2),
            encoding="utf-8",
        )

        if blackbox is not None:
            blackbox.record_human_feedback(
                DrivingSchoolRecord(
                    license_plate=resolution.license_plate,
                    reviewer=resolution.reviewer,
                    approved=resolution.approved,
                    ai_draft=ai_draft,
                    human_correction=resolution.corrected_code,
                    feedback_notes=resolution.feedback_notes,
                )
            )

        return resolved_file