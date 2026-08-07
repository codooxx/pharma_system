from sqlalchemy.orm import Session
from models.inventory import Batch
from models.products import ProductUnit

def process_sale_item(db: Session, product_id: int, unit_id: int, quantity_sold: int):
    """
    معالجة عملية البيع وخصم المخزون آلياً بحسب تاريخ الانتهاء (الأقرب فالأقرب)
    """
    # 1. جلب وحدة البيع لمعرفة معامل التحويل إلى أصغر وحدة
    unit = db.query(ProductUnit).filter(ProductUnit.id == unit_id).first()
    if not unit:
        raise ValueError("وحدة البيع المحددة غير موجودة.")

    total_base_units_needed = quantity_sold * unit.conversion_factor

    # 2. جلب التشغيلات المتوفرة مرتبة تصاعدياً حسب تاريخ الانتهاء
    batches = db.query(Batch).filter(
        Batch.product_id == product_id,
        Batch.quantity > 0
    ).order_by(Batch.expiry_date.asc()).all()

    # التحقق من توفر إجمالي الكمية المطلوبة
    total_available = sum(b.quantity for b in batches)
    if total_available < total_base_units_needed:
        raise ValueError(f"الكمية المتاحة في المخزون ({total_available}) غير كافية لبيع ({total_base_units_needed}) وحدة.")

    # 3. خصم الكمية من Batches بالترتيب
    remaining_needed = total_base_units_needed
    for batch in batches:
        if remaining_needed <= 0:
            break

        if batch.quantity >= remaining_needed:
            batch.quantity -= remaining_needed
            remaining_needed = 0
        else:
            remaining_needed -= batch.quantity
            batch.quantity = 0

    db.commit()
    return True