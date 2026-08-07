def calculate_effective_cost(unit_cost: float, total_units: int, bonus_units: int) -> float:
    """
    حساب متوسط التكلفة الفعلي للقطعة بعد إضافة كمية البونص المجانية
    """
    total_received = total_units + bonus_units
    if total_received == 0:
        return 0.0
    return round((unit_cost * total_units) / total_received, 2)

def convert_to_base_unit(quantity: int, conversion_factor: int) -> int:
    """
    تحويل الكمية المدخلة (علبة/دزينة/كرتونة) إلى أصغر وحدة تعبئة للمخزون
    """
    return quantity * conversion_factor