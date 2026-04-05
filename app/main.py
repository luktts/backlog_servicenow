import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from typing import List
import webbrowser
import os

from infra.json_repository import JsonRepository
from infra.csv_exporter import CsvDecisionExporter
from infra.department_repository import DepartmentRepository
from infra.email_eml_builder import EmailEmlBuilder
from infra.teams_message_builder import TeamsMessageBuilder

from app.teams_preview_window import TeamsPreviewWindow

from engine.decision_engine import DecisionEngine

from domain.rules import (
    rule_sla_at_risk,
    rule_aged_backlog,
    rule_priority_mismatch,
    rule_sla_paused_too_long
)
from domain.decision import Decision, DecisionType


class IncidentDecisionApp:
    SERVICENOW_URL = "https://example.service-now.com"

    DEPARTMENT_CONFIG_PATH = os.path.join("config", "departments.json")

    EMAIL_TEMPLATE_PATH = os.path.join("config", "email", "email_template.txt")
    EMAIL_SIGNATURE_PATH = os.path.join("assets", "email", "signature.png")

    TEAMS_TEMPLATE_PATH = os.path.join("config", "teams", "message_template.txt")

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Incident Backlog Decision Engine")
        self.root.geometry("1150x650")

        self.decisions: List[Decision] = []
        self.filtered_decisions: List[Decision] = []

        self.department_repo = DepartmentRepository(
            self.DEPARTMENT_CONFIG_PATH
        )

        self.email_builder = EmailEmlBuilder(
            email_template_path=self.EMAIL_TEMPLATE_PATH,
            signature_image_path=self.EMAIL_SIGNATURE_PATH
        )

        self.teams_builder = TeamsMessageBuilder(
            template_path=self.TEAMS_TEMPLATE_PATH
        )

        self._build_ui()

    # ---------------- UI ----------------
    def _build_ui(self):
        main = tk.Frame(self.root, padx=10, pady=10)
        main.pack(fill=tk.BOTH, expand=True)

        # ================== AÇÕES SUPERIORES ==================
        top_actions = tk.Frame(main)
        top_actions.pack(fill=tk.X)

        tk.Button(top_actions, text="Carregar JSON", command=self.load_json)\
            .pack(side=tk.LEFT)
        tk.Button(top_actions, text="Exportar CSV", command=self.export_csv)\
            .pack(side=tk.LEFT, padx=5)
        tk.Button(
            top_actions,
            text="Copiar incidentes do filtro",
            command=self.copy_filtered_incidents
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            top_actions,
            text="Abrir ServiceNow",
            command=self.open_servicenow
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            top_actions,
            text="Limpar",
            command=self.clear
        ).pack(side=tk.LEFT, padx=5)

        # ================== FILTROS ==================
        filters = tk.Frame(main)
        filters.pack(fill=tk.X, pady=10)

        tk.Label(filters, text="Tipo de decisão:").pack(side=tk.LEFT)

        self.type_filter = ttk.Combobox(
            filters,
            values=["Todos"] + [d.description for d in DecisionType],
            state="readonly",
            width=40
        )
        self.type_filter.current(0)
        self.type_filter.pack(side=tk.LEFT, padx=5)
        self.type_filter.bind(
            "<<ComboboxSelected>>",
            lambda e: self.apply_filters()
        )

        tk.Label(filters, text="Departamento:").pack(side=tk.LEFT, padx=(15, 2))

        self.department_filter = ttk.Combobox(
            filters,
            values=["Todos"] + self.department_repo.list_departments(),
            state="readonly",
            width=30
        )
        self.department_filter.current(0)
        self.department_filter.pack(side=tk.LEFT, padx=5)
        self.department_filter.bind(
            "<<ComboboxSelected>>",
            lambda e: self.apply_filters()
        )

        tk.Label(filters, text="Buscar:").pack(side=tk.LEFT, padx=(15, 2))

        self.search_var = tk.StringVar()
        search_entry = tk.Entry(
            filters,
            textvariable=self.search_var,
            width=35
        )
        search_entry.pack(side=tk.LEFT)
        search_entry.bind(
            "<KeyRelease>",
            lambda e: self.apply_filters()
        )

        # ================== TABELA ==================
        table_frame = tk.Frame(main)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("incident", "decision", "department", "reason")

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        self.tree.heading("incident", text="Incident")
        self.tree.heading("decision", text="Decisão")
        self.tree.heading("department", text="Departamento")
        self.tree.heading("reason", text="Motivo")

        self.tree.column("incident", width=120)
        self.tree.column("decision", width=330)
        self.tree.column("department", width=190)
        self.tree.column("reason", width=450)

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient=tk.VERTICAL,
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # ================== AÇÕES INFERIORES (CONTATO) ==================
        bottom_actions = tk.Frame(main, pady=10)
        bottom_actions.pack(fill=tk.X)

        tk.Button(
            bottom_actions,
            text="📧 Enviar e-mail ao Tech Lead",
            command=self.send_email_to_tech_lead,
            height=2,
            width=28
        ).pack(side=tk.LEFT)

        tk.Button(
            bottom_actions,
            text="💬 Mensagem Teams",
            command=self.open_teams_preview,
            height=2,
            width=28
        ).pack(side=tk.LEFT, padx=10)

        # ================== STATUS ==================
        self.status = tk.Label(
            self.root,
            text="Aguardando dados...",
            anchor="w"
        )
        self.status.pack(fill=tk.X)

    # ---------------- Actions ----------------
    def load_json(self):
        path = filedialog.askopenfilename(
            title="Selecione o export do ServiceNow",
            filetypes=[("JSON files", "*.json")]
        )
        if not path:
            return

        repo = JsonRepository()
        incidents = repo.load(path)

        engine = DecisionEngine([
            rule_sla_at_risk,
            rule_aged_backlog,
            rule_priority_mismatch,
            rule_sla_paused_too_long
        ])

        self.decisions = engine.evaluate(incidents)
        self.apply_filters()

    def apply_filters(self):
        self.tree.delete(*self.tree.get_children())

        type_selected = self.type_filter.get()
        dept_selected = self.department_filter.get()
        search_text = self.search_var.get().lower()

        filtered: List[Decision] = []

        for d in self.decisions:
            if type_selected != "Todos" and \
               d.decision_type.description != type_selected:
                continue

            department = self.department_repo.find_by_assignment_group(
                d.assignment_group
            )
            department_name = department.name if department else "Não mapeado"

            if dept_selected != "Todos" and \
               department_name != dept_selected:
                continue

            if search_text and \
               search_text not in (
                   d.incident_number.lower() + d.reason.lower()
               ):
                continue

            filtered.append(d)

            self.tree.insert(
                "",
                tk.END,
                values=(
                    d.incident_number,
                    d.decision_type.description,
                    department_name,
                    d.reason
                )
            )

        self.filtered_decisions = filtered
        self.status.config(
            text=f"{len(filtered)} de {len(self.decisions)} decisões exibidas"
        )

    def send_email_to_tech_lead(self):
        if not self.filtered_decisions:
            messagebox.showwarning(
                "Nenhuma decisão",
                "Não há decisões filtradas para envio."
            )
            return

        department = self.department_repo.find_by_assignment_group(
            self.filtered_decisions[0].assignment_group
        )

        self.email_builder.build_and_open(
            department_name=department.name,
            tech_lead_name=department.tech_lead,
            tech_lead_email=department.tech_lead_email,
            manager_name=department.manager,
            manager_email=department.manager_email,
            decisions=self.filtered_decisions
        )

    def open_teams_preview(self):
        if not self.filtered_decisions:
            messagebox.showwarning(
                "Nenhuma decisão",
                "Não há decisões filtradas para gerar mensagem."
            )
            return

        department = self.department_repo.find_by_assignment_group(
            self.filtered_decisions[0].assignment_group
        )

        message_text = self.teams_builder.build_message(
            department_name=department.name,
            tech_lead_name=department.tech_lead,
            manager_name=department.manager,
            decisions=self.filtered_decisions
        )

        TeamsPreviewWindow(self.root, message_text)

    def copy_filtered_incidents(self):
        if not self.filtered_decisions:
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(
            "\n".join(d.incident_number for d in self.filtered_decisions)
        )
        self.root.update()

    def open_servicenow(self):
        webbrowser.open_new_tab(self.SERVICENOW_URL)

    def export_csv(self):
        if not self.decisions:
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".csv"
        )
        if path:
            CsvDecisionExporter().export(self.decisions, path)

    def clear(self):
        self.tree.delete(*self.tree.get_children())
        self.decisions = []
        self.filtered_decisions = []
        self.status.config(text="Aguardando dados...")


if __name__ == "__main__":
    root = tk.Tk()
    IncidentDecisionApp(root)
    root.mainloop()