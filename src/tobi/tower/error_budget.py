from pydantic import BaseModel, Field


class BudgetStatus(BaseModel):
    max_pending_reviews: int
    current_pending: int
    is_overloaded: bool
    utilization_ratio: float = Field(ge=0.0)


class ErrorBudgetMonitor:
    def __init__(self, max_pending_reviews: int = 10):
        self.max_pending_reviews = max_pending_reviews

    def evaluate_load(self, current_pending_count: int) -> BudgetStatus:
        """Evalúa si la cola de supervisión humana supera el presupuesto cognitivo."""
        ratio = (
            current_pending_count / self.max_pending_reviews
            if self.max_pending_reviews > 0
            else 1.0
        )
        return BudgetStatus(
            max_pending_reviews=self.max_pending_reviews,
            current_pending=current_pending_count,
            is_overloaded=current_pending_count >= self.max_pending_reviews,
            utilization_ratio=round(ratio, 2),
        )