import json
import os
from typing import Dict, Optional, List


class Department:
    """
    Represents an organizational department.
    This is NOT a domain entity – it is configuration data.
    """

    def __init__(
        self,
        name: str,
        manager: str,
        manager_email: str,
        tech_lead: str,
        tech_lead_email: str,
        assignment_groups: List[str]
    ):
        self.name = name
        self.manager = manager
        self.manager_email = manager_email
        self.tech_lead = tech_lead
        self.tech_lead_email = tech_lead_email
        self.assignment_groups = assignment_groups


class DepartmentRepository:
    """
    Loads and provides access to department configuration data.

    Responsibility:
    - Read department definitions
    - Resolve assignment_group -> department
    """

    def __init__(self, relative_config_path: str):
        self.config_path = self._resolve_path(relative_config_path)
        self.departments: Dict[str, Department] = {}
        self._load()

    def _resolve_path(self, relative_path: str) -> str:
        """
        Resolve path relative to project root, not CWD.
        """
        base_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..")
        )
        return os.path.join(base_dir, relative_path)

    def _load(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(
                f"Arquivo de departamentos não encontrado: {self.config_path}"
            )

        with open(self.config_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        for dept_data in data.get("departments", []):
            department = Department(
                name=dept_data["name"],
                manager=dept_data["manager"],
                manager_email=dept_data["manager_email"],
                tech_lead=dept_data["tech_lead"],
                tech_lead_email=dept_data["tech_lead_email"],
                assignment_groups=dept_data["assignment_groups"]
            )
            self.departments[department.name] = department

    def find_by_assignment_group(
        self,
        assignment_group: Optional[str]
    ) -> Optional[Department]:
        if not assignment_group:
            return None

        for department in self.departments.values():
            if assignment_group in department.assignment_groups:
                return department
        return None

    def list_departments(self) -> List[str]:
        return list(self.departments.keys())