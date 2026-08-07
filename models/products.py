from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from models.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    barcode = Column(String, unique=True, index=True, nullable=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    
    # علاقة مع الوحدات والتشغيلات
    units = relationship("ProductUnit", back_populates="product", cascade="all, delete-orphan")
    batches = relationship("Batch", back_populates="product", cascade="all, delete-orphan")

class ProductUnit(Base):
    __tablename__ = "product_units"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    unit_name = Column(String, nullable=False)  # شريط، علبة، كرتونة، دزينة
    conversion_factor = Column(Integer, default=1)  # كم وحدة أصغر يحتوي هذا التغليف
    price = Column(Float, nullable=False)  # سعر البيع لهذا التغليف
    cost_price = Column(Float, default=0.0)  # سعر التكلفة
    is_default = Column(Boolean, default=False)

    product = relationship("Product", back_populates="units")