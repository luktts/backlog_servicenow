import os
from collections import defaultdict
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage


class EmailEmlBuilder:
    """
    Builds an editable Outlook draft (.eml) using MIME + X-Unsent header.
    Signature position is controlled EXCLUSIVELY by the HTML template.
    """

    def __init__(self, email_template_path: str, signature_image_path: str):
        self.email_template_path = self._resolve_path(email_template_path)
        self.signature_image_path = self._resolve_path(signature_image_path)

    def build_and_open(
        self,
        department_name: str,
        tech_lead_name: str,
        tech_lead_email: str,
        manager_name: str,
        manager_email: str,
        decisions: list
    ):
        decisions_block = self._build_decisions_block(decisions)
        template = self._load_template()

        html_body = template.format(
            department_name=department_name,
            tech_lead_name=tech_lead_name,
            manager_name=manager_name,
            decisions_by_type=decisions_block
        )

        msg = MIMEMultipart("related")
        msg["To"] = tech_lead_email
        msg["Cc"] = manager_email
        msg["Subject"] = f"[Backlog] Incidentes para tratamento - {department_name}"

        # 🔑 Este header força abertura como rascunho editável no Outlook
        msg["X-Unsent"] = "1"

        alternative = MIMEMultipart("alternative")

        alternative.attach(
            MIMEText(self._html_to_text(html_body), "plain", "utf-8")
        )
        alternative.attach(
            MIMEText(html_body, "html", "utf-8")
        )

        msg.attach(alternative)

        # ✅ Anexa a imagem UMA ÚNICA vez
        if os.path.exists(self.signature_image_path):
            with open(self.signature_image_path, "rb") as img:
                image = MIMEImage(img.read())
                image.add_header("Content-ID", "<signature>")
                image.add_header("Content-Disposition", "inline")
                msg.attach(image)

        output_dir = os.path.join(
            os.path.dirname(self.email_template_path),
            "..",
            "emails_sends"
        )
        os.makedirs(output_dir, exist_ok=True)

        eml_path = os.path.join(
            output_dir,
            f"email_{department_name.replace(' ', '_')}.eml"
        )

        with open(eml_path, "wb") as f:
            f.write(msg.as_bytes())

        os.startfile(eml_path)

    # ---------------- helpers ----------------

    def _build_decisions_block(self, decisions: list) -> str:
        grouped = defaultdict(list)
        for decision in decisions:
            grouped[decision.decision_type.description].append(
                decision.incident_number
            )

        blocks = []
        for desc, incs in grouped.items():
            blocks.append(
                f"""
                <h3>{desc} ({len(incs)})</h3>
                <pre>
{chr(10).join(incs)}
                </pre>
                <p><b>Link do ServiceNow (colar aqui):</b></p>
                <p>_____________________________________________</p>
                <br>
                """
            )
        return "\n".join(blocks)

    def _load_template(self) -> str:
        with open(self.email_template_path, "r", encoding="utf-8") as f:
            return f.read()

    def _resolve_path(self, relative_path: str) -> str:
        base_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..")
        )
        return os.path.join(base_dir, relative_path)

    def _html_to_text(self, html: str) -> str:
        return (
            html.replace("<br>", "\n")
                .replace("<br/>", "\n")
                .replace("<p>", "")
                .replace("</p>", "\n")
                .replace("<b>", "")
                .replace("</b>", "")
                .replace("<h3>", "")
                .replace("</h3>", "\n")
                .replace("<pre>", "")
                .replace("</pre>", "\n")
        )