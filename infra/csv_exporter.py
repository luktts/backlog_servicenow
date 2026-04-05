import csv
from typing import List
from domain.decision import Decision


class CsvDecisionExporter:
    """
    Exports decisions to a CSV file.
    """

    HEADER = ["incident_number", "decision_type", "reason"]

    def export(self, decisions: List[Decision], file_path: str) -> None:
        with open(file_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(self.HEADER)

            for decision in decisions:
                writer.writerow([
                    decision.incident_number,
                    decision.decision_type.value,
                    decision.reason
                ])