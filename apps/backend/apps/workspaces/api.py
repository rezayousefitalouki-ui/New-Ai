from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.text import slugify
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.workspaces.models import Membership, Workspace

User = get_user_model()


class WorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = ("id", "name", "slug", "created_at")
        read_only_fields = ("id", "slug", "created_at")


class MembershipSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Membership
        fields = ("id", "user", "role", "created_at")
        read_only_fields = fields

    def get_user(self, membership):
        return {
            "id": str(membership.user_id),
            "phone": membership.user.phone,
            "first_name": membership.user.first_name,
            "last_name": membership.user.last_name,
        }


def membership_for(user, workspace_id):
    try:
        return Membership.objects.select_related("workspace").get(
            workspace_id=workspace_id,
            user=user,
        )
    except (Membership.DoesNotExist, ValueError):
        return None


def can_manage(membership):
    return bool(
        membership
        and membership.role in (Membership.Role.OWNER, Membership.Role.ADMIN)
    )


class WorkspaceListCreateView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        workspaces = Workspace.objects.filter(
            memberships__user=request.user
        ).order_by("created_at")
        result = []
        for workspace in workspaces:
            membership = membership_for(request.user, workspace.id)
            row = WorkspaceSerializer(workspace).data
            row["role"] = membership.role if membership else None
            result.append(row)
        return Response({"workspaces": result})

    def post(self, request):
        name = str(request.data.get("name", "")).strip()
        if not name or len(name) > 120:
            return Response(
                {"name": ["نام فضا الزامی است و باید حداکثر ۱۲۰ نویسه باشد."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        base = slugify(name)[:60] or f"workspace-{request.user.id.hex[:8]}"
        slug = base
        suffix = 2
        while Workspace.objects.filter(slug=slug).exists():
            slug = f"{base[:70]}-{suffix}"
            suffix += 1
        with transaction.atomic():
            workspace = Workspace.objects.create(name=name, slug=slug)
            Membership.objects.create(
                workspace=workspace,
                user=request.user,
                role=Membership.Role.OWNER,
            )
        row = WorkspaceSerializer(workspace).data
        row["role"] = Membership.Role.OWNER
        return Response({"workspace": row}, status=status.HTTP_201_CREATED)


class WorkspaceDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def patch(self, request, workspace_id):
        membership = membership_for(request.user, workspace_id)
        if not membership:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if membership.role not in (Membership.Role.OWNER, Membership.Role.ADMIN):
            return Response(status=status.HTTP_403_FORBIDDEN)
        name = str(request.data.get("name", "")).strip()
        if not name or len(name) > 120:
            return Response(
                {"name": ["نام معتبر وارد کنید."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        membership.workspace.name = name
        membership.workspace.save(update_fields=("name", "updated_at"))
        row = WorkspaceSerializer(membership.workspace).data
        row["role"] = membership.role
        return Response({"workspace": row})


class WorkspaceMembersView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, workspace_id):
        membership = membership_for(request.user, workspace_id)
        if not membership:
            return Response(status=status.HTTP_404_NOT_FOUND)
        members = Membership.objects.filter(
            workspace_id=workspace_id
        ).select_related("user").order_by("created_at")
        return Response({"members": MembershipSerializer(members, many=True).data})

    def post(self, request, workspace_id):
        actor_membership = membership_for(request.user, workspace_id)
        if not actor_membership:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if not can_manage(actor_membership):
            return Response(status=status.HTTP_403_FORBIDDEN)
        phone = str(request.data.get("phone", "")).strip()
        role = request.data.get("role", Membership.Role.VIEWER)
        allowed_roles = {Membership.Role.EDITOR, Membership.Role.VIEWER}
        if actor_membership.role == Membership.Role.OWNER:
            allowed_roles.add(Membership.Role.ADMIN)
        if role not in allowed_roles:
            return Response(
                {"role": ["نقش انتخاب‌شده برای این کاربر مجاز نیست."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = User.objects.filter(phone=phone, is_active=True).first()
        if not user:
            return Response(
                {"phone": ["کاربری با این شماره پیدا نشد."]},
                status=status.HTTP_404_NOT_FOUND,
            )
        membership, created = Membership.objects.get_or_create(
            workspace=actor_membership.workspace,
            user=user,
            defaults={"role": role},
        )
        if not created:
            return Response(
                {"detail": "این کاربر عضو این فضا است."},
                status=status.HTTP_409_CONFLICT,
            )
        return Response(
            {"member": MembershipSerializer(membership).data},
            status=status.HTTP_201_CREATED,
        )


class WorkspaceMemberDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, workspace_id, membership_id):
        actor_membership = membership_for(request.user, workspace_id)
        if not actor_membership:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if not can_manage(actor_membership):
            return Response(status=status.HTTP_403_FORBIDDEN)
        target = Membership.objects.filter(
            id=membership_id,
            workspace_id=workspace_id,
        ).first()
        if not target:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if target.role == Membership.Role.OWNER:
            return Response(
                {"detail": "مالک فضا را نمی‌توان حذف کرد."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if target.role == Membership.Role.ADMIN and actor_membership.role != Membership.Role.OWNER:
            return Response(status=status.HTTP_403_FORBIDDEN)
        target.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
