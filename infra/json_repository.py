import json
from datetime import datetime
from typing import List

from domain.incident import Incident
from domain.sla import SLA


class JsonRepository:
    def load(self, file_path: str) -> List[Incident]:
        with open(file_path, "r", encoding="utf-8") as file:
            raw_data = json.load(file)

        incidents: List[Incident] = []

        for item in raw_data:
            incident = self._map_to_incident(item)
            incidents.append(incident)

        return incidents

    def _map_to_incident(self, data: dict) -> Incident:
        # --- Assignment group (string ou objeto) ---
        assignment_group = data.get("assignment_group")

        if isinstance(assignment_group, dict):
            group_name = assignment_group.get("name", "Unknown")
        elif isinstance(assignment_group, str):
            group_name = assignment_group
        else:
            group_name = "Unknown"

        # --- SLA ---
        sla_data = data.get("sla", {})
        sla = SLA(
            percentage=float(sla_data.get("percentage", 100)),
            paused=bool(sla_data.get("paused", False))
        )

        # --- Opened at ---
        opened_at_raw = data.get("opened_at")
        opened_at = datetime.strptime(
            opened_at_raw, "%Y-%m-%dT%H:%M:%SZ"
        ) if opened_at_raw else datetime.utcnow()

        return Incident(
            number=data.get("number"),
            assignment_group=group_name,
            impact=int(data.get("impact", 4)),
            urgency=int(data.get("urgency", 4)),
            opened_at=opened_at,
            sla=sla
        )