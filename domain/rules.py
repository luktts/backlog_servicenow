from typing import Optional
from domain.incident import Incident
from domain.decision import Decision, DecisionType


def rule_sla_at_risk(incident: Incident) -> Optional[Decision]:
    if incident.sla.is_at_risk(threshold=20.0):
        return Decision(
            incident_number=incident.number,
            assignment_group=incident.assignment_group,
            decision_type=DecisionType.ESCALATE_IMMEDIATELY,
            reason="SLA below critical threshold and not paused"
        )
    return None


def rule_aged_backlog(incident: Incident) -> Optional[Decision]:
    if incident.is_old(days=7):
        return Decision(
            incident_number=incident.number,
            assignment_group=incident.assignment_group,
            decision_type=DecisionType.REVIEW_BACKLOG_AGING,
            reason="Incident open for more than 7 days"
        )
    return None


def rule_priority_mismatch(incident: Incident) -> Optional[Decision]:
    if incident.impact == 1 and incident.urgency == 1:
        return Decision(
            incident_number=incident.number,
            assignment_group=incident.assignment_group,
            decision_type=DecisionType.REPRIORITIZE,
            reason="High impact and urgency require immediate prioritization"
        )
    return None


def rule_sla_paused_too_long(incident: Incident) -> Optional[Decision]:
    if incident.sla.paused and incident.is_old(days=5):
        return Decision(
            incident_number=incident.number,
            assignment_group=incident.assignment_group,
            decision_type=DecisionType.VALIDATE_SLA_PAUSE,
            reason="SLA paused for extended period on aged incident"
        )
    return None