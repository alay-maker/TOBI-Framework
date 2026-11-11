from pathlib import Path

from tobi.core.road import Road
from tobi.core.rules import Lane, RuleSeverity, TrafficRule
from tobi.core.vehicle import Vehicle
from tobi.engines.heuristics import validate_python_code_with_ruff
from tobi.interfaces.n8n_bridge import N8nBridge, ReviewResolution
from tobi.tower.blackbox import BlackBox
from tobi.tower.error_budget import ErrorBudgetMonitor


def test_middle_lane_creates_n8n_ticket_and_records_feedback(tmp_path: Path):
    db_file = tmp_path / "test_phase4.duckdb"
    shared_dir = tmp_path / "n8n_shared"

    blackbox = BlackBox(db_path=db_file)
    bridge = N8nBridge(shared_dir=shared_dir)
    road = Road(name="N8N_Road", blackbox=blackbox, n8n_bridge=bridge)
    road.add_post_rule(
        TrafficRule(
            rule_id="QUAL-01",
            description="Ruff check",
            severity=RuleSeverity.WARN_TO_MIDDLE,
            validator=validate_python_code_with_ruff,
        )
    )

    vehicle = Vehicle(payload={"generated_code": "def bad_syntax(:\n    pass"})
    result = road.transit(vehicle, run_llm=False)

    assert result.assigned_lane == Lane.MIDDLE
    assert bridge.count_pending_reviews() == 1

    resolution = ReviewResolution(
        license_plate=result.license_plate,
        reviewer="senior_auditor",
        approved=True,
        corrected_code="def good_syntax() -> None:\n    pass\n",
        feedback_notes="Fixed missing parenthesis and return type annotation.",
    )
    bridge.ingest_resolution(resolution, blackbox=blackbox)

    assert bridge.count_pending_reviews() == 0
    school_df = blackbox.fetch_driving_school_dataframe()
    assert school_df.height == 1
    assert school_df["license_plate"][0] == result.license_plate
    assert school_df["reviewer"][0] == "senior_auditor"


def test_error_budget_overload_forces_slow_lane(tmp_path: Path):
    shared_dir = tmp_path / "n8n_overload"
    bridge = N8nBridge(shared_dir=shared_dir)
    budget = ErrorBudgetMonitor(max_pending_reviews=1)

    road = Road(name="Budget_Protected_Road", n8n_bridge=bridge, error_budget=budget)

    # Simulamos un vehículo previo esperando revisión humana
    first_vehicle = Vehicle(assigned_lane=Lane.MIDDLE, payload={"task": "pending_1"})
    bridge.dispatch_for_review(first_vehicle, road_name="Budget_Protected_Road")
    assert bridge.count_pending_reviews() == 1

    # El siguiente vehículo debe frenarse automáticamente hacia el Carril Lento
    second_vehicle = Vehicle(payload={"task": "should_be_throttled"})
    result = road.transit(second_vehicle, run_llm=False)

    assert result.assigned_lane == Lane.SLOW