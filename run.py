import tkinter as tk
from app.main import IncidentDecisionApp


def main():
    root = tk.Tk()
    app = IncidentDecisionApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()