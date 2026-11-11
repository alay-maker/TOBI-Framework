from tobi.core.rules import Lane, RuleSeverity, TrafficRule
from tobi.core.vehicle import Vehicle
from tobi.engines.local_llm import LocalLLMEngine


class Road:
    def __init__(self, name: str, confidence_threshold: float = 0.85):
        self.name = name
        self.confidence_threshold = confidence_threshold
        self.pre_rules: list[TrafficRule] = []
        self.post_rules: list[TrafficRule] = []

    def add_pre_rule(self, rule: TrafficRule) -> None:
        self.pre_rules.append(rule)

    def add_post_rule(self, rule: TrafficRule) -> None:
        self.post_rules.append(rule)

    def transit(self, vehicle: Vehicle, run_llm: bool = True) -> Vehicle:
        vehicle.log_event(f"Entrando en carretera: {self.name}")

        for rule in self.pre_rules:
            if not rule.enforce(vehicle.payload):
                vehicle.log_event(f"Fallo en regla previa {rule.rule_id}: {rule.description}")
                if rule.severity == RuleSeverity.BLOCK_TO_SLOW:
                    vehicle.assigned_lane = Lane.SLOW
                    return vehicle
                vehicle.assigned_lane = Lane.MIDDLE

        if run_llm and "prompt" in vehicle.payload:
            try:
                engine = LocalLLMEngine(model_name=vehicle.engine)
                result = engine.generate_structured_code(vehicle.payload["prompt"])
                vehicle.output = result.model_dump()
                vehicle.payload["generated_code"] = result.python_code
                vehicle.log_event(f"Inferencia completada (Confianza: {result.confidence})")

                if result.confidence < self.confidence_threshold:
                    vehicle.assigned_lane = Lane.MIDDLE
                    vehicle.log_event("Confianza baja: degradado a Carril Medio")
            except Exception as e: #noqa: BLE001
                vehicle.assigned_lane = Lane.MIDDLE
                vehicle.log_event(f"Error en motor LLM ({e}): desviado a Carril Medio")
                return vehicle

        for rule in self.post_rules:
            if not rule.enforce(vehicle.payload):
                vehicle.log_event(f"Fallo en regla posterior {rule.rule_id}: {rule.description}")
                vehicle.assigned_lane = (
                    Lane.SLOW if rule.severity == RuleSeverity.BLOCK_TO_SLOW else Lane.MIDDLE
                )

        vehicle.log_event(f"Tránsito finalizado en: {vehicle.assigned_lane.value}")
        return vehicle
