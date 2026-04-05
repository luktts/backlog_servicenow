import os
from collections import defaultdict
from typing import List


class TeamsMessageBuilder:
    """
    Builds a Teams-ready message (plain text) from decisions,
    grouped by decision type.

    Responsibility:
    - Load Teams message template
    - Group incidents by decision type
    - Return a formatted text message for preview/copy
    """

    def __init__(self, template_path: str):
        self.template_path = self._resolve_path(template_path)

    # --------------------------------------------------

    def build_message(
        self,
        department_name: str,
        tech_lead_name: str,
        manager_name: str,
        decisions: List
    ) -> str:
        """
        Returns the final Teams message as plain text.
        """

        template = self._load_template()
        decisions_block = self._build_decisions_block(decisions)

        return template.format(
            department_name=department_name,
            tech_lead_name=tech_lead_name,
            manager_name=manager_name,
            decisions_by_type=decisions_block
        )

    # --------------------------------------------------
    # Internal helpers
    # --------------------------------------------------

    def _build_decisions_block(self, decisions: List) -> str:
        grouped = defaultdict(list)

        for decision in decisions:
            grouped[decision.decision_type.description].append(
                decision.incident_number
            )

        blocks = []

        for decision_description, incidents in grouped.items():
            block_lines = [
                f"🔹 {decision_description} ({len(incidents)})",
                *[f"- {inc}" for inc in incidents],
                "",
                "Link do ServiceNow (cole aqui):",
                "--------------------------------",
                ""
            ]
            blocks.append("\n".join(block_lines))

        return "\n".join(blocks)

    def _load_template(self) -> str:
        if not os.path.exists(self.template_path):
            raise FileNotFoundError(
                f"Template Teams não encontrado: {self.template_path}"
            )

        with open(self.template_path, "r", encoding="utf-8") as file:
            return file.read()

    def _resolve_path(self, relative_path: str) -> str:
        base_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..")
        )
        return os.path.join(base_dir, relative_path)