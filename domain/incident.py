from dataclasses import dataclass
from datetime import datetime
from .sla import SLA


@dataclass(frozen=True)
class Incident:
    number: str
    assignment_group: str
    impact: int
    urgency: int
    opened_at: datetime
    sla: SLA

    def priority_score(self) -> int:
        """
        Derives a priority score based on impact and urgency.
        Lower score means higher priority.
        """
        return self.impact + self.urgency

    def is_old(self, days: int = 7) -> bool:
        """
        Checks if the incident has been open longer than the given number of days.
        """
        delta = datetime.utcnow() - self.opened_at
        return delta.days >= days