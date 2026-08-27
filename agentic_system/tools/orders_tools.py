"""
Tools حوالين team_code/orders_billing.py.
قاعدة أساسية زي menu_tools.py: الملف ده معدلش أي سطر في كود الفريق.

ملحوظة مهمة عن باگ معروف في كودهم:
    OrderSystem.create_invoice() بتعمل InvoiceSystem() جديدة كل مرة،
    فكل الفواتير بتاخد نفس الـ invoice_id (1). عشان كده إحنا مش بنستخدم
    order_system.create_invoice() خالص - بنستخدم InvoiceSystem الحقيقية
    بتاعتهم مباشرة، بس بنسخة واحدة بنمسكها إحنا هنا. صفر تعديل في
    ملفهم، وصفر باگ في النتيجة.

كل tool بيرجع نفس الشكل الموحد:
    {"success": bool, "data": ..., "error": Optional[str]}
"""

import logging

from tasks.team_code.orders_billing import OrderSystem, InvoiceSystem
from agentic_system.tools.menu_tools import restaurant  # عشان نجيب السعر الحقيقي من المنيو

logger = logging.getLogger(__name__)

# instance واحد بس من كل حاجة، بيتعمل مرة لما السيرفر يشتغل
order_system = OrderSystem()
invoice_system = InvoiceSystem()  # نسخة إحنا شايلينها - مش اللي جوه create_invoice الأصلية


def _order_to_dict(order) -> dict:
    return {
        "order_id": order.order_id,
        "customer_id": order.customer_id,
        "status": order.status,
        "items": [
            {"item_id": i.item_id, "name": i.name, "price": i.price, "quantity": i.quantity}
            for i in order.items
        ],
        "total_price": order.total_price,
    }


def create_order(customer_id: str) -> dict:
    """بيفتح أوردر جديد فاضي لعميل معين."""
    try:
        order = order_system.create_order(customer_id)
        return {"success": True, "data": _order_to_dict(order), "error": None}
    except Exception as e:
        logger.exception(f"Error in create_order: {e}")
        return {"success": False, "data": None, "error": str(e)}


def add_item_to_order(order_id: int, item_id: int, quantity: int) -> dict:
    """بيضيف صنف للأوردر - السعر والاسم بيتجابوا من المنيو الحقيقي، مش من الموديل."""
    try:
        order = order_system.get_order(order_id)
        if order is None:
            return {"success": False, "data": None, "error": "الأوردر ده مش موجود"}

        menu_row = restaurant.menu.menu[restaurant.menu.menu["Item_ID"] == item_id]
        if menu_row.empty:
            return {"success": False, "data": None, "error": "الصنف ده مش موجود في المنيو"}

        name = menu_row.iloc[0]["Item"]
        price = float(menu_row.iloc[0]["Price"])

        ok = order.add_item_to_order(item_id, name, price, quantity)
        if not ok:
            return {"success": False, "data": None, "error": "الكمية غير صحيحة"}

        return {"success": True, "data": _order_to_dict(order), "error": None}
    except Exception as e:
        logger.exception(f"Error in add_item_to_order: {e}")
        return {"success": False, "data": None, "error": str(e)}


def remove_item_from_order(order_id: int, item_id: int) -> dict:
    try:
        order = order_system.get_order(order_id)
        if order is None:
            return {"success": False, "data": None, "error": "الأوردر ده مش موجود"}
        ok = order.remove_item_from_order(item_id)
        error = None if ok else "الصنف ده مش موجود في الأوردر"
        return {"success": ok, "data": _order_to_dict(order) if ok else None, "error": error}
    except Exception as e:
        logger.exception(f"Error in remove_item_from_order: {e}")
        return {"success": False, "data": None, "error": str(e)}


def get_order_status(order_id: int) -> dict:
    try:
        order = order_system.get_order(order_id)
        if order is None:
            return {"success": False, "data": None, "error": "الأوردر ده مش موجود"}
        return {"success": True, "data": {"status": order.get_order_status()}, "error": None}
    except Exception as e:
        logger.exception(f"Error in get_order_status: {e}")
        return {"success": False, "data": None, "error": str(e)}


def update_order_status(order_id: int, status: str) -> dict:
    try:
        order = order_system.get_order(order_id)
        if order is None:
            return {"success": False, "data": None, "error": "الأوردر ده مش موجود"}
        ok = order.update_order_status(status)
        error = None if ok else "حالة غير صحيحة (pending/preparing/ready/delivered/cancelled)"
        return {"success": ok, "data": {"status": order.status} if ok else None, "error": error}
    except Exception as e:
        logger.exception(f"Error in update_order_status: {e}")
        return {"success": False, "data": None, "error": str(e)}


def calculate_invoice(order_id: int) -> dict:
    """بيحسب الفاتورة - بيستخدم InvoiceSystem مباشرة عشان يتفادى باگ الـ ID المكرر."""
    try:
        order = order_system.get_order(order_id)
        if order is None:
            return {"success": False, "data": None, "error": "الأوردر ده مش موجود"}

        invoice = invoice_system.create_invoice(order)
        return {
            "success": True,
            "data": {
                "invoice_id": invoice.invoice_id,
                "order_id": invoice.order_id,
                "subtotal": invoice.subtotal,
                "tax": invoice.tax,
                "discount": invoice.discount,
                "total": invoice.total,
                "payment_status": invoice.payment_status,
            },
            "error": None,
        }
    except Exception as e:
        logger.exception(f"Error in calculate_invoice: {e}")
        return {"success": False, "data": None, "error": str(e)}