from celery import shared_task
from django.utils import timezone

from apps.ai_engine.models import AIGeneration, BrandProfile
from apps.ai_engine.provider import ProviderError, generate


@shared_task
def run_generation(generation_id):
    generation = AIGeneration.objects.select_related("workspace").filter(id=generation_id).first()
    if not generation or generation.status in (AIGeneration.Status.SUCCEEDED, AIGeneration.Status.FAILED):
        return
    generation.status = AIGeneration.Status.RUNNING
    generation.error_message = ""
    generation.save(update_fields=("status", "error_message", "updated_at"))
    brand = BrandProfile.objects.filter(workspace=generation.workspace).first() or BrandProfile(workspace=generation.workspace)
    try:
        result, model, usage = generate(generation.kind, generation.brief, brand)
    except ProviderError as exc:
        generation.status = AIGeneration.Status.FAILED
        generation.error_message = str(exc)[:300]
    else:
        generation.status = AIGeneration.Status.SUCCEEDED
        generation.result = result
        generation.provider_model = model[:120]
        generation.usage_tokens = usage if isinstance(usage, int) and usage >= 0 else None
    generation.updated_at = timezone.now()
    generation.save(update_fields=("status", "error_message", "result", "provider_model", "usage_tokens", "updated_at"))
