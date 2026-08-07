import tkinter as tk
from views.sales_view import SalesView

class PharmaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("نظام الصيدلية المتكامل - Pharma System")
        self.geometry("950x650")
        self.configure(bg="#1B2A4A")

        self.lift()
        self.attributes('-topmost', True)
        self.after_idle(self.attributes, '-topmost', False)
        self.focus_force()

        self.sales_view = SalesView(self)
        self.sales_view.pack(fill="both", expand=True)

        self.bind_shortcuts()

    def bind_shortcuts(self):
        self.bind("<F9>", lambda e: self.sales_view.combo_search.focus_set())
        self.bind("<Control-s>", lambda e: self.sales_view.checkout())

if __name__ == "__main__":
    app = PharmaApp()
    app.mainloop()