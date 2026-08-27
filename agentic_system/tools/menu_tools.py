"""
Tools حوالين team_code/menu_table_reservation.py.
قاعدة أساسية: الملف ده معدلش ولا سطر في كود الفريق - بس بينادي عليه
أو بيقرا الـ attributes العامة بتاعته مباشرة.

كل tool بيرجع نفس الشكل الموحد:
    {"success": bool, "data": ..., "error": Optional[str]}
"""

import logging

from tasks.team_code.menu_table_reservation import Restaurant

logger = logging.getLogger(__name__)

# instance واحد بس بيتعمل مرة لما السيرفر يشتغل، وكل الـ tools بتتعامل معاه
# TODO: عدّل الاسم وعدد الطرابيزات لما يبقى عندنا القيم الحقيقية
restaurant = Restaurant(name="AI Restaurant", number_of_tables=10)


def get_menu() -> dict:
    """يرجع المنيو بالكامل."""
    try:
        return {"success": True, "data": restaurant.menu.menu.to_dict(orient="records"), "error": None}
    except Exception as e:
        logger.exception(f"Error in get_menu: {e}")
        return {"success": False, "data": None, "error": str(e)}


def search_menu_item(item_name: str) -> dict:
    """بيدور على صنف في المنيو بالاسم (بحث جزئي، case-insensitive)."""
    try:
        df = restaurant.menu.menu
        result = df[df["Item"].str.contains(item_name, case=False, na=False)]
        return {"success": True, "data": result.to_dict(orient="records"), "error": None}
    except Exception as e:
        logger.exception(f"Error in search_menu_item: {e}")
        return {"success": False, "data": None, "error": str(e)}


def get_menu_by_category(category: str) -> dict:
    """يرجع كل أصناف تصنيف معين (Pizza, Burger, Sandwich, Fries)."""
    try:
        df = restaurant.menu.menu
        result = df[df["Category"].str.lower() == category.lower()]
        return {"success": True, "data": result.to_dict(orient="records"), "error": None}
    except Exception as e:
        logger.exception(f"Error in get_menu_by_category: {e}")
        return {"success": False, "data": None, "error": str(e)}


def check_table_availability(number_of_people: int) -> dict:
    """بيدور على أقرب طرابيزة فاضية تكفي العدد ده، من غير ما يحجزها."""
    try:
        table = restaurant.find_available_table(number_of_people)
        if table is None:
            return {"success": True, "data": None, "error": None}
        return {
            "success": True,
            "data": {"table_id": table.table_id, "capacity": table.capacity, "status": table.status},
            "error": None,
        }
    except Exception as e:
        logger.exception(f"Error in check_table_availability: {e}")
        return {"success": False, "data": None, "error": str(e)}


def get_available_tables() -> dict:
    """يرجع كل الطرابيزات الفاضية دلوقتي."""
    try:
        available = [
            {"table_id": t.table_id, "capacity": t.capacity, "status": t.status}
            for t in restaurant.tables.values()
            if t.status == "available"
        ]
        return {"success": True, "data": available, "error": None}
    except Exception as e:
        logger.exception(f"Error in get_available_tables: {e}")
        return {"success": False, "data": None, "error": str(e)}


def make_reservation(customer_id: str, date: str, time: str, number_of_people: int) -> dict:
    """بيحجز طرابيزة فعليًا لو فيه واحدة فاضية تكفي العدد."""
    try:
        reservation = restaurant.make_reservation(
            customer_id=customer_id, date=date, time=time, number_of_people=number_of_people
        )
        if reservation is None:
            return {"success": False, "data": None, "error": "لا يوجد طرابيزة متاحة لهذا العدد من الأشخاص"}
        return {
            "success": True,
            "data": {
                "reservation_id": reservation.reservation_id,
                "table_id": reservation.table_id,
                "date": reservation.date,
                "time": reservation.time,
                "number_of_people": reservation.number_of_people,
                "status": reservation.status,
            },
            "error": None,
        }
    except Exception as e:
        logger.exception(f"Error in make_reservation: {e}")
        return {"success": False, "data": None, "error": str(e)}


def cancel_reservation(reservation_id: int) -> dict:
    """بيلغي حجز موجود، ويرجع الطرابيزة فاضية تاني."""
    try:
        success = restaurant.cancel_reservation(reservation_id)
        error = None if success else "الحجز غير موجود أو ملغي بالفعل"
        return {"success": success, "data": None, "error": error}
    except Exception as e:
        logger.exception(f"Error in cancel_reservation: {e}")
        return {"success": False, "data": None, "error": str(e)}