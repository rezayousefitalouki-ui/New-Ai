# نمای معماری

SocialMind AI به‌صورت monorepo با API ماژولار و runtimeهای جدا برای وب و رندر ویدیو توسعه می‌یابد. Docker Compose محیط توسعهٔ محلی است، نه پیکربندی production.

## مرزبندی

- `apps/api/app/api`: قراردادهای HTTP و health checks
- `apps/api/app/core`: تنظیمات و اجزای مشترک
- `apps/api/app/db`: مدل‌ها، session و migrations
- دامنه‌های آینده: auth، workspaces، billing، Instagram، content و publishing
- `apps/web`: رابط Persian-first با RTL
- `video-engine/remotion`: compositionهای از پیش تعریف‌شده؛ JSON معتبر storyboard به composition نگاشت می‌شود و کد تولیدشده اجرا نمی‌شود.

منطق دامنه از framework و provider جدا می‌ماند. همهٔ داده‌های متعلق به مشتری workspace-scoped هستند؛ workspace باید از عضویت معتبر سمت سرور تعیین شود. OAuth tokenها، پرداخت و اعتبار نیازمند کنترل دسترسی، audit و تراکنش‌اند.

## زمان و کارهای پس‌زمینه

Timestampها UTC و timezone-aware هستند؛ تقویم جلالی فقط نمایش است. درخواست HTTP نباید رندر ویدیو را اجرا کند. صف‌های Celery/Redis و worker مجزای Node در مرحلهٔ پردازش پس‌زمینه تکمیل می‌شوند.

## تصمیم‌های باز

مجوزهای دقیق Meta به نوع حساب و تأیید Meta وابسته‌اند. انتخاب AI provider، S3، درگاه‌های پرداخت و observability پس از تعیین الزامات استقرار انجام می‌شود.
