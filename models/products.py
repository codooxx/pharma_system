from datetime import datetime
from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from models.database import Base

class User(Base):
    __tablename__="users"; id=Column(Integer,primary_key=True); username=Column(String(80),unique=True,nullable=False,index=True); full_name=Column(String(160),nullable=False); password_hash=Column(String(300),nullable=False); role=Column(String(30),default="cashier",nullable=False); active=Column(Boolean,default=True); created_at=Column(DateTime,default=datetime.utcnow)
class Category(Base):
    __tablename__="categories"; id=Column(Integer,primary_key=True); name=Column(String(120),unique=True,nullable=False)
class Supplier(Base):
    __tablename__="suppliers"; id=Column(Integer,primary_key=True); name=Column(String(180),nullable=False,index=True); phone=Column(String(50)); address=Column(String(250)); balance=Column(Float,default=0)
class Customer(Base):
    __tablename__="customers"; id=Column(Integer,primary_key=True); name=Column(String(180),nullable=False,index=True); phone=Column(String(50)); balance=Column(Float,default=0)
class Product(Base):
    __tablename__="products"; id=Column(Integer,primary_key=True); barcode=Column(String(100),unique=True,index=True); name=Column(String(200),nullable=False,index=True); scientific_name=Column(String(200)); category_id=Column(Integer,ForeignKey("categories.id")); manufacturer=Column(String(160)); min_stock=Column(Float,default=5); active=Column(Boolean,default=True)
    category=relationship("Category"); units=relationship("ProductUnit",back_populates="product",cascade="all, delete-orphan"); batches=relationship("Batch",back_populates="product",cascade="all, delete-orphan")
class ProductUnit(Base):
    __tablename__="product_units"; id=Column(Integer,primary_key=True); product_id=Column(Integer,ForeignKey("products.id"),nullable=False); unit_name=Column(String(80),default="وحدة",nullable=False); conversion_factor=Column(Float,default=1); price=Column(Float,nullable=False); cost_price=Column(Float,default=0); is_default=Column(Boolean,default=True); product=relationship("Product",back_populates="units")
class Batch(Base):
    __tablename__="batches"; id=Column(Integer,primary_key=True); product_id=Column(Integer,ForeignKey("products.id"),nullable=False,index=True); batch_number=Column(String(100),nullable=False); expiry_date=Column(Date,nullable=False,index=True); quantity=Column(Float,default=0); cost_price=Column(Float,default=0); sale_price=Column(Float,default=0); product=relationship("Product",back_populates="batches")
class Sale(Base):
    __tablename__="sales"; id=Column(Integer,primary_key=True); invoice_no=Column(String(40),unique=True,nullable=False,index=True); customer_id=Column(Integer,ForeignKey("customers.id")); user_id=Column(Integer,ForeignKey("users.id")); subtotal=Column(Float,default=0); discount=Column(Float,default=0); paid=Column(Float,default=0); payment_method=Column(String(30),default="cash"); status=Column(String(30),default="completed"); created_at=Column(DateTime,default=datetime.utcnow,index=True); items=relationship("SaleItem",cascade="all, delete-orphan")
class SaleItem(Base):
    __tablename__="sale_items"; id=Column(Integer,primary_key=True); sale_id=Column(Integer,ForeignKey("sales.id"),nullable=False); product_id=Column(Integer,ForeignKey("products.id"),nullable=False); batch_id=Column(Integer,ForeignKey("batches.id"),nullable=False); quantity=Column(Float,nullable=False); price=Column(Float,nullable=False); cost=Column(Float,default=0); product=relationship("Product")
class Purchase(Base):
    __tablename__="purchases"; id=Column(Integer,primary_key=True); invoice_no=Column(String(80),index=True); supplier_id=Column(Integer,ForeignKey("suppliers.id")); user_id=Column(Integer,ForeignKey("users.id")); total=Column(Float,default=0); paid=Column(Float,default=0); created_at=Column(DateTime,default=datetime.utcnow,index=True); items=relationship("PurchaseItem",cascade="all, delete-orphan")
class PurchaseItem(Base):
    __tablename__="purchase_items"; id=Column(Integer,primary_key=True); purchase_id=Column(Integer,ForeignKey("purchases.id"),nullable=False); product_id=Column(Integer,ForeignKey("products.id"),nullable=False); batch_id=Column(Integer,ForeignKey("batches.id"),nullable=False); quantity=Column(Float,nullable=False); cost=Column(Float,nullable=False)
class Expense(Base):
    __tablename__="expenses"; id=Column(Integer,primary_key=True); title=Column(String(180),nullable=False); category=Column(String(100),default="عام"); amount=Column(Float,nullable=False); notes=Column(Text); created_at=Column(DateTime,default=datetime.utcnow,index=True)
class Setting(Base):
    __tablename__="settings"; key=Column(String(100),primary_key=True); value=Column(Text,default="")
class AuditLog(Base):
    __tablename__="audit_logs"; id=Column(Integer,primary_key=True); user_id=Column(Integer,ForeignKey("users.id")); action=Column(String(120),nullable=False); details=Column(Text); created_at=Column(DateTime,default=datetime.utcnow,index=True)
