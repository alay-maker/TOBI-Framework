from tobi.core.road import Road
from tobi.core.rules import Lane, RuleSeverity, TrafficRule
from tobi.core.vehicle import Vehicle
from tobi.engines.heuristics import (
    check_encryption_compliance,
    validate_python_code_with_ruff,
)


def build_test_road() -> Road:
    road = Road(name="Desarrollo_Modulos_TOBI")
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


def test_emergency_brake_to_slow_lane():
    road = build_test_road()
    vehicle = Vehicle(payload={"contains_sensitive_data": True, "is_encrypted": False})
    result = road.transit(vehicle, run_llm=False)
    assert result.assigned_lane == Lane.SLOW


def test_ruff_validation_routes_bad_code_to_middle_lane():
    road = build_test_road()
    # Código con sintaxis inválida para forzar que Ruff lo envíe al Carril Medio
    vehicle = Vehicle(payload={"generated_code": "def funcion_rota(:\n    pass"})
    result = road.transit(vehicle, run_llm=False)
    assert result.assigned_lane == Lane.MIDDLE


def test_clean_code_stays_in_fast_lane():
    road = build_test_road()
    vehicle = Vehicle(
        payload={
            "generated_code": "def suma(a: int, b: int) -> int:\n    return a + b\n"
        }
    )
    result = road.transit(vehicle, run_llm=False)
    assert result.assigned_lane == Lane.FAST
