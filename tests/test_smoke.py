from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import Base
from models.products import Batch, Product, ProductUnit
from services.auth import authenticate, ensure_admin
from services.pharmacy import sell, stock_for

def test_sale_reduces_stock():
    engine=create_engine("sqlite:///:memory:"); Base.metadata.create_all(engine); db=sessionmaker(bind=engine)(); ensure_admin(db)
    user=authenticate(db,"admin","admin123"); assert user
    product=Product(name="Test",barcode="T1"); db.add(product); db.flush()
    db.add(ProductUnit(product_id=product.id,price=100,cost_price=60)); db.add(Batch(product_id=product.id,batch_number="B1",expiry_date=date.today()+timedelta(days=100),quantity=10,cost_price=60,sale_price=100)); db.commit()
    sell(db,[{"product_id":product.id,"name":product.name,"qty":2,"price":100}],user.id)
    assert stock_for(db,product.id)==8
