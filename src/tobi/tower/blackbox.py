import json
import os
from pathlib import Path

import duckdb
import polars as pl
from pydantic import BaseModel

from tobi.core.vehicle import Vehicle


class AuditRecord(BaseModel):
    license_plate: str
    road_name: str
    assigned_lane: str
    engine: str
    payload_json: str
    output_json: str
    audit_log: str


class DrivingSchoolRecord(BaseModel):
    license_plate: str
    reviewer: str
    approved: bool
    ai_draft: str
    human_correction: str
    feedback_notes: str


class BlackBox:
    def __init__(self, db_path: str | Path | None = None):
        if db_path is None:
            storage_dir = os.getenv(
                "TOBI_STORAGE_PATH",
                os.path.expanduser("~/storage/tobi-data"),
            )
            Path(storage_dir).mkdir(parents=True, exist_ok=True)
            db_path = Path(storage_dir) / "tobi_blackbox.duckdb"

        self.db_path = str(db_path)
        self._init_db()

    def _init_db(self) -> None:
        """Inicializa las tablas vehicles_audit y driving_school en DuckDB."""
        with duckdb.connect(self.db_path) as con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS vehicles_audit (
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    license_plate VARCHAR,
                    road_name VARCHAR,
                    assigned_lane VARCHAR,
                    engine VARCHAR,
                    payload_json TEXT,
                    output_json TEXT,
                    audit_log TEXT
                )
                """
            )
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS driving_school (
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    license_plate VARCHAR,
                    reviewer VARCHAR,
                    approved BOOLEAN,
                    ai_draft TEXT,
                    human_correction TEXT,
                    feedback_notes TEXT
                )
                """
            )

    def record_transit(self, vehicle: Vehicle, road_name: str = "default_road") -> None:
        """Persiste el viaje del vehículo en la Caja Negra local."""
        record = AuditRecord(
            license_plate=vehicle.license_plate,
            road_name=road_name,
            assigned_lane=vehicle.assigned_lane.value,
            engine=vehicle.engine,
            payload_json=json.dumps(vehicle.payload, ensure_ascii=False, default=str),
            output_json=json.dumps(vehicle.output, ensure_ascii=False, default=str)
            if vehicle.output
            else "null",
            audit_log=" | ".join(vehicle.audit_log),
        )

        with duckdb.connect(self.db_path) as con:
            con.execute(
                """
                INSERT INTO vehicles_audit (
                    license_plate,
                    road_name,
                    assigned_lane,
                    engine,
                    payload_json,
                    output_json,
                    audit_log
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    record.license_plate,
                    record.road_name,
                    record.assigned_lane,
                    record.engine,
                    record.payload_json,
                    record.output_json,
                    record.audit_log,
                ],
            )

    def record_human_feedback(self, record: DrivingSchoolRecord) -> None:
        """Registra la auditoría humana de La Autoescuela en DuckDB."""
        with duckdb.connect(self.db_path) as con:
            con.execute(
                """
                INSERT INTO driving_school (
                    license_plate,
                    reviewer,
                    approved,
                    ai_draft,
                    human_correction,
                    feedback_notes
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    record.license_plate,
                    record.reviewer,
                    record.approved,
                    record.ai_draft,
                    record.human_correction,
                    record.feedback_notes,
                ],
            )

    def fetch_audit_dataframe(self) -> pl.DataFrame:
        """Devuelve el historial de tráfico como un DataFrame de Polars vía Apache Arrow."""
        with duckdb.connect(self.db_path) as con:
            return con.sql("SELECT * FROM vehicles_audit").pl()

    def fetch_driving_school_dataframe(self) -> pl.DataFrame:
        """Devuelve las correcciones humanas registradas como un DataFrame de Polars."""
        with duckdb.connect(self.db_path) as con:
            return con.sql("SELECT * FROM driving_school").pl()
