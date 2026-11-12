from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from apps.accounts.models import User
from apps.workspaces.models import Membership, Workspace


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "phone", "email", "first_name", "last_name", "date_joined")
        read_only_fields = ("id", "phone", "date_joined")


class RegistrationSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=16)
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    workspace_name = serializers.CharField(max_length=120)

    def validate_phone(self, value):
        field = User._meta.get_field("phone")
        field.run_validators(value)
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("این شماره قبلاً ثبت شده است.")
        return value

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages)) from exc
        return value

    def create(self, validated_data):
        from django.db import transaction
        from django.utils.text import slugify
        import uuid

        with transaction.atomic():
            password = validated_data.pop("password")
            workspace_name = validated_data.pop("workspace_name")
            user = User.objects.create_user(password=password, **validated_data)
            base_slug = slugify(workspace_name)[:60] or f"workspace-{uuid.uuid4().hex[:8]}"
            slug = base_slug
            while Workspace.objects.filter(slug=slug).exists():
                slug = f"{base_slug[:65]}-{uuid.uuid4().hex[:6]}"
            workspace = Workspace.objects.create(name=workspace_name, slug=slug)
            Membership.objects.create(
                workspace=workspace, user=user, role=Membership.Role.OWNER
            )
        return user
