"""
Tools حوالين team_code/customer_complaint.py.
قاعدة أساسية زي الملفات التانية: معدلش أي سطر في كود الفريق.

فجوات في كودهم بنسدها هنا بس (من غير ما نلمس ملفهم):
    1. مفيش CustomerSystem بيمسك ويدور على العملاء - عملنا dict محلي.
    2. مفيش توليد تلقائي لـ complaint_id - عملنا counter بسيط.
    3. update_status مفيهاش أي validation - بنتحقق إحنا ضد
       ComplaintStatus قبل ما ننادي عليها.

كل tool بيرجع نفس الشكل الموحد:
    {"success": bool, "data": ..., "error": Optional[str]}
"""

import itertools
import logging

from tasks.team_code.customer_complaint import Customer, ComplaintStatus, analyze_complaint

logger = logging.getLogger(__name__)

# تسجيل العملاء - كود الفريق مفيهوش نظام بيمسك العملاء، فبنمسكهم إحنا هنا
_customers: dict[str, Customer] = {}
_complaint_id_counter = itertools.count(1)


def _complaint_to_dict(complaint) -> dict:
    return {
        "complaint_id": complaint.complaint_id,
        "customer_id": complaint.customer_id,
        "order_id": complaint.order_id,
        "message": complaint.message,
        "category": complaint.category,
        "status": complaint.status,
        "created_at": complaint.created_at,
    }


def register_customer(customer_id: str, name: str, email: str) -> dict:
    """بيسجل عميل جديد (أو بيرجع الموجود لو already مسجل)."""
    try:
        if customer_id not in _customers:
            _customers[customer_id] = Customer(customer_id, name, email)
        c = _customers[customer_id]
        return {
            "success": True,
            "data": {"customer_id": c.customer_id, "name": c.name, "email": c.email},
            "error": None,
        }
    except Exception as e:
        logger.exception(f"Error in register_customer: {e}")
        return {"success": False, "data": None, "error": str(e)}


def get_customer_history(customer_id: str) -> dict:
    """بيرجع كل شكاوى العميل ده اللي اتسجلت قبل كده."""
    try:
        customer = _customers.get(customer_id)
        if customer is None:
            return {"success": False, "data": None, "error": "العميل ده مش مسجل"}
        history = [_complaint_to_dict(c) for c in customer.complaint_history]
        return {"success": True, "data": history, "error": None}
    except Exception as e:
        logger.exception(f"Error in get_customer_history: {e}")
        return {"success": False, "data": None, "error": str(e)}


def log_complaint(customer_id: str, order_id: str, message: str) -> dict:
    """بيسجل شكوى جديدة - التصنيف بيتحدد تلقائيًا من نص الشكوى."""
    try:
        customer = _customers.get(customer_id)
        if customer is None:
            return {"success": False, "data": None, "error": "العميل ده مش مسجل، سجله الأول"}

        category = analyze_complaint(message)
        complaint_id = next(_complaint_id_counter)

        complaint = customer.create_complaint(
            complaint_id=complaint_id, order_id=order_id, message=message, category=category
        )
        return {"success": True, "data": _complaint_to_dict(complaint), "error": None}
    except Exception as e:
        logger.exception(f"Error in log_complaint: {e}")
        return {"success": False, "data": None, "error": str(e)}


def _find_complaint(customer_id: str, complaint_id):
    customer = _customers.get(customer_id)
    if customer is None:
        return None
    for c in customer.complaint_history:
        if c.complaint_id == complaint_id:
            return c
    return None


def update_complaint_status(customer_id: str, complaint_id, new_status: str) -> dict:
    """بيحدث حالة الشكوى - بيتحقق من القيمة الأول عشان كودهم مبيتحققش."""
    try:
        valid_statuses = [s.value for s in ComplaintStatus]
        if new_status not in valid_statuses:
            return {
                "success": False,
                "data": None,
                "error": f"حالة غير صحيحة، لازم تكون واحدة من: {valid_statuses}",
            }

        complaint = _find_complaint(customer_id, complaint_id)
        if complaint is None:
            return {"success": False, "data": None, "error": "الشكوى دي مش موجودة"}

        complaint.update_status(new_status)
        return {"success": True, "data": _complaint_to_dict(complaint), "error": None}
    except Exception as e:
        logger.exception(f"Error in update_complaint_status: {e}")
        return {"success": False, "data": None, "error": str(e)}


def get_complaint_status(customer_id: str, complaint_id) -> dict:
    try:
        complaint = _find_complaint(customer_id, complaint_id)
        if complaint is None:
            return {"success": False, "data": None, "error": "الشكوى دي مش موجودة"}
        return {"success": True, "data": {"status": complaint.status}, "error": None}
    except Exception as e:
        logger.exception(f"Error in get_complaint_status: {e}")
        return {"success": False, "data": None, "error": str(e)}