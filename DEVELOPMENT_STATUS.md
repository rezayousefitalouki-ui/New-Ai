# وضعیت توسعه

آخرین به‌روزرسانی: 2026-11-12

## تکمیل‌شده
- [x] بررسی مخزن و ثبت معماری آغازین.
- [x] رابط فارسی RTL با داشبورد، اینباکس، تقویم جلالی، تحلیل و استودیوی ویدیو بر پایهٔ تصاویر مرجع.
- [x] تم تیره و روشن، Next.js App Router و پیکربندی Tailwind/shadcn و TanStack Query.
- [x] جایگزینی طرح FastAPI با Django؛ اضافه‌شدن settings تفکیک‌شده، DRF، کاربر سفارشی موبایل‌محور، workspace/membership، Django Admin، health endpoint و migrationهای اولیه.
- [x] پیکربندی PostgreSQL، Redis، Celery/Beat و Nginx در Compose.

## در حال انجام
- [ ] اجرای Docker Compose و بررسی migrations و buildها از checkout محلی.
- [ ] بازبینی دستی صفحه‌ها در مرورگر در ابعاد desktop/mobile و اصلاح ریزه‌کاری‌های RTL.

## معوق
- [ ] اجرای واقعی تست‌ها و رفع خطاهای احتمالی؛ این نشست checkout اجرایی ندارد.
- [ ] تکمیل احراز هویت و session/CSRF امن، workspace authorization و تست‌های tenant isolation.
- [ ] تکمیل APIهای feature و اتصال عملی frontend به آن‌ها.
- [ ] اتصال رسمی Meta، AI provider/LangGraph، صف‌های دامنه‌ای، انتشار و پرداخت.
- [ ] تکمیل فایل‌های باقیماندهٔ ساختار production و مستندات امنیت/استقرار.

## محدودیت ورودی
فایل prompt جدید دریافتی در میانهٔ بخش «Analytics Agent» پایان می‌یابد؛ بخش‌های بعدی آن در دسترس نیستند. تصمیم‌های این مرحله بر تعریف محصول، stack Django، ساختار repo و نیازهای UI/UX موجود در فایل متکی‌اند.

## نتایج اجرا
هیچ build، migration یا تستی در این نشست اجرا نشده است؛ ابزار GitHub امکان خواندن/نوشتن remote را دارد اما checkout محلی پروژه موجود نیست. رابط‌ها نمونهٔ طراحی‌اند و داده‌های شبکه، تحلیل، پیام، انتشار و AI عملیاتی نیستند.

## گام بعد
Checkout شاخهٔ `phase-0/foundation`، اجرای Compose، pytest و build/typecheck فرانت، سپس رفع خطاها و تکمیل فاز ۰ پیش از گسترش featureها.
