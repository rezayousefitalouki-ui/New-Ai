# وضعیت توسعه

آخرین به‌روزرسانی: 2026-11-12

## تکمیل‌شده

- [x] معماری Django/DRF، Next.js/TypeScript، PostgreSQL، Redis، Celery و پیکربندی Compose.
- [x] رابط فارسی RTL و صفحات workspace، اعضا، اتصال حساب، تقویم و اینباکس.
- [x] ثبت‌نام/ورود session-based با CSRF، نقش‌های workspace و کنترل دسترسی داده‌ها بر اساس عضویت.
- [x] اتصال Facebook Pages و Instagram حرفه‌ای با OAuth Meta و نگهداری رمزگذاری‌شدهٔ tokenها.
- [x] ساخت پیش‌نویس، زمان‌بندی، مدیریت محتوا و صف انتشار Celery برای مقصدهای انتخاب‌شده.
- [x] انتشار Meta محدود: Facebook Page (متن/عکس) و Instagram (یک تصویر JPEG).
- [x] دریافت پیام/دیدگاه از webhook با HMAC، نگهداری conversation/message، پاسخ‌دادن از UI و حذف اثر تکراری webhook بر شمارندهٔ خوانده‌نشده.
- [x] CI روی GitHub: Django check، migration drift check، pytest، Ruff، TypeScript و production build.

## محدودیت‌ها و نیازهای راه‌اندازی

- برای Meta باید App ID/secret، نسخهٔ Graph، callback مجاز، token encryption key و مجوزهای پذیرفته‌شده پیکربندی شوند.
- webhook باید از HTTPS عمومی در Meta ثبت شود؛ verify token، subscription رویدادها و اتصال Page/حساب هنوز باید در Meta Developer Dashboard انجام شود.
- رسانه باید از نشانی HTTPS عمومی قابل دسترسی باشد؛ بارگذاری مستقیم فایل ویدیو، Instagram Reels و انواع رسانهٔ دیگر هنوز پشتیبانی نمی‌شود.
- inbox فقط گفتگوهایی را نمایش می‌دهد که Meta webhook به اپ ارسال کرده باشد؛ پاسخ‌گویی تابع مجوزها و دسترسی‌های اپ Meta است.
- LinkedIn و YouTube، analytics زنده، AI provider، moderation/automation و پرداخت همچنان فازهای بعدی‌اند.
- ارسال دعوت عضو با ایمیل/SMS به سرویس پیام‌رسانی نیاز دارد؛ فعلاً افزودن کاربران ثبت‌نام‌کرده در دسترس است.

## اعتبارسنجی CI

GitHub Actions روی commit 3f66f741970b1741e47af302ec0dca9480e762bc سبز است: Django checks، migration drift، pytest، Ruff، TypeScript typecheck و production build همگی موفق شدند. این مخزن در این نشست از طریق GitHub و بدون checkout محلی ویرایش شده است.

## ورودی محصول

متن prompt پیوست‌شده در میانهٔ بخش «Analytics Agent» پایان می‌یابد؛ جزئیات پس از آن در دسترس نبود. موارد آینده با توجه به نیازهای موجود و تصاویر مرجع به‌صورت مرحله‌ای تعریف می‌شوند.
