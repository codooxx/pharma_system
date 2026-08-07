import sys
import os

# إضافة جذر المشروع إلى مسار بايثون
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date
from models.database import SessionLocal, engine, Base
from models.products import Product, ProductUnit
from models.inventory import Batch

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    if db.query(Product).first():
        print("[-] البيانات التجريبية موجودة مسبقاً.")
        db.close()
        return

    # صنف تجريبي
    panadol = Product(name="Panadol Extra", barcode="6281000111222")
    db.add(panadol)
    db.commit()

    # الوحدات (علبة وشريط)
    u_pack = ProductUnit(product_id=panadol.id, unit_name="علبة", conversion_factor=2, price=2000.0, cost_price=1500.0, is_default=True)
    u_strip = ProductUnit(product_id=panadol.id, unit_name="شريط", conversion_factor=1, price=1000.0, cost_price=750.0, is_default=False)
    db.add_all([u_pack, u_strip])

    # التشغيلة والمخزون
    batch = Batch(product_id=panadol.id, batch_number="BN202601", expiry_date=date(2027, 12, 31), quantity=100, bonus_quantity=10)
    db.add(batch)

    db.commit()
    db.close()
    print("[+] تم إضافة بيانات الفحص بنجاح!")

if __name__ == "__main__":
    seed()