from dataclasses import dataclass


@dataclass(frozen=True)
class SLA:
    percentage: float
    paused: bool

    def is_at_risk(self, threshold: float = 20.0) -> bool:
        """
        Returns True if SLA percentage is below threshold
        and the SLA is not paused.
        """
        return not self.paused and self.percentage <= threshold