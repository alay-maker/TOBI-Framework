from tobi.core.rules import Lane, RuleSeverity, TrafficRule
from tobi.core.vehicle import Vehicle
from tobi.engines.local_llm import LocalLLMEngine
from tobi.memory.policy_rag import PolicyRAG
from tobi.tower.blackbox import BlackBox


class Road:
    def __init__(
        self,
        name: str,
        confidence_threshold: float = 0.85,
        blackbox: BlackBox | None = None,
        policy_rag: PolicyRAG | None = None,
    ):
        self.name = name
        self.confidence_threshold = confidence_threshold
        self.pre_rules: list[TrafficRule] = []
        self.post_rules: list[TrafficRule] = []
        self.blackbox = blackbox
        self.policy_rag = policy_rag

    def add_pre_rule(self, rule: TrafficRule) -> None:
        self.pre_rules.append(rule)

    def add_post_rule(self, rule: TrafficRule) -> None:
        self.post_rules.append(rule)

    def _finalize_transit(self, vehicle: Vehicle) -> Vehicle:
        vehicle.log_event(f"Tránsito finalizado en: {vehicle.assigned_lane.value}")
        if self.blackbox is not None:
            self.blackbox.record_transit(vehicle, road_name=self.name)
        return vehicle

    def transit(self, vehicle: Vehicle, run_llm: bool = True) -> Vehicle:
        vehicle.log_event(f"Entrando en carretera: {self.name}")

        # 1. Filtro Previo (Policy-as-Code a coste cero)
        for rule in self.pre_rules:
            if not rule.enforce(vehicle.payload):
                vehicle.log_event(f"Fallo en regla previa {rule.rule_id}: {rule.description}")
                if rule.severity == RuleSeverity.BLOCK_TO_SLOW:
                    vehicle.assigned_lane = Lane.SLOW
                    return self._finalize_transit(vehicle)
                vehicle.assigned_lane = Lane.MIDDLE

        # 2. Pilar 3: Verificación Anti-Alucinación en Qdrant (Local RAG)
        query_text = vehicle.payload.get("prompt") or vehicle.payload.get("query")
        if self.policy_rag is not None and isinstance(query_text, str):
            match = self.policy_rag.verify_query(query_text)
            if not match.has_sufficient_backing:
                vehicle.assigned_lane = Lane.MIDDLE
                vehicle.log_event(
                    f"Sin respaldo suficiente en PolicyRAG (Score: {match.best_score:.2f}): "
                    "degradado a Carril Medio"
                )
            else:
                vehicle.payload["policy_context"] = match.matched_policy
                vehicle.log_event(
                    f"Respaldo verificado en PolicyRAG (Score: {match.best_score:.2f})"
                )

        # 3. Ejecución del Motor Local
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
            except Exception as e:  # noqa: BLE001
                vehicle.assigned_lane = Lane.MIDDLE
                vehicle.log_event(f"Error en motor LLM ({e}): desviado a Carril Medio")
                return self._finalize_transit(vehicle)

        # 4. Filtro Posterior (Validación de calidad con Ruff)
        for rule in self.post_rules:
            if not rule.enforce(vehicle.payload):
                vehicle.log_event(f"Fallo en regla posterior {rule.rule_id}: {rule.description}")
                vehicle.assigned_lane = (
                    Lane.SLOW if rule.severity == RuleSeverity.BLOCK_TO_SLOW else Lane.MIDDLE
                )

        return self._finalize_transit(vehicle)
