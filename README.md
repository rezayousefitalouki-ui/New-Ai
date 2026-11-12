# SocialMind AI

پلتفرم فارسی‌محور برای برنامه‌ریزی و تولید محتوای اینستاگرام با هوش مصنوعی.

## راه‌اندازی

پیش‌نیاز: Docker و Docker Compose.

```powershell
Copy-Item .env.example .env
docker compose up --build
```

- وب: http://localhost:3000
- API و OpenAPI: http://localhost:8000/docs
- سلامت API: http://localhost:8000/health/ready
- استودیوی Remotion: http://localhost:3001

مخزن از حالت خالی شروع شده است. وضعیت و محدودیت‌های اجرا در [DEVELOPMENT_STATUS.md](DEVELOPMENT_STATUS.md) ثبت می‌شود.
