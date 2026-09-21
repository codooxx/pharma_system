import csv, shutil, tkinter as tk
from datetime import date, datetime, timedelta
from tkinter import filedialog, messagebox, ttk
from sqlalchemy import func, or_
from models.database import DB_PATH, SessionLocal
from models.products import Batch, Expense, Product, ProductUnit, Sale, SaleItem, User
from services.auth import authenticate, hash_password
from services.pharmacy import dashboard, sell, stock_for
BG="#f3f6f9"; NAV="#123b5d"; GREEN="#16a085"; TEXT="#183247"
class PharmacyApp(tk.Tk):
    def __init__(self):
        super().__init__(); self.title("Night Soft Pharmacy ERP"); self.geometry("1180x720"); self.minsize(1000,620); self.configure(bg=BG); self.user=None; self.login()
    def clear(self):
        for w in self.winfo_children(): w.destroy()
    def login(self):
        self.clear(); box=tk.Frame(self,bg="white",padx=45,pady=35); box.place(relx=.5,rely=.5,anchor="center")
        tk.Label(box,text="نظام إدارة الصيدلية",font=("Arial",24,"bold"),fg=NAV,bg="white").pack(pady=(0,20)); tk.Label(box,text="اسم المستخدم",bg="white").pack(anchor="e"); u=tk.Entry(box,width=32,font=("Arial",13),justify="right"); u.pack(pady=5); tk.Label(box,text="كلمة المرور",bg="white").pack(anchor="e"); p=tk.Entry(box,width=32,font=("Arial",13),show="*",justify="right"); p.pack(pady=5)
        def go(*_):
            db=SessionLocal(); user=authenticate(db,u.get(),p.get()); db.close()
            if not user: messagebox.showerror("دخول","بيانات الدخول غير صحيحة"); return
            self.user=user; self.shell()
        tk.Button(box,text="دخول",command=go,bg=GREEN,fg="white",font=("Arial",13,"bold"),width=25).pack(pady=20); p.bind("<Return>",go); u.focus_set(); tk.Label(box,text="أول دخول: admin / admin123",bg="white",fg="#777").pack()
    def shell(self):
        self.clear(); nav=tk.Frame(self,bg=NAV,width=205); nav.pack(side="right",fill="y"); nav.pack_propagate(False); tk.Label(nav,text="Night Soft\nPharmacy",bg=NAV,fg="white",font=("Arial",18,"bold")).pack(pady=20); self.content=tk.Frame(self,bg=BG); self.content.pack(fill="both",expand=True)
        pages=[("لوحة التحكم",self.dashboard_page),("نقطة البيع",self.pos_page),("الأصناف والمخزون",self.products_page),("الصلاحيات",self.expiry_page),("المصروفات",self.expenses_page),("التقارير",self.reports_page)]
        if self.user.role=="admin": pages += [("المستخدمون",self.users_page),("الإعدادات والنسخ",self.settings_page)]
        for text,fn in pages: tk.Button(nav,text=text,command=fn,bg=NAV,fg="white",relief="flat",font=("Arial",12),anchor="e",padx=20,pady=10).pack(fill="x")
        tk.Button(nav,text="تسجيل الخروج",command=self.login,bg="#b23b3b",fg="white",relief="flat",pady=10).pack(side="bottom",fill="x"); self.dashboard_page()
    def page_start(self,title):
        for w in self.content.winfo_children(): w.destroy()
        tk.Label(self.content,text=title,bg=BG,fg=TEXT,font=("Arial",22,"bold"),anchor="e").pack(fill="x",padx=25,pady=18); body=tk.Frame(self.content,bg=BG); body.pack(fill="both",expand=True,padx=25,pady=(0,20)); return body
    def dashboard_page(self):
        b=self.page_start("لوحة التحكم"); db=SessionLocal(); d=dashboard(db); db.close()
        for title,value,color in [("مبيعات اليوم",f"{d['sales']:,.2f} ج.س",GREEN),("صافي اليوم",f"{d['net']:,.2f} ج.س","#2980b9"),("مخزون منخفض",d['low'],"#e67e22"),("قريب الانتهاء",d['expiry'],"#c0392b")]:
            c=tk.Frame(b,bg="white",padx=25,pady=25); c.pack(side="right",padx=8,fill="x",expand=True); tk.Label(c,text=title,bg="white",fg="#687785",font=("Arial",12)).pack(); tk.Label(c,text=value,bg="white",fg=color,font=("Arial",20,"bold")).pack(pady=8)
    def products_page(self):
        b=self.page_start("الأصناف والمخزون"); form=tk.Frame(b,bg="white",padx=12,pady=12); form.pack(fill="x"); fields=[]
        for label in ["الاسم","الباركود","التكلفة","سعر البيع","الكمية","التشغيلة","الصلاحية YYYY-MM-DD"]:
            e=tk.Entry(form,width=14,justify="right"); e.pack(side="right",padx=2); tk.Label(form,text=label,bg="white").pack(side="right"); fields.append(e)
        tree=self.table(b,("stock","price","expiry","barcode","name"),("المخزون","السعر","أقرب صلاحية","الباركود","الصنف"))
        def load():
            tree.delete(*tree.get_children()); db=SessionLocal()
            for p in db.query(Product).order_by(Product.name).all():
                unit=p.units[0] if p.units else None; ex=min((x.expiry_date for x in p.batches if x.quantity>0),default="-"); tree.insert("","end",values=(stock_for(db,p.id),unit.price if unit else 0,ex,p.barcode or "",p.name))
            db.close()
        def add():
            try:
                name,barcode,cost,price,qty,batch,expiry=[x.get().strip() for x in fields]; db=SessionLocal(); p=db.query(Product).filter(Product.barcode==barcode).first() if barcode else None
                if not p: p=Product(name=name,barcode=barcode or None); db.add(p); db.flush(); db.add(ProductUnit(product_id=p.id,unit_name="وحدة",price=float(price),cost_price=float(cost)))
                db.add(Batch(product_id=p.id,batch_number=batch or f"B-{datetime.now():%H%M%S}",expiry_date=datetime.strptime(expiry,"%Y-%m-%d").date(),quantity=float(qty),cost_price=float(cost),sale_price=float(price))); db.commit(); db.close(); load()
            except Exception as e: messagebox.showerror("خطأ",str(e))
        tk.Button(form,text="حفظ",command=add,bg=GREEN,fg="white").pack(side="left",padx=8); load()
    def pos_page(self):
        b=self.page_start("نقطة البيع"); top=tk.Frame(b,bg="white",pady=10); top.pack(fill="x"); search=tk.Entry(top,font=("Arial",14),justify="right"); search.pack(side="right",fill="x",expand=True,padx=10); cart=[]; tree=self.table(b,("total","qty","price","name"),("الإجمالي","الكمية","السعر","الصنف")); total=tk.StringVar(value="الإجمالي: 0.00 ج.س")
        def refresh():
            tree.delete(*tree.get_children()); [tree.insert("","end",values=(f"{x['qty']*x['price']:.2f}",x['qty'],f"{x['price']:.2f}",x['name'])) for x in cart]; total.set(f"الإجمالي: {sum(x['qty']*x['price'] for x in cart):,.2f} ج.س")
        def add(*_):
            q=search.get().strip(); db=SessionLocal(); p=db.query(Product).filter(or_(Product.barcode==q,Product.name.ilike(f"%{q}%"))).first()
            if not p or not p.units: db.close(); messagebox.showwarning("بحث","الصنف غير موجود"); return
            row=next((x for x in cart if x["product_id"]==p.id),None)
            if row: row["qty"]+=1
            else: cart.append({"product_id":p.id,"name":p.name,"qty":1,"price":p.units[0].price})
            db.close(); refresh(); search.delete(0,"end")
        def checkout():
            db=SessionLocal()
            try: sale=sell(db,cart,self.user.id); messagebox.showinfo("تم",f"تم حفظ الفاتورة {sale.invoice_no}"); cart.clear(); refresh()
            except Exception as e: db.rollback(); messagebox.showerror("تعذر البيع",str(e))
            finally: db.close()
        tk.Button(top,text="إضافة",command=add,bg=GREEN,fg="white",width=12).pack(side="right"); search.bind("<Return>",add); tk.Label(b,textvariable=total,bg=BG,fg=GREEN,font=("Arial",20,"bold")).pack(side="right",pady=12); tk.Button(b,text="إتمام البيع",command=checkout,bg=NAV,fg="white",font=("Arial",13,"bold"),padx=20,pady=8).pack(side="left",pady=12); search.focus_set()
    def expiry_page(self):
        b=self.page_start("تنبيهات الصلاحية"); tree=self.table(b,("qty","expiry","batch","name"),("الكمية","الصلاحية","التشغيلة","الصنف")); db=SessionLocal()
        for x in db.query(Batch).filter(Batch.quantity>0,Batch.expiry_date<=date.today()+timedelta(days=180)).order_by(Batch.expiry_date).all(): tree.insert("","end",values=(x.quantity,x.expiry_date,x.batch_number,x.product.name))
        db.close()
    def expenses_page(self):
        b=self.page_start("المصروفات"); f=tk.Frame(b,bg="white",pady=10); f.pack(fill="x"); title=tk.Entry(f,justify="right"); amount=tk.Entry(f,justify="right")
        for label,e in [("البيان",title),("المبلغ",amount)]: e.pack(side="right",padx=5); tk.Label(f,text=label,bg="white").pack(side="right")
        tree=self.table(b,("date","amount","title"),("التاريخ","المبلغ","البيان"))
        def load():
            tree.delete(*tree.get_children()); db=SessionLocal(); [tree.insert("","end",values=(x.created_at.strftime("%Y-%m-%d"),x.amount,x.title)) for x in db.query(Expense).order_by(Expense.id.desc()).all()]; db.close()
        def add():
            try: db=SessionLocal(); db.add(Expense(title=title.get(),amount=float(amount.get()))); db.commit(); db.close(); load()
            except Exception as e: messagebox.showerror("خطأ",str(e))
        tk.Button(f,text="إضافة",command=add,bg=GREEN,fg="white").pack(side="left",padx=10); load()
    def reports_page(self):
        b=self.page_start("تقارير المبيعات والأرباح"); tree=self.table(b,("profit","cost","sales","date"),("الربح","التكلفة","المبيعات","التاريخ")); db=SessionLocal(); rows=db.query(func.date(Sale.created_at),func.sum(Sale.subtotal-Sale.discount),func.sum(SaleItem.cost*SaleItem.quantity)).join(SaleItem,SaleItem.sale_id==Sale.id).group_by(func.date(Sale.created_at)).order_by(func.date(Sale.created_at).desc()).all(); db.close()
        for day,sales,cost in rows: tree.insert("","end",values=(f"{sales-cost:.2f}",f"{cost:.2f}",f"{sales:.2f}",day))
        def export():
            path=filedialog.asksaveasfilename(defaultextension=".csv",filetypes=[("CSV","*.csv")])
            if path:
                with open(path,"w",newline="",encoding="utf-8-sig") as f: w=csv.writer(f); w.writerow(["التاريخ","المبيعات","التكلفة","الربح"]); [w.writerow(reversed(tree.item(i)["values"])) for i in tree.get_children()]
        tk.Button(b,text="تصدير CSV",command=export,bg=GREEN,fg="white").pack(anchor="w",pady=8)
    def users_page(self):
        b=self.page_start("المستخدمون والصلاحيات"); f=tk.Frame(b,bg="white",pady=10); f.pack(fill="x"); es=[tk.Entry(f,justify="right") for _ in range(3)]; role=ttk.Combobox(f,values=["admin","manager","pharmacist","cashier"],state="readonly"); role.set("cashier")
        for label,e in zip(["الاسم الكامل","المستخدم","كلمة المرور"],es): e.pack(side="right",padx=4); tk.Label(f,text=label,bg="white").pack(side="right")
        role.pack(side="right",padx=4); tree=self.table(b,("active","role","username","name"),("نشط","الدور","المستخدم","الاسم"))
        def load():
            tree.delete(*tree.get_children()); db=SessionLocal(); [tree.insert("","end",values=("نعم" if x.active else "لا",x.role,x.username,x.full_name)) for x in db.query(User).all()]; db.close()
        def add():
            try: db=SessionLocal(); db.add(User(full_name=es[0].get(),username=es[1].get(),password_hash=hash_password(es[2].get()),role=role.get())); db.commit(); db.close(); load()
            except Exception as e: messagebox.showerror("خطأ",str(e))
        tk.Button(f,text="إضافة مستخدم",command=add,bg=GREEN,fg="white").pack(side="left",padx=8); load()
    def settings_page(self):
        b=self.page_start("الإعدادات والنسخ الاحتياطي"); tk.Label(b,text="ملف البيانات محفوظ محلياً ويمكن نسخه واستعادته بسهولة.",bg=BG,font=("Arial",14)).pack(pady=20)
        def backup():
            path=filedialog.asksaveasfilename(defaultextension=".db",initialfile=f"pharmacy-backup-{date.today()}.db")
            if path: shutil.copy2(DB_PATH,path); messagebox.showinfo("تم","تم إنشاء النسخة الاحتياطية")
        tk.Button(b,text="إنشاء نسخة احتياطية",command=backup,bg=GREEN,fg="white",font=("Arial",13),padx=20,pady=10).pack()
    def table(self,parent,columns,headings):
        wrap=tk.Frame(parent,bg="white"); wrap.pack(fill="both",expand=True,pady=10); tree=ttk.Treeview(wrap,columns=columns,show="headings")
        for c,h in zip(columns,headings): tree.heading(c,text=h); tree.column(c,anchor="center")
        tree.pack(fill="both",expand=True); return tree
