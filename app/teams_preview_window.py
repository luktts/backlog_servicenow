import tkinter as tk
from tkinter import messagebox


class TeamsPreviewWindow(tk.Toplevel):
    """
    Janela de pré-visualização da mensagem para Microsoft Teams.

    Responsabilidades:
    - Exibir a mensagem gerada
    - Permitir copiar a mensagem para a área de transferência
    """

    def __init__(self, parent: tk.Tk, message_text: str):
        super().__init__(parent)

        self.title("Pré-visualização da mensagem (Teams)")
        self.geometry("720x520")
        self.resizable(True, True)

        self.message_text = message_text

        self._build_ui()

    # --------------------------------------------------

    def _build_ui(self):
        container = tk.Frame(self, padx=12, pady=12)
        container.pack(fill=tk.BOTH, expand=True)

        # Título
        title_label = tk.Label(
            container,
            text="Mensagem pronta para envio no Microsoft Teams",
            font=("Segoe UI", 11, "bold")
        )
        title_label.pack(anchor="w", pady=(0, 10))

        # Área de texto com scroll
        text_frame = tk.Frame(container)
        text_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_area = tk.Text(
            text_frame,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            font=("Segoe UI", 10)
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)

        scrollbar.config(command=self.text_area.yview)

        # Inserir texto e desabilitar edição
        self.text_area.insert(tk.END, self.message_text)
        self.text_area.config(state=tk.DISABLED)

        # Área de ações
        actions = tk.Frame(container)
        actions.pack(fill=tk.X, pady=(12, 0))

        copy_button = tk.Button(
            actions,
            text="📋 Copiar mensagem",
            command=self._copy_message,
            width=22
        )
        copy_button.pack(side=tk.RIGHT)

    # --------------------------------------------------

    def _copy_message(self):
        try:
            self.clipboard_clear()
            self.clipboard_append(self.message_text)
            self.update()

            messagebox.showinfo(
                "Mensagem copiada",
                "A mensagem foi copiada para a área de transferência.\n"
                "Agora é só colar no Teams."
            )

        except Exception as exc:
            messagebox.showerror(
                "Erro ao copiar mensagem",
                str(exc)
            )