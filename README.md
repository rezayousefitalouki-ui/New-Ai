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

داشبورد و ابزارهای تحلیل/ویدیو هنوز بخش‌هایی از پیش‌نمایش محصول‌اند. تقویم، انتشار محدود Meta و اینباکس برای پیام‌ها/دیدگاه‌های دریافت‌شده، API و مدل داده دارند. برای فعال‌شدن عملیات Meta باید تنظیمات اپ و webhook انجام شود. وضعیت و محدودیت‌ها در [DEVELOPMENT_STATUS.md](DEVELOPMENT_STATUS.md) ثبت شده‌اند.


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

## فاز ۳: محتوا و تقویم

- ایجاد پیش‌نویس و زمان‌بندی پست در workspace، انتخاب حساب‌های متصل، مشاهدهٔ تقویم جلالی و وضعیت انتشار
- مدل محتوا و مقصدهای انتشار با کنترل دسترسی workspace؛ صف زمان‌بندی با Celery Beat
- برای رسانه، نشانی HTTPS عمومی لازم است؛ بارگذاری فایل در این فاز پیاده‌سازی نشده است

## فاز ۴: انتشار اجتماعی

- انتشار متن/عکس در Facebook Page و انتشار یک تصویر JPEG در حساب حرفه‌ای Instagram متصل
- انتشار فوری یا زمان‌بندی‌شده؛ وضعیت نتیجه برای هر مقصد نگهداری می‌شود
- قالب‌های دیگر Instagram، ویدیو/Reels، LinkedIn و YouTube در این فاز پشتیبانی نمی‌شوند
- موفقیت به نسخهٔ Graph API، مجوزهای تأییدشدهٔ اپ، نوع حساب و دسترسی Page بستگی دارد

## فاز ۵: اینباکس

- دریافت پیام و دیدگاه Meta از webhook با بررسی امضای HMAC، ذخیره‌سازی conversation/message و جلوگیری از تکرار پیام‌های وب‌هوک
- نمایش گفتگوها و ارسال پاسخ از حساب متصل؛ فقط گفتگوهایی که webhook دریافت کرده در دسترس‌اند
- webhook عمومی HTTPS را در Meta Developer Dashboard ثبت و حساب‌ها/Pageها را برای فیلدهای لازم subscribe کنید. verify token را در `META_WEBHOOK_VERIFY_TOKEN` و secret همان اپ را در `META_APP_SECRET` قرار دهید.
- قابلیت دسترسی پیام‌رسانی به مجوزهای Meta و review اپ بستگی دارد؛ این فاز subscription حساب‌ها را به‌صورت خودکار فعال نمی‌کند

### راه‌اندازی انتشار و اینباکس Meta

1. `META_APP_ID`، `META_APP_SECRET`، `META_GRAPH_VERSION`، `META_OAUTH_CALLBACK_URI` و `TOKEN_ENCRYPTION_KEY` را تنظیم کنید.
2. در `META_OAUTH_SCOPES` فقط مجوزهای فعال و تأییدشدهٔ اپ Meta خود را وارد کنید؛ برای inbox نیز مجوزهای پیام‌رسانی مربوط به نوع اتصال/حساب را لازم دارید.
3. `META_WEBHOOK_VERIFY_TOKEN` را به یک مقدار محرمانهٔ تصادفی تنظیم کنید و callback عمومی HTTPS زیر را در Meta ثبت کنید: `/api/v1/inbox/webhook/`.
4. رویدادهای پیام/دیدگاه مورد نیاز را در Meta انتخاب کنید و Page/حساب‌های حرفه‌ای را subscribe کنید.
5. worker، celery-beat، PostgreSQL و Redis باید در حال اجرا باشند. قبل از فعال‌کردن انتشار واقعی، دسترسی‌ها و محتوای آزمایشی را در Meta بررسی کنید.

