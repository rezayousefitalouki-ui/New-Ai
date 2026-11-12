from rest_framework import serializers

from apps.ai_engine.models import AIGeneration, BrandProfile


class BrandProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandProfile
        fields = ("id", "business_name", "industry", "products", "audience", "voice", "preferred_topics", "forbidden_terms", "updated_at")
        read_only_fields = ("id", "updated_at")

    def validate_preferred_topics(self, value):
        if not isinstance(value, list) or len(value) > 20 or any(not isinstance(v, str) or len(v) > 100 for v in value):
            raise serializers.ValidationError("حداکثر ۲۰ موضوع کوتاه وارد کنید.")
        return value

    def validate_forbidden_terms(self, value):
        if not isinstance(value, list) or len(value) > 50 or any(not isinstance(v, str) or len(v) > 100 for v in value):
            raise serializers.ValidationError("حداکثر ۵۰ عبارت کوتاه وارد کنید.")
        return value


class AIGenerationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIGeneration
        fields = ("id", "kind", "brief", "status", "result", "provider_model", "usage_tokens", "error_message", "created_at", "updated_at")
        read_only_fields = ("id", "status", "result", "provider_model", "usage_tokens", "error_message", "created_at", "updated_at")
