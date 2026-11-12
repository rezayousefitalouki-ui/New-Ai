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
