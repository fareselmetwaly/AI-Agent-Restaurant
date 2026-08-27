from datetime import datetime  # استيراد مكتبة الوقت والتاريخ
from enum import Enum  # استيراد كلاس Enum لتعريف الثوابت


class ComplaintCategory(Enum):  # كلاس يحدد أنواع/تصنيفات الشكاوى
    LATE_ORDER = "late_order"  # تصنيف: تأخير في الطلب
    WRONG_ORDER = "wrong_order"  # تصنيف: طلب خاطئ
    MISSING_ITEM = "missing_item"  # تصنيف: عنصر مفقود
    FOOD_QUALITY = "food_quality"  # تصنيف: جودة الطعام
    STAFF = "staff"  # تصنيف: مشكلة مع الموظفين
    PAYMENT = "payment"  # تصنيف: مشكلة في الدفع
    OTHER = "other"  # تصنيف: أسباب أخرى


class ComplaintStatus(Enum):  # كلاس يحدد الحالات المختلفة للشكوى
    NEW = "new"  # حالة: شكوى جديدة
    IN_PROGRESS = "in_progress"  # حالة: قيد المعالجة والحل
    RESOLVED = "resolved"  # حالة: تم حل الشكوى
    CLOSED = "closed"  # حالة: تم إغلاق الشكوى


class Complaint:  # كلاس الشكوى المخصص لتخزين بيانات كل شكوى

    def __init__(
        self, complaint_id, customer_id, order_id, message, category
    ):  # دالة بناء الشكوى وتسجيل البيانات الأولية
        self.complaint_id = complaint_id  # حفظ رقم/معرف الشكوى
        self.customer_id = customer_id  # حفظ رقم العميل صاحب الشكوى
        self.order_id = order_id  # حفظ رقم الطلب المتعلق بالشكوى
        self.message = message  # حفظ نص رسالة الشكوى
        self.category = category  # حفظ نوع وتصنيف الشكوى
        self.status = (
            ComplaintStatus.NEW.value
        )  # إعطاء الشكوى حالة افتراضية "جديدة"
        self.created_at = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )  # تسجيل تاريخ ووقت إنشاء الشكوى تلقائياً

    def update_status(self, new_status):  # دالة لتحديث وتغيير حالة الشكوى
        self.status = new_status  # تعيين الحالة الجديدة للشكوى


class Customer:  # كلاس العميل لتخزين بياناته وسجله

    def __init__(
        self, customer_id, name, email
    ):  # دالة بناء العميل وتسجيل بياناته
        self.customer_id = customer_id  # حفظ رقم/معرف العميل
        self.name = name  # حفظ اسم العميل
        self.email = email  # حفظ البريد الإلكتروني للعميل
        self.complaint_history = (
            []
        )  # إنشاء قائمة فارغة لتخزين سجل شكاوى العميل

    def create_complaint(
        self, complaint_id, order_id, message, category
    ):  # دالة لإنشاء شكوى جديدة وإضافتها للعميل
        complaint = Complaint(
            complaint_id, self.customer_id, order_id, message, category
        )  # إنشاء كائن شكوى جديد
        self.complaint_history.append(
            complaint
        )  # إضافة الشكوى إلى قائمة سجل الشكاوى الخاص بالعميل
        return complaint  # إرجاع الشكوى الجديدة لاستخدامها


def analyze_complaint(
    message,
):  # دالة لتحليل نص الشكوى وتحديد نوعها تلقائياً
    message_lower = message.lower()  # تحويل جميع الحروف إلى حروف صغيرة للسهولة

    if (
        "late" in message_lower or "delay" in message_lower
    ):  # فحص وجود كلمات تعبر عن التأخير
        return (
            ComplaintCategory.LATE_ORDER.value
        )  # إرجاع التصنيف: تأخير في الطلب
    elif (
        "wrong" in message_lower or "incorrect" in message_lower
    ):  # فحص وجود كلمات تعبر عن خطأ الطلب
        return ComplaintCategory.WRONG_ORDER.value  # إرجاع التصنيف: طلب خاطئ
    elif (
        "missing" in message_lower or "forgot" in message_lower
    ):  # فحص وجود كلمات تعبر عن عناصر مفقودة
        return (
            ComplaintCategory.MISSING_ITEM.value
        )  # إرجاع التصنيف: عنصر مفقود
    elif (
        "cold" in message_lower or "quality" in message_lower
    ):  # فحص وجود كلمات تعبر عن جودة الطعام
        return (
            ComplaintCategory.FOOD_QUALITY.value
        )  # إرجاع التصنيف: جودة الطعام
    else:  # في حالة عدم تطابق أي كلمة مفتاحية
        return ComplaintCategory.OTHER.value  # إرجاع التصنيف: أخرى


# === تجربة وتنفيذ الكود ===

customer1 = Customer(
    customer_id="CUST101", name="Ahmed Ali", email="ahmed@example.com"
)  # إنشاء عميل جديد
message_text = "My food arrived late and cold"  # تحديد نص الشكوى للتجربة
detected_category = analyze_complaint(
    message_text
)  # تحليل الرسالة وتحديد تصنيفها تلقائياً

new_complaint = customer1.create_complaint(  # إنشاء الشكوى وتسجيلها للعميل
    complaint_id="CMP1001",  # تحديد معرف الشكوى
    order_id="ORD5501",  # تحديد معرف الطلب
    message=message_text,  # إرسال النص
    category=detected_category,  # إرسال التصنيف المستخرج
)

new_complaint.update_status(
    ComplaintStatus.IN_PROGRESS.value
)  # تحديث حالة الشكوى إلى "قيد المعالجة"

print(
    "=== Customer History & Complaint Details ==="
)  # طباعة عنوان النتيجة في الشاشة
print(f"Customer ID: {customer1.customer_id}")  # طباعة رقم العميل
print(f"Complaint ID: {new_complaint.complaint_id}")  # طباعة رقم الشكوى
print(f"Message: {new_complaint.message}")  # طباعة نص الشكوى
print(f"Category: {new_complaint.category}")  # طباعة نوع/تصنيف الشكوى
print(f"Status: {new_complaint.status}")  # طباعة حالة الشكوى الحالية
print(
    f"Created At: {new_complaint.created_at}"
)  # طباعة وقت وتاريخ إنشاء الشكوى