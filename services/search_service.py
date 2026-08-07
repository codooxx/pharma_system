from sqlalchemy.orm import Session
from sqlalchemy import or_
from models.products import Product

def quick_search_product(db: Session, query: str):
    """
    خدمة البحث السريع المخصصة لاختصار F9 (بحث بالباركود أو الاسم)
    """
    if not query:
        return []

    results = db.query(Product).filter(
        or_(
            Product.barcode == query,
            Product.name.ilike(f"%{query}%")
        )
    ).limit(10).all()

    formatted_results = []
    for prod in results:
        default_unit = next((u for u in prod.units if u.is_default), None)
        formatted_results.append({
            "id": prod.id,
            "name": prod.name,
            "barcode": prod.barcode,
            "default_price": default_unit.price if default_unit else 0.0,
            "default_unit": default_unit.unit_name if default_unit else "وحدة"
        })

    return formatted_results
