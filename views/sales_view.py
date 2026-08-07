import tkinter as tk
from tkinter import ttk, messagebox
from models.database import SessionLocal
from services.search_service import quick_search_product
from controllers.sales_controller import process_sale_item

class SalesView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#1B2A4A")
        self.parent = parent
        self.cart = []
        self.setup_ui()

    def setup_ui(self):
        search_frame = tk.LabelFrame(self, text=" إدخال الأصناف (F9) ", fg="white", bg="#1B2A4A", font=("Arial", 11, "bold"))
        search_frame.pack(fill="x", padx=15, pady=10)

        tk.Label(search_frame, text="اسم الصنف / الباركود:", fg="white", bg="#1B2A4A").pack(side="right", padx=5, pady=5)
        self.entry_search = tk.Entry(search_frame, font=("Arial", 12), justify="right")
        self.entry_search.pack(side="right", fill="x", expand=True, padx=5, pady=5)
        self.entry_search.bind("<Return>", self.perform_search)

        table_frame = tk.Frame(self, bg="#1B2A4A")
        table_frame.pack(fill="both", expand=True, padx=15, pady=5)

        columns = ("total", "price", "qty", "unit", "name", "id")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
        
        self.tree.heading("id", text="#")
        self.tree.heading("name", text="الصنف")
        self.tree.heading("unit", text="الوحدة")
        self.tree.heading("qty", text="الكمية")
        self.tree.heading("price", text="السعر")
        self.tree.heading("total", text="الإجمالي")

        self.tree.column("id", width=40, anchor="center")
        self.tree.column("name", width=200, anchor="e")
        self.tree.column("unit", width=80, anchor="center")
        self.tree.column("qty", width=60, anchor="center")
        self.tree.column("price", width=80, anchor="center")
        self.tree.column("total", width=90, anchor="center")

        self.tree.pack(fill="both", expand=True)

        bottom_frame = tk.Frame(self, bg="#1B2A4A")
        bottom_frame.pack(fill="x", padx=15, pady=10)

        self.lbl_total = tk.Label(bottom_frame, text="الإجمالي: 0.00 ج.س", font=("Arial", 16, "bold"), fg="#4ECCA3", bg="#1B2A4A")
        self.lbl_total.pack(side="right", padx=10)

        btn_checkout = tk.Button(bottom_frame, text="حفظ وإتمام البيع (Ctrl+S)", bg="#4ECCA3", fg="black", font=("Arial", 12, "bold"), command=self.checkout)
        btn_checkout.pack(side="left", padx=10)

    def perform_search(self, event=None):
        query = self.entry_search.get().strip()
        if not query:
            return

        db = SessionLocal()
        results = quick_search_product(db, query)
        db.close()

        if results:
            item = results[0]
            self.add_to_cart(item["id"], item["name"], item["default_unit"], 1, item["default_price"], 1)
            self.entry_search.delete(0, tk.END)
        else:
            messagebox.showwarning("تنبيه", "الصنف غير موجود بالمخزون!")

    def add_to_cart(self, prod_id, name, unit_name, qty, price, unit_id):
        total = qty * price
        self.cart.append({"product_id": prod_id, "unit_id": unit_id, "qty": qty, "price": price})
        self.tree.insert("", "end", values=(f"{total:.2f}", f"{price:.2f}", qty, unit_name, name, prod_id))
        self.update_total()

    def update_total(self):
        grand_total = sum(item["qty"] * item["price"] for item in self.cart)
        self.lbl_total.config(text=f"الإجمالي: {grand_total:.2f} ج.س")

    def checkout(self):
        if not self.cart:
            messagebox.showwarning("تنبيه", "الفاتورة فارغة!")
            return

        db = SessionLocal()
        try:
            for item in self.cart:
                process_sale_item(db, item["product_id"], item["unit_id"], item["qty"])
            
            messagebox.showinfo("نجاح", "تم حفظ الفاتورة وخصم الكميات من المخزون بنجاح!")
            self.cart.clear()
            for row in self.tree.get_children():
                self.tree.delete(row)
            self.update_total()
        except Exception as e:
            messagebox.showerror("خطأ في المبيعات", str(e))
        finally:
            db.close()