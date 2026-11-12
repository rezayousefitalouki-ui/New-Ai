from rest_framework import serializers

from apps.analytics.models import AccountSnapshot, MediaSnapshot


class AccountSnapshotSerializer(serializers.ModelSerializer):
    account_id = serializers.UUIDField(source="social_account_id")
    account_name = serializers.CharField(source="social_account.display_name")
    username = serializers.CharField(source="social_account.username")

    class Meta:
        model = AccountSnapshot
        fields = ("id", "account_id", "account_name", "username", "followers_count", "media_count", "captured_at")


class MediaSnapshotSerializer(serializers.ModelSerializer):
    account_name = serializers.CharField(source="social_account.display_name")

    class Meta:
        model = MediaSnapshot
        fields = ("id", "remote_media_id", "account_name", "caption", "media_type", "permalink", "published_at", "like_count", "comments_count", "fetched_at")
