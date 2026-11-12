import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from apps.video_studio.models import RenderJob

def _request(path, payload=None):
    if not settings.VIDEO_WORKER_TOKEN:
        raise ValueError("Video render worker token is not configured.")
    headers = {"Authorization": f"Bearer {settings.VIDEO_WORKER_TOKEN}", "Accept": "application/json"}
    data = None
    method = "GET"
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")
        method = "POST"
    request = Request(f"{settings.VIDEO_WORKER_URL}{path}", data=data, headers=headers, method=method)
    try:
        with urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise ValueError("ارتباط با worker ویدیویی ناموفق بود.") from exc

@shared_task
def submit_render(render_id):
    job = RenderJob.objects.select_related("project").filter(id=render_id).first()
    if not job or job.status != RenderJob.Status.QUEUED:
        return
    job.status = RenderJob.Status.RENDERING
    job.started_at = timezone.now()
    job.save(update_fields=("status", "started_at"))
    try:
        _request("/render", {"jobId": str(job.id), "aspectRatio": job.project.aspect_ratio, "storyboard": job.project.storyboard})
    except ValueError as exc:
        job.status = RenderJob.Status.FAILED
        job.error_message = str(exc)[:300]
        job.finished_at = timezone.now()
        job.save(update_fields=("status", "error_message", "finished_at"))

@shared_task
def poll_render(render_id):
    job = RenderJob.objects.select_related("project").filter(id=render_id).first()
    if not job or job.status != RenderJob.Status.RENDERING:
        return
    try:
        state = _request(f"/renders/{job.id}")
    except ValueError as exc:
        job.status = RenderJob.Status.FAILED
        job.error_message = str(exc)[:300]
        job.finished_at = timezone.now()
        job.save(update_fields=("status", "error_message", "finished_at"))
        return
    if state.get("status") == "succeeded":
        job.status = RenderJob.Status.SUCCEEDED
        job.output_url = f"/api/v1/video/renders/{job.id}/file/"
        job.finished_at = timezone.now()
        job.save(update_fields=("status", "output_url", "finished_at"))
    elif state.get("status") == "failed":
        job.status = RenderJob.Status.FAILED
        job.error_message = str(state.get("error") or "رندر ویدیو ناموفق بود.")[:300]
        job.finished_at = timezone.now()
        job.save(update_fields=("status", "error_message", "finished_at"))

@shared_task
def enqueue_render_polls():
    for job_id in RenderJob.objects.filter(status=RenderJob.Status.RENDERING).values_list("id", flat=True):
        poll_render.delay(str(job_id))
