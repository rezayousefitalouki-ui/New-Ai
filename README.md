# SocialMind AI

پلتفرم فارسی‌محور مدیریت و تولید محتوای اینستاگرام با هوش مصنوعی.

## معماری آغازین

- `apps/backend`: Django 5.2، DRF، Django ORM، PostgreSQL و Celery
- `apps/frontend`: Next.js App Router، TypeScript، Tailwind CSS، shadcn/ui و رابط راست‌چین
- `video-engine/remotion`: استودیوی اولیهٔ Remotion
- `infrastructure/nginx`: reverse proxy برای اجرای محلی

## اجرا

پیش‌نیاز: Docker Engine و Docker Compose.

```powershell
Copy-Item .env.example .env
docker compose up --build
```

- رابط فارسی: http://localhost:3000
- ورودی Nginx: http://localhost:8080
- API health: http://localhost:8000/api/v1/health/live/
- Django Admin: http://localhost:8000/admin/
- Remotion Studio: http://localhost:3001

اکنون صفحه‌های داشبورد، اینباکس، تقویم، تحلیل و استودیوی ویدیو پیش‌نمایش رابط‌اند؛ تا اتصال OAuth و سرویس‌ها، داده و عملیات واقعی نمایش/اجرا نمی‌شوند. برای وضعیت دقیق و محدودیت‌ها فایل [DEVELOPMENT_STATUS.md](DEVELOPMENT_STATUS.md) را ببینید.


## فازهای ۱ و ۲: هویت، فضای کاری و اتصال حساب

- ثبت‌نام با شماره و گذرواژه، ورود با session کوکی امن، CSRF، خروج و اطلاعات پروفایل
- ساخت و تغییر نام workspace، نمایش فضاهای عضو، نقش‌های مالک/مدیر/ویرایشگر/بیننده، افزودن کاربر موجود و مدیریت عضویت
- اتصال Facebook Pages و حساب‌های حرفه‌ای Instagram از مسیر OAuth رسمی Meta؛ توکن‌ها سمت سرور رمزگذاری می‌شوند و هرگز در API به مرورگر برگردانده نمی‌شوند
- حذف دسترسی محلی SocialMind از صفحهٔ اتصال‌ها؛ این کار مجوز برنامه را در Meta لغو نمی‌کند

### فعال‌سازی Meta برای توسعه

1. از اپ Meta خودتان شناسه و secret بسازید، محصول Facebook Login را فعال کنید و callback زیر را دقیقاً به فهرست مجاز Redirect URI اضافه کنید: `http://localhost:8000/api/v1/social-accounts/oauth/meta/callback/`.
2. `META_GRAPH_VERSION` را روی نسخهٔ Graph API فعال در اپ خود تنظیم کنید.
3. `META_OAUTH_SCOPES` را با مجوزهایی که در اپ شما فعال و تأیید شده‌اند پر کنید. مجوزها بر اساس مسیر ورود، نوع حساب Instagram و سطح دسترسی اپ متفاوت‌اند؛ مقدار نمونه عمداً خالی است.
4. کلید رمزگذاری توکن بسازید و در `.env` قرار دهید:

```powershell
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

بدون App ID، secret، نسخهٔ Graph، callback، مجوزها و کلید رمزگذاری، دکمهٔ اتصال API با پاسخ «تنظیمات کامل نیست» غیرفعال می‌ماند. افزودن عضو فعلاً فقط برای حساب ثبت‌نام‌شده است؛ ارسال دعوت پیامکی/ایمیلی به سرویس ارسال نیاز دارد.
