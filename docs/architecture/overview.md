# معماری SocialMind AI

## پایه

محصول یک monorepo با Django modular monolith برای عملیات کسب‌وکار، Next.js برای رابط کاربر و workerهای جدا برای کارهای پس‌زمینه است. Django ORM منبع اصلی persistence است. FastAPI و ORM دوم بخشی از معماری آغازین نیستند.

## مرزها

- `apps/backend/config`: تنظیمات environment، URL و Celery
- `apps/backend/apps/accounts`: کاربر سفارشی با شمارهٔ موبایل
- `apps/backend/apps/workspaces`: workspace و عضویت
- سایر اپ‌های Django در فازهای بعد برای Instagram، analytics، content، billing و publishing اضافه می‌شوند.
- `apps/frontend`: App Router، مسیرهای کاربردی، اجزای مشترک و API client
- `video-engine/remotion`: compositionهای از پیش تعریف‌شده برای رندر امن
- PostgreSQL، Redis، Celery و Nginx در Docker Compose توسعهٔ محلی

## امنیت tenant

هر دادهٔ متعلق به مشتری باید workspace-scoped باشد. workspace از عضویت تاییدشدهٔ کاربر استخراج می‌شود و نباید به شناسهٔ ارسال‌شده از مرورگر اعتماد کرد. دسترسی‌ها در selectors/services و permissionهای DRF محدود می‌شوند؛ migration فعلی فقط اسکلت workspace و membership را ایجاد می‌کند و هنوز workflow مجوزدهی کامل نشده است.

## زمان و localization

زبان رابط فارسی، جهت RTL و timezone نمایشی Asia/Tehran است. پایگاه داده timestampهای timezone-aware ذخیره می‌کند. تاریخ جلالی فقط برای نمایش/برنامه‌ریزی است و canonical timestamp نیست.

## مرزهای ادغام

Meta، درگاه‌های پرداخت، providerهای مدل زبانی و object storage از طریق آداپترها اضافه می‌شوند. تا دریافت credential، پاسخ‌ها و داده‌ها mock یا خالی می‌مانند و نباید عملیات موفق وانمود شود. کد storyboard فقط JSON اعتبارسنجی‌شده می‌پذیرد؛ اجرای JavaScript تولیدشده توسط مدل مجاز نیست.
