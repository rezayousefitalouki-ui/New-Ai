from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from django.conf import settings
from django.db import transaction
from django.http import StreamingHttpResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.video_studio.models import RenderJob, VideoProject
from apps.video_studio.serializers import RenderJobSerializer, VideoProjectSerializer
from apps.video_studio.tasks import submit_render
from apps.workspaces.models import Membership

def _membership(user, workspace_id):
    try:
        return Membership.objects.get(user=user, workspace_id=workspace_id)
    except (Membership.DoesNotExist, ValueError):
        return None

def _writer(membership):
    return bool(membership and membership.role in (Membership.Role.OWNER, Membership.Role.ADMIN, Membership.Role.EDITOR))

class ProjectListCreateView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        workspace_id = request.query_params.get("workspace_id")
        if not _membership(request.user, workspace_id):
            return Response(status=status.HTTP_404_NOT_FOUND)
        projects = VideoProject.objects.filter(workspace_id=workspace_id)
        renders = RenderJob.objects.filter(project__workspace_id=workspace_id)[:30]
        return Response({"projects": VideoProjectSerializer(projects, many=True).data, "renders": RenderJobSerializer(renders, many=True).data})
    def post(self, request):
        membership = _membership(request.user, request.data.get("workspace_id"))
        if not membership:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if not _writer(membership):
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = VideoProjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        project = serializer.save(workspace=membership.workspace, created_by=request.user)
        return Response({"project": VideoProjectSerializer(project).data}, status=status.HTTP_201_CREATED)

class ProjectDetailView(APIView):
    permission_classes = (IsAuthenticated,)
    def patch(self, request, project_id):
        project = VideoProject.objects.filter(id=project_id, workspace__memberships__user=request.user).first()
        if not project:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if not _writer(_membership(request.user, project.workspace_id)):
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = VideoProjectSerializer(project, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        return Response({"project": VideoProjectSerializer(serializer.save()).data})

class RenderCreateView(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request, project_id):
        project = VideoProject.objects.filter(id=project_id, workspace__memberships__user=request.user).first()
        if not project:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if not _writer(_membership(request.user, project.workspace_id)):
            return Response(status=status.HTTP_403_FORBIDDEN)
        active = RenderJob.objects.filter(project=project, status__in=(RenderJob.Status.QUEUED, RenderJob.Status.RENDERING)).first()
        if active:
            return Response({"render": RenderJobSerializer(active).data}, status=status.HTTP_202_ACCEPTED)
        job = RenderJob.objects.create(project=project)
        transaction.on_commit(lambda: submit_render.delay(str(job.id)))
        return Response({"render": RenderJobSerializer(job).data}, status=status.HTTP_202_ACCEPTED)

class RenderJobListView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        workspace_id = request.query_params.get("workspace_id")
        if not _membership(request.user, workspace_id):
            return Response(status=status.HTTP_404_NOT_FOUND)
        jobs = RenderJob.objects.filter(project__workspace_id=workspace_id)[:30]
        return Response({"renders": RenderJobSerializer(jobs, many=True).data})

class RenderFileView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, render_id):
        job = RenderJob.objects.filter(id=render_id, status=RenderJob.Status.SUCCEEDED, project__workspace__memberships__user=request.user).first()
        if not job:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if not settings.VIDEO_WORKER_TOKEN:
            return Response({"detail": "Video renderer is not configured."}, status=503)
        req = Request(f"{settings.VIDEO_WORKER_URL}/renders/{job.id}/file", headers={"Authorization": f"Bearer {settings.VIDEO_WORKER_TOKEN}"})
        try:
            upstream = urlopen(req, timeout=30)
        except (HTTPError, URLError, TimeoutError):
            return Response({"detail": "Rendered file is unavailable."}, status=502)
        def chunks():
            try:
                while chunk := upstream.read(65536):
                    yield chunk
            finally:
                upstream.close()
        return StreamingHttpResponse(chunks(), content_type="video/mp4", headers={"Content-Disposition": f'attachment; filename="socialmind-{job.id}.mp4"'})
