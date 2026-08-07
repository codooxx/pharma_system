import tkinter as tk
from tkinter import ttk, messagebox
from models.database import SessionLocal
from services.search_service import quick_search_product
from controllers.purchase_controller import receive_purchase_item

class PurchasesView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#1B2A4A")
        self.parent = parent
        self.selected_product_id = None
        self.selected_unit_id = None
        self.setup_ui()

    def setup_ui(self):
        # Header
        header = tk.Label(self, text="إدارة المشتريات وإدخال المخزون (Intake)", font=("Arial", 16, "bold"), fg="#FFFFFF", bg="#1B2A4A")
        header.pack(pady=10)

        # Form Container
        form_frame = tk.LabelFrame(self, text=" بيانات الفاتورة والوجبة ", font=("Arial", 11, "bold"), fg="#FFFFFF", bg="#1B2A4A")
        form_frame.pack(fill="x", padx=20, pady=10)

        # Product Search
        tk.Label(form_frame, text="الصنف (F9):", fg="white", bg="#1B2A4A").grid(row=0, column=3, padx=5, pady=5, sticky="e")
        self.combo_search = ttk.Combobox(form_frame, font=("Arial", 11), justify="right", width=30)
        self.combo_search.grid(row=0, column=2, padx=5, pady=5)
        self.combo_search.bind("<KeyRelease>", self.on_search_key)
        self.combo_search.bind("<<ComboboxSelected>>", self.on_select_product)

        # Quantity
        tk.Label(form_frame, text="الكمية المشكولة:", fg="white", bg="#1B2A4A").grid(row=0, column=1, padx=5, pady=5, sticky="e")
        self.entry_qty = tk.Entry(form_frame, font=("Arial", 11), justify="center", width=10)
        self.entry_qty.grid(row=0, column=0, padx=5, pady=5)

        # Bonus Quantity
        tk.Label(form_frame, text="البونص (Bonus):", fg="white", bg="#1B2A4A").grid(row=1, column=3, padx=5, pady=5, sticky="e")
        self.entry_bonus = tk.Entry(form_frame, font=("Arial", 11), justify="center", width=10)
        self.entry_bonus.insert(0, "0")
        self.entry_bonus.grid(row=1, column=2, padx=5, pady=5)

        # Cost Price
        tk.Label(form_frame, text="سعر الشراء للوحدة:", fg="white", bg="#1B2A4A").grid(row=1, column=1, padx=5, pady=5, sticky="e")
        self.entry_cost = tk.Entry(form_frame, font=("Arial", 11), justify="center", width=10)
        self.entry_cost.grid(row=1, column=0, padx=5, pady=5)

        # Batch Number
        tk.Label(form_frame, text="رقم التشغيلة (Batch):", fg="white", bg="#1B2A4A").grid(row=2, column=3, padx=5, pady=5, sticky="e")
        self.entry_batch = tk.Entry(form_frame, font=("Arial", 11), justify="center", width=15)
        self.entry_batch.grid(row=2, column=2, padx=5, pady=5)

        # Expiry Date
        tk.Label(form_frame, text="تاريخ الانتهاء (YYYY-MM-DD):", fg="white", bg="#1B2A4A").grid(row=2, column=1, padx=5, pady=5, sticky="e")
        self.entry_expiry = tk.Entry(form_frame, font=("Arial", 11), justify="center", width=12)
        self.entry_expiry.insert(0, "2027-12-31")
        self.entry_expiry.grid(row=2, column=0, padx=5, pady=5)

        # Submit Button
        btn_save = tk.Button(self, text="حفظ الفاتورة وتحديث المخزون", font=("Arial", 12, "bold"), bg="#4ECCA3", fg="black", command=self.save_intake)
        btn_save.pack(pady=15)

    def on_search_key(self, event):
        if event.keysym in ("Up", "Down", "Return", "Left", "Right", "Escape"):
            return
        query = self.combo_search.get().strip()
        if not query:
            return

        db = SessionLocal()
        results = quick_search_product(db, query)
        db.close()

        if results:
            self.search_map = {f"{item['name']} - [{item['default_unit']}]": item for item in results}
            self.combo_search['values'] = list(self.search_map.keys())
            self.combo_search.event_generate('<Down>')

    def on_select_product(self, event=None):
        selected = self.combo_search.get()
        if selected in self.search_map:
            item = self.search_map[selected]
            self.selected_product_id = item["id"]
            self.selected_unit_id = 1  # Default unit ID

    def save_intake(self):
        if not self.selected_product_id:
            messagebox.showwarning("تنبيه", "الرجاء اختيار الصنف أولاً!")
            return

        try:
            qty = int(self.entry_qty.get().strip())
            bonus = int(self.entry_bonus.get().strip())
            cost = float(self.entry_cost.get().strip())
            batch = self.entry_batch.get().strip()
            expiry = self.entry_expiry.get().strip()

            db = SessionLocal()
            receive_purchase_item(db, self.selected_product_id, self.selected_unit_id, qty, bonus, cost, batch, expiry)
            db.close()

            messagebox.showinfo("نجاح", "تم تسجيل المشتريات وتحديث متوسط التكلفة والمخزون بنجاح!")
            self.clear_form()
        except Exception as e:
            messagebox.showerror("خطأ", f"تعذر حفظ الفاتورة: {str(e)}")

    def clear_form(self):
        self.combo_search.set('')
        self.entry_qty.delete(0, tk.END)
        self.entry_bonus.delete(0, tk.END)
        self.entry_bonus.insert(0, "0")
        self.entry_cost.delete(0, tk.END)
        self.entry_batch.delete(0, tk.END)
        self.selected_product_id = None