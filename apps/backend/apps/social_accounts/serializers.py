from rest_framework import serializers

from apps.social_accounts.models import SocialAccount


class SocialAccountSerializer(serializers.ModelSerializer):
    token_expires_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = SocialAccount
        fields = (
            "id",
            "platform",
            "external_id",
            "display_name",
            "username",
            "token_expires_at",
            "granted_scopes",
            "status",
            "created_at",
        )
        read_only_fields = fields
