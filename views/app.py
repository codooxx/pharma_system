import csv, shutil, tkinter as tk
from datetime import date, datetime, timedelta
from tkinter import filedialog, messagebox, ttk
from sqlalchemy import func, or_
from models.database import DB_PATH, SessionLocal
from models.products import Batch, Expense, Product, ProductUnit, Sale, SaleItem, SupplierOffer, User
from services.auth import authenticate, hash_password
from services.pharmacy import dashboard, sell, stock_for
BG="#eef3f8"; NAV="#102a43"; NAV_HOVER="#1e4d6f"; GREEN="#12a884"; TEXT="#102a43"; MUTED="#6b7c8f"; BORDER="#d8e2eb"
class PharmacyApp(tk.Tk):
    def __init__(self):
        super().__init__(); self.title("Night Soft Pharmacy ERP"); self.configure(bg=BG); self.user=None
        sw,sh=self.winfo_screenwidth(),self.winfo_screenheight(); self.geometry(f"{int(sw*.92)}x{int(sh*.88)}+{int(sw*.04)}+{int(sh*.05)}"); self.minsize(1050,650)
        style=ttk.Style(self); style.theme_use("clam"); style.configure("Treeview",background="white",fieldbackground="white",foreground=TEXT,rowheight=36,font=("Arial",11),borderwidth=0); style.configure("Treeview.Heading",background="#dfeaf3",foreground=TEXT,font=("Arial",11,"bold"),padding=10); style.map("Treeview",background=[("selected",GREEN)],foreground=[("selected","white")]); style.configure("TCombobox",padding=7)
        self.login()
    def clear(self):
        for w in self.winfo_children(): w.destroy()
    def button(self,parent,text,command,bg=GREEN,width=None,font=("Arial",12,"bold")):
        btn=tk.Label(parent,text=text,bg=bg,fg="white",font=font,cursor="hand2",padx=18,pady=10,width=width)
        btn.bind("<Button-1>",lambda _e:command()); btn.bind("<Enter>",lambda _e:btn.configure(bg=NAV_HOVER)); btn.bind("<Leave>",lambda _e:btn.configure(bg=bg)); return btn
    def login(self):
        self.clear(); box=tk.Frame(self,bg="white",padx=45,pady=35); box.place(relx=.5,rely=.5,anchor="center")
        tk.Label(box,text="نظام إدارة الصيدلية",font=("Arial",24,"bold"),fg=NAV,bg="white").pack(pady=(0,20)); tk.Label(box,text="اسم المستخدم",bg="white").pack(anchor="e"); u=tk.Entry(box,width=32,font=("Arial",13),justify="right"); u.pack(pady=5); tk.Label(box,text="كلمة المرور",bg="white").pack(anchor="e"); p=tk.Entry(box,width=32,font=("Arial",13),show="*",justify="right"); p.pack(pady=5)
        def go(*_):
            db=SessionLocal(); user=authenticate(db,u.get(),p.get()); db.close()
            if not user: messagebox.showerror("دخول","بيانات الدخول غير صحيحة"); return
            self.user=user; self.shell()
        self.button(box,"دخول",go,width=22,font=("Arial",13,"bold")).pack(pady=20); p.bind("<Return>",go); u.focus_set(); tk.Label(box,text="أول دخول: admin / admin123",bg="white",fg="#777").pack()
    def shell(self):
        self.clear(); nav=tk.Frame(self,bg=NAV,width=245); nav.pack(side="right",fill="y"); nav.pack_propagate(False)
        brand=tk.Frame(nav,bg=NAV); brand.pack(fill="x",padx=18,pady=(24,16)); tk.Label(brand,text="✚",bg=GREEN,fg="white",font=("Arial",19,"bold"),width=2).pack(side="right"); tk.Label(brand,text="Night Soft\nPharmacy ERP",bg=NAV,fg="white",font=("Arial",16,"bold"),justify="right").pack(side="right",padx=10)
        tk.Frame(nav,bg="#274c68",height=1).pack(fill="x",padx=18,pady=(0,8)); self.content=tk.Frame(self,bg=BG); self.content.pack(fill="both",expand=True)
        pages=[("⌂  لوحة التحكم",self.dashboard_page),("▣  نقطة البيع",self.pos_page),("▤  الأصناف والمخزون",self.products_page),("$  أسعار الموردين",self.supplier_prices_page),("◷  الصلاحيات",self.expiry_page),("−  المصروفات",self.expenses_page),("▥  التقارير",self.reports_page)]
        if self.user.role=="admin": pages += [("المستخدمون",self.users_page),("الإعدادات والنسخ",self.settings_page)]
        self.nav_labels=[]
        for text,fn in pages:
            item=tk.Label(nav,text=text,bg=NAV,fg="#d9e6ef",font=("Arial",12,"bold"),anchor="e",padx=22,pady=13,cursor="hand2"); item.pack(fill="x",padx=8,pady=2); item.bind("<Button-1>",lambda _e,f=fn,w=item:self.open_page(f,w)); item.bind("<Enter>",lambda _e,w=item:w.configure(bg=NAV_HOVER)); item.bind("<Leave>",lambda _e,w=item:w.configure(bg=GREEN if getattr(self,"active_nav",None)==w else NAV)); self.nav_labels.append(item)
        userbox=tk.Frame(nav,bg="#0b2237"); userbox.pack(side="bottom",fill="x"); tk.Label(userbox,text=f"{self.user.full_name}\n{self.user.role}",bg="#0b2237",fg="#bfd0dc",font=("Arial",10),justify="right").pack(side="right",padx=14,pady=12); logout=tk.Label(userbox,text="خروج",bg="#b84242",fg="white",cursor="hand2",padx=12,pady=8); logout.pack(side="left",padx=10); logout.bind("<Button-1>",lambda _e:self.login())
        self.open_page(self.dashboard_page,self.nav_labels[0])
    def open_page(self,fn,item):
        self.active_nav=item
        for w in self.nav_labels: w.configure(bg=GREEN if w==item else NAV,fg="white" if w==item else "#d9e6ef")
        fn()
    def page_start(self,title):
        for w in self.content.winfo_children(): w.destroy()
        top=tk.Frame(self.content,bg="white",height=78,highlightbackground=BORDER,highlightthickness=1); top.pack(fill="x"); top.pack_propagate(False); tk.Label(top,text=title,bg="white",fg=TEXT,font=("Arial",22,"bold"),anchor="e").pack(side="right",fill="y",padx=28); tk.Label(top,text=datetime.now().strftime("%Y-%m-%d"),bg="white",fg=MUTED,font=("Arial",11)).pack(side="left",padx=28)
        body=tk.Frame(self.content,bg=BG); body.pack(fill="both",expand=True,padx=26,pady=24); return body
    def dashboard_page(self):
        b=self.page_start("لوحة التحكم"); db=SessionLocal(); d=dashboard(db); db.close()
        cards=tk.Frame(b,bg=BG); cards.pack(fill="x")
        for i,(icon,title,value,color) in enumerate([("↗","مبيعات اليوم",f"{d['sales']:,.2f} ج.س",GREEN),("✓","صافي اليوم",f"{d['net']:,.2f} ج.س","#2477b3"),("!","مخزون منخفض",d['low'],"#e67e22"),("◷","قريب الانتهاء",d['expiry'],"#c0392b")]):
            c=tk.Frame(cards,bg="white",highlightbackground=BORDER,highlightthickness=1,padx=20,pady=18); c.grid(row=0,column=3-i,sticky="nsew",padx=7); cards.grid_columnconfigure(3-i,weight=1); tk.Label(c,text=icon,bg=color,fg="white",font=("Arial",16,"bold"),width=3,height=1).pack(side="right",padx=(12,0)); info=tk.Frame(c,bg="white"); info.pack(side="right",fill="both",expand=True); tk.Label(info,text=title,bg="white",fg=MUTED,font=("Arial",11),anchor="e").pack(fill="x"); tk.Label(info,text=value,bg="white",fg=TEXT,font=("Arial",19,"bold"),anchor="e").pack(fill="x",pady=(8,0))
        welcome=tk.Frame(b,bg="white",highlightbackground=BORDER,highlightthickness=1,padx=28,pady=24); welcome.pack(fill="both",expand=True,pady=(22,0)); tk.Label(welcome,text=f"مرحباً، {self.user.full_name}",bg="white",fg=TEXT,font=("Arial",20,"bold"),anchor="e").pack(fill="x"); tk.Label(welcome,text="ابدأ البيع من نقطة البيع، أو راجع المخزون وأسعار الشركات من القائمة الجانبية.",bg="white",fg=MUTED,font=("Arial",13),anchor="e").pack(fill="x",pady=(10,22)); quick=tk.Frame(welcome,bg="white"); quick.pack(anchor="e"); self.button(quick,"فتح نقطة البيع",self.pos_page).pack(side="right",padx=5); self.button(quick,"عرض الأصناف",self.products_page,bg="#2477b3").pack(side="right",padx=5)
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
        self.button(form,"حفظ الصنف",add).pack(side="left",padx=8); load()
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
        self.button(top,"إضافة",add,width=9).pack(side="right"); search.bind("<Return>",add); tk.Label(b,textvariable=total,bg=BG,fg=GREEN,font=("Arial",20,"bold")).pack(side="right",pady=12); self.button(b,"إتمام البيع",checkout,bg=NAV,font=("Arial",13,"bold")).pack(side="left",pady=12); search.focus_set()
    def expiry_page(self):
        b=self.page_start("تنبيهات الصلاحية"); tree=self.table(b,("qty","expiry","batch","name"),("الكمية","الصلاحية","التشغيلة","الصنف")); db=SessionLocal()
        for x in db.query(Batch).filter(Batch.quantity>0,Batch.expiry_date<=date.today()+timedelta(days=180)).order_by(Batch.expiry_date).all(): tree.insert("","end",values=(x.quantity,x.expiry_date,x.batch_number,x.product.name))
        db.close()
    def supplier_prices_page(self):
        b=self.page_start("دليل أسعار الموردين"); bar=tk.Frame(b,bg="white",pady=10); bar.pack(fill="x"); q=tk.Entry(bar,font=("Arial",13),justify="right"); q.pack(side="right",fill="x",expand=True,padx=10); tree=self.table(b,("expiry","retail","wholesale","unit","supplier","name"),("الصلاحية","سعر البيع","سعر المورد","الوحدة","الشركة","الصنف"))
        def load(*_):
            tree.delete(*tree.get_children()); db=SessionLocal(); query=db.query(SupplierOffer).join(Product)
            if q.get().strip(): query=query.filter(Product.name.ilike(f"%{q.get().strip()}%"))
            for x in query.order_by(Product.name).limit(1500).all(): tree.insert("","end",values=(x.expiry_date or "-",f"{x.retail_price:,.2f}" if x.retail_price else "-",f"{x.wholesale_price:,.2f}" if x.wholesale_price else "-",x.unit,x.supplier.name,x.product.name))
            db.close()
        self.button(bar,"بحث",load,width=8).pack(side="right"); q.bind("<Return>",load); load()
    def expenses_page(self):
        b=self.page_start("المصروفات"); f=tk.Frame(b,bg="white",pady=10); f.pack(fill="x"); title=tk.Entry(f,justify="right"); amount=tk.Entry(f,justify="right")
        for label,e in [("البيان",title),("المبلغ",amount)]: e.pack(side="right",padx=5); tk.Label(f,text=label,bg="white").pack(side="right")
        tree=self.table(b,("date","amount","title"),("التاريخ","المبلغ","البيان"))
        def load():
            tree.delete(*tree.get_children()); db=SessionLocal(); [tree.insert("","end",values=(x.created_at.strftime("%Y-%m-%d"),x.amount,x.title)) for x in db.query(Expense).order_by(Expense.id.desc()).all()]; db.close()
        def add():
            try: db=SessionLocal(); db.add(Expense(title=title.get(),amount=float(amount.get()))); db.commit(); db.close(); load()
            except Exception as e: messagebox.showerror("خطأ",str(e))
        self.button(f,"إضافة مصروف",add).pack(side="left",padx=10); load()
    def reports_page(self):
        b=self.page_start("تقارير المبيعات والأرباح"); tree=self.table(b,("profit","cost","sales","date"),("الربح","التكلفة","المبيعات","التاريخ")); db=SessionLocal(); rows=db.query(func.date(Sale.created_at),func.sum(Sale.subtotal-Sale.discount),func.sum(SaleItem.cost*SaleItem.quantity)).join(SaleItem,SaleItem.sale_id==Sale.id).group_by(func.date(Sale.created_at)).order_by(func.date(Sale.created_at).desc()).all(); db.close()
        for day,sales,cost in rows: tree.insert("","end",values=(f"{sales-cost:.2f}",f"{cost:.2f}",f"{sales:.2f}",day))
        def export():
            path=filedialog.asksaveasfilename(defaultextension=".csv",filetypes=[("CSV","*.csv")])
            if path:
                with open(path,"w",newline="",encoding="utf-8-sig") as f: w=csv.writer(f); w.writerow(["التاريخ","المبيعات","التكلفة","الربح"]); [w.writerow(reversed(tree.item(i)["values"])) for i in tree.get_children()]
        self.button(b,"تصدير CSV",export).pack(anchor="w",pady=8)
    def users_page(self):
        b=self.page_start("المستخدمون والصلاحيات"); f=tk.Frame(b,bg="white",pady=10); f.pack(fill="x"); es=[tk.Entry(f,justify="right") for _ in range(3)]; role=ttk.Combobox(f,values=["admin","manager","pharmacist","cashier"],state="readonly"); role.set("cashier")
        for label,e in zip(["الاسم الكامل","المستخدم","كلمة المرور"],es): e.pack(side="right",padx=4); tk.Label(f,text=label,bg="white").pack(side="right")
        role.pack(side="right",padx=4); tree=self.table(b,("active","role","username","name"),("نشط","الدور","المستخدم","الاسم"))
        def load():
            tree.delete(*tree.get_children()); db=SessionLocal(); [tree.insert("","end",values=("نعم" if x.active else "لا",x.role,x.username,x.full_name)) for x in db.query(User).all()]; db.close()
        def add():
            try: db=SessionLocal(); db.add(User(full_name=es[0].get(),username=es[1].get(),password_hash=hash_password(es[2].get()),role=role.get())); db.commit(); db.close(); load()
            except Exception as e: messagebox.showerror("خطأ",str(e))
        self.button(f,"إضافة مستخدم",add).pack(side="left",padx=8); load()
    def settings_page(self):
        b=self.page_start("الإعدادات والنسخ الاحتياطي"); tk.Label(b,text="ملف البيانات محفوظ محلياً ويمكن نسخه واستعادته بسهولة.",bg=BG,font=("Arial",14)).pack(pady=20)
        def backup():
            path=filedialog.asksaveasfilename(defaultextension=".db",initialfile=f"pharmacy-backup-{date.today()}.db")
            if path: shutil.copy2(DB_PATH,path); messagebox.showinfo("تم","تم إنشاء النسخة الاحتياطية")
        self.button(b,"إنشاء نسخة احتياطية",backup,font=("Arial",13,"bold")).pack()
    def table(self,parent,columns,headings):
        wrap=tk.Frame(parent,bg="white"); wrap.pack(fill="both",expand=True,pady=10); tree=ttk.Treeview(wrap,columns=columns,show="headings")
        for c,h in zip(columns,headings): tree.heading(c,text=h); tree.column(c,anchor="center")
        tree.pack(fill="both",expand=True); return tree
