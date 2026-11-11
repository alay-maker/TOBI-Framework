from typing import Any

from mcp.server.fastmcp import FastMCP

from tobi.core.road import Road
from tobi.core.rules import RuleSeverity, TrafficRule
from tobi.core.vehicle import Vehicle
from tobi.engines.heuristics import (
    check_encryption_compliance,
    validate_python_code_with_ruff,
)
from tobi.interfaces.n8n_bridge import N8nBridge, ReviewResolution
from tobi.tower.blackbox import BlackBox
from tobi.tower.error_budget import ErrorBudgetMonitor

mcp = FastMCP("TOBI-Control-Tower")


def build_default_road(
    blackbox: BlackBox | None = None,
    n8n_bridge: N8nBridge | None = None,
) -> Road:
    road = Road(
        name="MCP_Self_Construction_Road",
        blackbox=blackbox or BlackBox(),
        n8n_bridge=n8n_bridge or N8nBridge(),
        error_budget=ErrorBudgetMonitor(max_pending_reviews=10),
    )
    road.add_pre_rule(
        TrafficRule(
            rule_id="SEC-01",
            description="Freno de emergencia ante datos sensibles no cifrados",
            severity=RuleSeverity.BLOCK_TO_SLOW,
            validator=check_encryption_compliance,
        )
    )
    road.add_post_rule(
        TrafficRule(
            rule_id="QUAL-01",
            description="Validación de sintaxis Python con Ruff",
            severity=RuleSeverity.WARN_TO_MIDDLE,
            validator=validate_python_code_with_ruff,
        )
    )
    return road


@mcp.tool()
def dispatch_code_vehicle(prompt: str, run_llm: bool = False) -> dict[str, Any]:
    """Despacha un Vehicle en la carretera gobernada de T.O.B.I. y devuelve su trazabilidad."""
    road = build_default_road()
    vehicle = Vehicle(payload={"prompt": prompt})
    result = road.transit(vehicle, run_llm=run_llm)
    return {
        "license_plate": result.license_plate,
        "assigned_lane": result.assigned_lane.value,
        "output": result.output,
        "audit_log": result.audit_log,
    }


@mcp.tool()
def get_control_tower_status() -> dict[str, Any]:
    """Consulta el estado actual de la Torre de Control, Caja Negra y Error Budget."""
    blackbox = BlackBox()
    bridge = N8nBridge()
    budget = ErrorBudgetMonitor(max_pending_reviews=10)

    df = blackbox.fetch_audit_dataframe()
    status = budget.evaluate_load(bridge.count_pending_reviews())

    return {
        "total_vehicles_audited": df.height,
        "pending_middle_lane_reviews": status.current_pending,
        "error_budget_overloaded": status.is_overloaded,
        "budget_utilization_ratio": status.utilization_ratio,
    }


@mcp.tool()
def submit_driving_school_review(
    license_plate: str,
    approved: bool,
    corrected_code: str = "",
    feedback_notes: str = "",
) -> dict[str, str]:
    """Registra la revisión humana de un vehículo del Carril Medio en La Autoescuela."""
    blackbox = BlackBox()
    bridge = N8nBridge()
    resolution = ReviewResolution(
        license_plate=license_plate,
        approved=approved,
        corrected_code=corrected_code,
        feedback_notes=feedback_notes,
    )
    resolved_path = bridge.ingest_resolution(resolution, blackbox=blackbox)
    return {
        "status": "recorded",
        "license_plate": license_plate,
        "resolved_file": str(resolved_path),
    }


if __name__ == "__main__":
    mcp.run()