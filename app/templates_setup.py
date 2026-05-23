from pathlib import Path
from fastapi.templating import Jinja2Templates

from app.config import settings

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"

TRANSLATIONS = {
    "nav.dashboard": {"en": "Dashboard", "ar": "لوحة التحكم"},
    "nav.campaigns": {"en": "Campaigns", "ar": "الحملات"},
    "nav.settings": {"en": "Settings", "ar": "الإعدادات"},
    "nav.notifications": {"en": "Notifications", "ar": "الإشعارات"},
    "nav.analytics": {"en": "Analytics", "ar": "الإحصائيات"},
    "nav.language": {"en": "Language", "ar": "اللغة"},
    "nav.theme": {"en": "Theme", "ar": "المظهر"},
    "common.logout": {"en": "Logout", "ar": "تسجيل الخروج"},
    "campaign.title": {"en": "Campaigns", "ar": "الحملات"},
    "campaign.add": {"en": "Add Campaign", "ar": "إضافة حملة"},
    "campaign.edit": {"en": "Edit Campaign", "ar": "تعديل الحملة"},
    "campaign.name": {"en": "Name", "ar": "الاسم"},
    "campaign.platform": {"en": "Platform", "ar": "المنصة"},
    "campaign.keywords": {"en": "Keywords", "ar": "الكلمات المفتاحية"},
    "campaign.match_type": {"en": "Match Type", "ar": "نوع المطابقة"},
    "campaign.reply": {"en": "Reply Text", "ar": "نص الرد"},
    "campaign.status": {"en": "Status", "ar": "الحالة"},
    "campaign.actions": {"en": "Actions", "ar": "الإجراءات"},
    "campaign.matched": {"en": "Matched", "ar": "متطابق"},
    "campaign.save": {"en": "Save Campaign", "ar": "حفظ الحملة"},
    "campaign.cancel": {"en": "Cancel", "ar": "إلغاء"},
    "campaign.empty": {"en": "No campaigns yet. Create your first one!", "ar": "لا توجد حملات بعد. أنشئ أول حملة!"},
    "campaign.confirm_delete": {"en": "Are you sure you want to delete this campaign?", "ar": "هل أنت متأكد من حذف هذه الحملة؟"},
    "campaign.match_exact": {"en": "Exact", "ar": "مطابق تام"},
    "campaign.match_contains": {"en": "Contains", "ar": "يحتوي"},
    "campaign.match_regex": {"en": "Regex", "ar": "تعبير منتظم"},
    "campaign.keywords_help": {"en": "Separate keywords with commas", "ar": "افصل الكلمات المفتاحية بفواصل"},
    "settings.title": {"en": "Platform Settings", "ar": "إعدادات المنصة"},
    "settings.instagram": {"en": "Instagram", "ar": "إنستغرام"},
    "settings.facebook": {"en": "Facebook", "ar": "فيسبوك"},
    "settings.app_id": {"en": "App ID", "ar": "معرف التطبيق"},
    "settings.app_secret": {"en": "App Secret", "ar": "سر التطبيق"},
    "settings.access_token": {"en": "Access Token", "ar": "رمز الوصول"},
    "settings.page_id": {"en": "Page ID", "ar": "معرف الصفحة"},
    "settings.ig_user_id": {"en": "IG Business Account ID", "ar": "معرف حساب الأعمال في إنستغرام"},
    "settings.webhook_token": {"en": "Webhook Verify Token", "ar": "رمز التحقق من Webhook"},
    "settings.webhook_url": {"en": "Webhook URL", "ar": "رابط Webhook"},
    "settings.save": {"en": "Save Settings", "ar": "حفظ الإعدادات"},
    "settings.test": {"en": "Test Connection", "ar": "اختبار الاتصال"},
    "notif.title": {"en": "Notifications", "ar": "الإشعارات"},
    "notif.mark_all_read": {"en": "Mark All Read", "ar": "تحديد الكل كمقروء"},
    "notif.filter_all": {"en": "All", "ar": "الكل"},
    "notif.filter_replies": {"en": "Replies", "ar": "الردود"},
    "notif.filter_dms": {"en": "DMs", "ar": "الرسائل"},
    "notif.filter_errors": {"en": "Errors", "ar": "الأخطاء"},
    "notif.empty": {"en": "No notifications yet", "ar": "لا توجد إشعارات بعد"},
    "common.loading": {"en": "Loading...", "ar": "جار التحميل..."},
    "common.cancel": {"en": "Cancel", "ar": "إلغاء"},
    "common.delete": {"en": "Delete", "ar": "حذف"},
    "common.confirm": {"en": "Confirm", "ar": "تأكيد"},
    "share.copy": {"en": "Copy", "ar": "نسخ"},
    "share.copied": {"en": "Copied!", "ar": "تم النسخ!"},
    "share.desc": {"en": "Anyone with this link can see your live auto-reply feed.", "ar": "أي شخص لديه هذا الرابط يمكنه رؤية خلاصة الردود المباشرة."},
    "stats.replies": {"en": "Replies Sent", "ar": "الردود المرسلة"},
    "stats.dms": {"en": "DMs Sent", "ar": "الرسائل المرسلة"},
    "stats.active": {"en": "Active Campaigns", "ar": "الحملات النشطة"},
    "stats.errors": {"en": "Errors", "ar": "الأخطاء"},
    "analytics.title": {"en": "Analytics", "ar": "الإحصائيات"},
    "analytics.chart_title": {"en": "Daily Activity (Last 7 Days)", "ar": "النشاط اليومي (آخر 7 أيام)"},
    "analytics.total_replies": {"en": "Total Replies", "ar": "إجمالي الردود"},
    "analytics.total_dms": {"en": "Total DMs", "ar": "إجمالي الرسائل"},
    "analytics.success_rate": {"en": "Success Rate", "ar": "نسبة النجاح"},
    "analytics.keywords_matched": {"en": "Keywords Matched", "ar": "الكلمات المتطابقة"},
    "login.desc": {"en": "Enter the PIN to access the dashboard", "ar": "أدخل رمز PIN للوصول إلى لوحة التحكم"},
    "login.pin": {"en": "PIN Code", "ar": "رمز PIN"},
    "login.submit": {"en": "Unlock", "ar": "فتح"},
    "login.error": {"en": "Invalid PIN", "ar": "رمز PIN غير صحيح"},
    "topbar.dashboard": {"en": "Dashboard", "ar": "لوحة التحكم"},
    "topbar.campaigns": {"en": "Campaigns", "ar": "الحملات"},
    "topbar.settings": {"en": "Settings", "ar": "الإعدادات"},
    "topbar.notifications": {"en": "Notifications", "ar": "الإشعارات"},
    "topbar.analytics": {"en": "Analytics", "ar": "الإحصائيات"},
    "common.yes": {"en": "Yes", "ar": "نعم"},
    "common.no": {"en": "No", "ar": "لا"},
    "common.close": {"en": "Close", "ar": "إغلاق"},
    "common.error": {"en": "An error occurred", "ar": "حدث خطأ"},
    "common.save": {"en": "Save", "ar": "حفظ"},
}


def t(key: str, lang: str = "en") -> str:
    entry = TRANSLATIONS.get(key)
    if not entry:
        return key
    return entry.get(lang, entry.get("en", key))


templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
templates.env.globals["app_name"] = settings.app_name
templates.env.globals["public_url"] = settings.public_url
templates.env.globals["t"] = t
