from datetime import date, datetime, timedelta
from sqlalchemy import func
from models.products import AuditLog, Batch, Expense, Product, Sale, SaleItem
def stock_for(db,product_id): return float(db.query(func.coalesce(func.sum(Batch.quantity),0)).filter(Batch.product_id==product_id).scalar())
def sell(db,cart,user_id,discount=0,payment_method="cash"):
    if not cart: raise ValueError("الفاتورة فارغة")
    subtotal=sum(float(x["qty"])*float(x["price"]) for x in cart); discount=max(0,min(float(discount or 0),subtotal)); invoice=f"S-{datetime.now():%Y%m%d%H%M%S%f}"
    sale=Sale(invoice_no=invoice,user_id=user_id,subtotal=subtotal,discount=discount,paid=subtotal-discount,payment_method=payment_method); db.add(sale); db.flush()
    for row in cart:
        remaining=float(row["qty"]); batches=db.query(Batch).filter(Batch.product_id==row["product_id"],Batch.quantity>0,Batch.expiry_date>=date.today()).order_by(Batch.expiry_date).all()
        if sum(b.quantity for b in batches)<remaining: raise ValueError(f"المخزون غير كافٍ: {row['name']}")
        for batch in batches:
            take=min(remaining,batch.quantity)
            if take: batch.quantity-=take; db.add(SaleItem(sale_id=sale.id,product_id=row["product_id"],batch_id=batch.id,quantity=take,price=float(row["price"]),cost=batch.cost_price)); remaining-=take
            if remaining<=0: break
    db.add(AuditLog(user_id=user_id,action="sale.created",details=invoice)); db.commit(); return sale
def dashboard(db):
    today=date.today(); start=datetime.combine(today,datetime.min.time()); sales=db.query(func.coalesce(func.sum(Sale.subtotal-Sale.discount),0)).filter(Sale.created_at>=start,Sale.status=="completed").scalar(); expenses=db.query(func.coalesce(func.sum(Expense.amount),0)).filter(Expense.created_at>=start).scalar(); low=sum(stock_for(db,p.id)<=p.min_stock for p in db.query(Product).filter(Product.active.is_(True)).all()); expiry=db.query(Batch).filter(Batch.quantity>0,Batch.expiry_date<=today+timedelta(days=90)).count(); return {"sales":float(sales),"expenses":float(expenses),"net":float(sales-expenses),"low":low,"expiry":expiry}
