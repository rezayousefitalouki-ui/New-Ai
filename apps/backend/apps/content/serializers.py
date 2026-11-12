from urllib.parse import urlsplit

from rest_framework import serializers

from apps.content.models import Post, PostTarget
from apps.social_accounts.models import SocialAccount


class PostTargetSerializer(serializers.ModelSerializer):
    platform = serializers.CharField(source="social_account.platform", read_only=True)
    account_name = serializers.CharField(source="social_account.display_name", read_only=True)
    username = serializers.CharField(source="social_account.username", read_only=True)

    class Meta:
        model = PostTarget
        fields = (
            "id",
            "platform",
            "account_name",
            "username",
            "status",
            "remote_id",
            "error_message",
            "attempts",
            "published_at",
        )


class PostSerializer(serializers.ModelSerializer):
    targets = PostTargetSerializer(many=True, read_only=True)
    social_account_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Post
        fields = (
            "id",
            "caption",
            "media_urls",
            "status",
            "scheduled_at",
            "published_at",
            "created_at",
            "updated_at",
            "targets",
            "social_account_ids",
        )
        read_only_fields = (
            "id",
            "status",
            "published_at",
            "created_at",
            "updated_at",
            "targets",
        )

    def validate_media_urls(self, value):
        if not isinstance(value, list) or len(value) > 10:
            raise serializers.ValidationError("حداکثر ۱۰ نشانی رسانه وارد کنید.")
        for url in value:
            parts = urlsplit(str(url))
            if parts.scheme != "https" or not parts.netloc or parts.username or parts.password:
                raise serializers.ValidationError(
                    "رسانه باید روی یک نشانی عمومی HTTPS میزبانی شده باشد."
                )
        return value

    def validate_scheduled_at(self, value):
        if value is not None and value <= __import__("django.utils.timezone", fromlist=["now"]).now():
            raise serializers.ValidationError("زمان زمان‌بندی باید در آینده باشد.")
        return value

    def validate(self, attrs):
        account_ids = attrs.get("social_account_ids")
        if account_ids is None and self.instance:
            return attrs
        workspace = self.context["workspace"]
        accounts = SocialAccount.objects.filter(
            workspace=workspace,
            status=SocialAccount.Status.CONNECTED,
            id__in=account_ids or [],
        )
        if accounts.count() != len(set(account_ids or [])):
            raise serializers.ValidationError(
                {"social_account_ids": "فقط حساب‌های متصل همین فضای کاری قابل انتخاب‌اند."}
            )
        attrs["_accounts"] = list(accounts)
        if attrs.get("scheduled_at") and not accounts and not self.instance:
            raise serializers.ValidationError(
                {"social_account_ids": "برای زمان‌بندی، دست‌کم یک حساب متصل انتخاب کنید."}
            )
        return attrs

    def create(self, validated_data):
        accounts = validated_data.pop("_accounts", [])
        validated_data.pop("social_account_ids", None)
        post = Post.objects.create(
            workspace=self.context["workspace"],
            created_by=self.context["request"].user,
            status=Post.Status.SCHEDULED if validated_data.get("scheduled_at") else Post.Status.DRAFT,
            **validated_data,
        )
        for account in accounts:
            PostTarget.objects.create(post=post, social_account=account)
        return post

    def update(self, instance, validated_data):
        accounts = validated_data.pop("_accounts", None)
        validated_data.pop("social_account_ids", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        if "scheduled_at" in validated_data:
            instance.status = Post.Status.SCHEDULED if instance.scheduled_at else Post.Status.DRAFT
        instance.save()
        if accounts is not None:
            PostTarget.objects.filter(post=instance).delete()
            for account in accounts:
                PostTarget.objects.create(post=instance, social_account=account)
        return instance
