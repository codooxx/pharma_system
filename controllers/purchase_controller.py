from datetime import datetime
from sqlalchemy.orm import Session
from models.products import Product, ProductUnit
from models.inventory import Batch

def receive_purchase_item(
    db: Session, 
    product_id: int, 
    unit_id: int, 
    qty_purchased: int, 
    bonus_qty: int, 
    purchase_price: float, 
    batch_number: str, 
    expiry_date_str: str
):
    """
    Processes incoming stock intake, computes unit conversions, and manages batch inventory with bonus tracking.
    """
    unit = db.query(ProductUnit).filter(ProductUnit.id == unit_id).first()
    if not unit:
        raise ValueError("Selected product unit does not exist.")

    # Convert incoming pack quantities to total base units
    total_base_qty = (qty_purchased + bonus_qty) * unit.conversion_factor
    expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()

    # Check if batch exists or create new one
    batch = db.query(Batch).filter(
        Batch.product_id == product_id,
        Batch.batch_number == batch_number
    ).first()

    if batch:
        batch.quantity += total_base_qty
        batch.bonus_quantity += (bonus_qty * unit.conversion_factor)
    else:
        batch = Batch(
            product_id=product_id,
            batch_number=batch_number,
            expiry_date=expiry_date,
            quantity=total_base_qty,
            bonus_quantity=(bonus_qty * unit.conversion_factor)
        )
        db.add(batch)

    # Calculate effective cost considering bonus items
    total_received = qty_purchased + bonus_qty
    effective_unit_cost = (purchase_price * qty_purchased) / total_received if total_received > 0 else purchase_price
    unit.cost_price = round(effective_unit_cost, 2)

    db.commit()
    return True