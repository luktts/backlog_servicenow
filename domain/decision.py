from dataclasses import dataclass
from enum import Enum


class DecisionType(Enum):
    ESCALATE_IMMEDIATELY = "ESCALATE_IMMEDIATELY"
    REVIEW_BACKLOG_AGING = "REVIEW_BACKLOG_AGING"
    REPRIORITIZE = "REPRIORITIZE"
    VALIDATE_SLA_PAUSE = "VALIDATE_SLA_PAUSE"

    @property
    def description(self) -> str:
        return {
            DecisionType.ESCALATE_IMMEDIATELY:
                "Escalonar imediatamente (risco crítico de SLA)",
            DecisionType.REVIEW_BACKLOG_AGING:
                "Revisar incidente antigo no backlog",
            DecisionType.REPRIORITIZE:
                "Reavaliar prioridade do incidente",
            DecisionType.VALIDATE_SLA_PAUSE:
                "Validar pausa prolongada de SLA",
        }[self]


@dataclass(frozen=True)
class Decision:
    incident_number: str
    assignment_group: str            # ✅ ADICIONADO
    decision_type: DecisionType
    reason: str