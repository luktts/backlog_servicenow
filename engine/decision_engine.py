from typing import List, Callable

from domain.incident import Incident
from domain.decision import Decision


Rule = Callable[[Incident], Decision | None]


class DecisionEngine:
    """
    Applies a set of business rules to incidents
    and produces business decisions.
    """

    def __init__(self, rules: List[Rule]):
        self._rules = rules

    def evaluate(self, incidents: List[Incident]) -> List[Decision]:
        """
        Applies all rules to all incidents and
        returns a list of generated decisions.
        """
        decisions: List[Decision] = []

        for incident in incidents:
            for rule in self._rules:
                decision = rule(incident)
                if decision:
                    decisions.append(decision)

        return decisions