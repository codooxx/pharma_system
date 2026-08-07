from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from models.database import Base

class Batch(Base):
    __tablename__ = "batches"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    batch_number = Column(String, nullable=False, index=True)
    expiry_date = Column(Date, nullable=False)
    quantity = Column(Integer, default=0)  # الكمية المتاحة بالوحدة الصغرى
    bonus_quantity = Column(Integer, default=0)  # حقل البونص المجاني

    product = relationship("Product", back_populates="batches")