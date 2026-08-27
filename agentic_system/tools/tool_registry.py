"""
مكان واحد بيجمع كل الـ tools من كل الملفات، ويجهزها بشكل الموديل بيفهمه
(OpenAI-style function calling، متوافق مع Groq).

لإضافة جزء جديد (orders / customer) لما يوصل كود الفريق:
    1. اعمل الـ wrapper بتاعه في ملفه (زي menu_tools.py)
    2. import للملف هنا تحت
    3. ضيف الـ schemas بتاعته في TOOL_DEFINITIONS
باقي النظام (agent.py) مبيتلمسش خالص.
"""

from agentic_system.tools import menu_tools
from agentic_system.tools import orders_tools
from agentic_system.tools import customer_tools


TOOL_DEFINITIONS = [
    {
        "schema": {
            "type": "function",
            "function": {
                "name": "get_menu",
                "description": "يرجع كل المنيو بالكامل (كل الأصناف والأسعار).",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        },
        "function": menu_tools.get_menu,
    },
    {
        "schema": {
            "type": "function",
            "function": {
                "name": "search_menu_item",
                "description": "يبحث عن صنف معين في المنيو بالاسم أو جزء منه.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "item_name": {"type": "string", "description": "اسم الصنف أو جزء منه"}
                    },
                    "required": ["item_name"],
                },
            },
        },
        "function": menu_tools.search_menu_item,
    },
    {
        "schema": {
            "type": "function",
            "function": {
                "name": "get_menu_by_category",
                "description": "يرجع كل أصناف تصنيف معين زي Pizza أو Burger أو Sandwich أو Fries.",
                "parameters": {
                    "type": "object",
                    "properties": {"category": {"type": "string"}},
                    "required": ["category"],
                },
            },
        },
        "function": menu_tools.get_menu_by_category,
    },
    {
        "schema": {
            "type": "function",
            "function": {
                "name": "check_table_availability",
                "description": "يشيك هل فيه طرابيزة فاضية تكفي عدد أشخاص معين، من غير ما يحجزها.",
                "parameters": {
                    "type": "object",
                    "properties": {"number_of_people": {"type": "integer"}},
                    "required": ["number_of_people"],
                },
            },
        },
        "function": menu_tools.check_table_availability,
    },
    {
        "schema": {
            "type": "function",
            "function": {
                "name": "get_available_tables",
                "description": "يرجع كل الطرابيزات الفاضية دلوقتي.",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        },
        "function": menu_tools.get_available_tables,
    },
    {
        "schema": {
            "type": "function",
            "function": {
                "name": "make_reservation",
                "description": "بيحجز طرابيزة فعليًا لعميل في تاريخ ووقت معين وعدد أشخاص معين.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {"type": "string"},
                        "date": {"type": "string", "description": "بصيغة DD/MM/YYYY"},
                        "time": {"type": "string", "description": "مثال: 07:00 PM"},
                        "number_of_people": {"type": "integer"},
                    },
                    "required": ["customer_id", "date", "time", "number_of_people"],
                },
            },
        },
        "function": menu_tools.make_reservation,
    },
    {
        "schema": {
            "type": "function",
            "function": {
                "name": "cancel_reservation",
                "description": "بيلغي حجز موجود بمعرفه.",
                "parameters": {
                    "type": "object",
                    "properties": {"reservation_id": {"type": "integer"}},
                    "required": ["reservation_id"],
                },
            },
        },
        "function": menu_tools.cancel_reservation,
    },
    {
        "schema": {
            "type": "function",
            "function": {
                "name": "create_order",
                "description": "بيفتح أوردر جديد فاضي لعميل معين.",
                "parameters": {
                    "type": "object",
                    "properties": {"customer_id": {"type": "string"}},
                    "required": ["customer_id"],
                },
            },
        },
        "function": orders_tools.create_order,
    },
    {
        "schema": {
            "type": "function",
            "function": {
                "name": "add_item_to_order",
                "description": "يضيف صنف من المنيو لأوردر موجود، بالسعر الحقيقي من المنيو.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order_id": {"type": "integer"},
                        "item_id": {"type": "integer", "description": "Item_ID زي ما هو في المنيو"},
                        "quantity": {"type": "integer"},
                    },
                    "required": ["order_id", "item_id", "quantity"],
                },
            },
        },
        "function": orders_tools.add_item_to_order,
    },
    {
        "schema": {
            "type": "function",
            "function": {
                "name": "remove_item_from_order",
                "description": "يشيل صنف من أوردر موجود.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order_id": {"type": "integer"},
                        "item_id": {"type": "integer"},
                    },
                    "required": ["order_id", "item_id"],
                },
            },
        },
        "function": orders_tools.remove_item_from_order,
    },
    {
        "schema": {
            "type": "function",
            "function": {
                "name": "get_order_status",
                "description": "يرجع حالة أوردر معين.",
                "parameters": {
                    "type": "object",
                    "properties": {"order_id": {"type": "integer"}},
                    "required": ["order_id"],
                },
            },
        },
        "function": orders_tools.get_order_status,
    },
    {
        "schema": {
            "type": "function",
            "function": {
                "name": "calculate_invoice",
                "description": "يحسب فاتورة نهائية لأوردر معين (subtotal, tax, discount, total).",
                "parameters": {
                    "type": "object",
                    "properties": {"order_id": {"type": "integer"}},
                    "required": ["order_id"],
                },
            },
        },
        "function": orders_tools.calculate_invoice,
    },
    {
        "schema": {
            "type": "function",
            "function": {
                "name": "register_customer",
                "description": "يسجل عميل جديد (اسم وإيميل) قبل أي تفاعل تاني معاه.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {"type": "string"},
                        "name": {"type": "string"},
                        "email": {"type": "string"},
                    },
                    "required": ["customer_id", "name", "email"],
                },
            },
        },
        "function": customer_tools.register_customer,
    },
    {
        "schema": {
            "type": "function",
            "function": {
                "name": "log_complaint",
                "description": "يسجل شكوى جديدة لعميل مسجل، والتصنيف بيتحدد تلقائيًا من نص الشكوى.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {"type": "string"},
                        "order_id": {"type": "string"},
                        "message": {"type": "string"},
                    },
                    "required": ["customer_id", "order_id", "message"],
                },
            },
        },
        "function": customer_tools.log_complaint,
    },
    {
        "schema": {
            "type": "function",
            "function": {
                "name": "get_customer_history",
                "description": "يرجع كل شكاوى عميل معين اللي اتسجلت قبل كده.",
                "parameters": {
                    "type": "object",
                    "properties": {"customer_id": {"type": "string"}},
                    "required": ["customer_id"],
                },
            },
        },
        "function": customer_tools.get_customer_history,
    },
]


def get_tool_schemas() -> list:
    """الشكل اللي بيتبعت للموديل مع كل رسالة."""
    return [t["schema"] for t in TOOL_DEFINITIONS]


def get_tool_function(name: str):
    """بيرجع الـ python function الحقيقية بناءً على اسم الـ tool اللي الموديل طلبه."""
    for t in TOOL_DEFINITIONS:
        if t["schema"]["function"]["name"] == name:
            return t["function"]
    return None