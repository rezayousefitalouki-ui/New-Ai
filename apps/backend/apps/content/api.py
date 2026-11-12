from django.db import transaction
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.content.models import Post, PostTarget
from apps.content.serializers import PostSerializer
from apps.content.tasks import publish_post
from apps.workspaces.models import Membership


def _membership(user, workspace_id):
    try:
        return Membership.objects.get(user=user, workspace_id=workspace_id)
    except (Membership.DoesNotExist, ValueError):
        return None


def _writer(membership):
    return bool(
        membership
        and membership.role in (
            Membership.Role.OWNER,
            Membership.Role.ADMIN,
            Membership.Role.EDITOR,
        )
    )


class PostListCreateView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        workspace_id = request.query_params.get("workspace_id")
        if not _membership(request.user, workspace_id):
            return Response(status=status.HTTP_404_NOT_FOUND)
        posts = Post.objects.filter(workspace_id=workspace_id).prefetch_related(
            "targets__social_account"
        )
        start = request.query_params.get("start")
        end = request.query_params.get("end")
        if start:
            parsed = parse_datetime(start)
            if parsed:
                posts = posts.filter(scheduled_at__gte=parsed)
        if end:
            parsed = parse_datetime(end)
            if parsed:
                posts = posts.filter(scheduled_at__lt=parsed)
        return Response({"posts": PostSerializer(posts[:200], many=True).data})

    def post(self, request):
        workspace_id = request.data.get("workspace_id")
        membership = _membership(request.user, workspace_id)
        if not membership:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if not _writer(membership):
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = PostSerializer(
            data=request.data,
            context={"workspace": membership.workspace, "request": request},
        )
        serializer.is_valid(raise_exception=True)
        return Response(
            {"post": PostSerializer(serializer.save()).data},
            status=status.HTTP_201_CREATED,
        )


class PostDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def _get(self, request, post_id):
        post = Post.objects.prefetch_related("targets__social_account").filter(
            id=post_id
        ).first()
        if not post or not _membership(request.user, post.workspace_id):
            return None
        return post

    def get(self, request, post_id):
        post = self._get(request, post_id)
        if not post:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response({"post": PostSerializer(post).data})

    def patch(self, request, post_id):
        post = self._get(request, post_id)
        if not post:
            return Response(status=status.HTTP_404_NOT_FOUND)
        membership = _membership(request.user, post.workspace_id)
        if not _writer(membership):
            return Response(status=status.HTTP_403_FORBIDDEN)
        if post.status not in (Post.Status.DRAFT, Post.Status.SCHEDULED, Post.Status.FAILED):
            return Response(
                {"detail": "این محتوا در وضعیت فعلی قابل ویرایش نیست."},
                status=status.HTTP_409_CONFLICT,
            )
        serializer = PostSerializer(
            post,
            data=request.data,
            partial=True,
            context={"workspace": post.workspace, "request": request},
        )
        serializer.is_valid(raise_exception=True)
        return Response({"post": PostSerializer(serializer.save()).data})

    def delete(self, request, post_id):
        post = self._get(request, post_id)
        if not post:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if not _writer(_membership(request.user, post.workspace_id)):
            return Response(status=status.HTTP_403_FORBIDDEN)
        if post.status in (Post.Status.PUBLISHING, Post.Status.PUBLISHED):
            return Response(
                {"detail": "محتوای در حال انتشار یا منتشرشده حذف نمی‌شود."},
                status=status.HTTP_409_CONFLICT,
            )
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PostActionView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, post_id):
        post = Post.objects.prefetch_related("targets__social_account").filter(
            id=post_id
        ).first()
        if not post:
            return Response(status=status.HTTP_404_NOT_FOUND)
        membership = _membership(request.user, post.workspace_id)
        if not membership:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if not _writer(membership):
            return Response(status=status.HTTP_403_FORBIDDEN)
        action = request.data.get("action")
        if action == "publish":
            if not post.targets.exists():
                return Response(
                    {"detail": "برای انتشار یک یا چند حساب متصل انتخاب کنید."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if post.status == Post.Status.PUBLISHING:
                return Response({"detail": "این محتوا در حال انتشار است."}, status=409)
            if post.status == Post.Status.PUBLISHED:
                return Response({"detail": "این محتوا قبلاً منتشر شده است."}, status=409)
            PostTarget.objects.filter(
                post=post,
                status=PostTarget.Status.FAILED,
            ).update(status=PostTarget.Status.QUEUED)
            post.status = Post.Status.PUBLISHING
            post.save(update_fields=("status", "updated_at"))
            transaction.on_commit(lambda: publish_post.delay(str(post.id)))
            return Response({"status": post.status}, status=status.HTTP_202_ACCEPTED)
        if action == "cancel":
            if post.status not in (Post.Status.DRAFT, Post.Status.SCHEDULED, Post.Status.FAILED):
                return Response({"detail": "این محتوا قابل لغو نیست."}, status=409)
            post.status = Post.Status.CANCELLED
            post.save(update_fields=("status", "updated_at"))
            return Response({"status": post.status})
        return Response({"action": ["عملیات پشتیبانی نمی‌شود."]}, status=400)
