from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ai_engine.models import AIGeneration, BrandProfile
from apps.ai_engine.serializers import AIGenerationSerializer, BrandProfileSerializer
from apps.ai_engine.tasks import run_generation
from apps.workspaces.models import Membership


def _membership(user, workspace_id):
    try:
        return Membership.objects.get(user=user, workspace_id=workspace_id)
    except (Membership.DoesNotExist, ValueError):
        return None


def _writer(membership):
    return bool(membership and membership.role in (Membership.Role.OWNER, Membership.Role.ADMIN, Membership.Role.EDITOR))


class BrandProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        workspace_id = request.query_params.get("workspace_id")
        membership = _membership(request.user, workspace_id)
        if not membership:
            return Response(status=status.HTTP_404_NOT_FOUND)
        profile, _ = BrandProfile.objects.get_or_create(workspace=membership.workspace)
        return Response({"brand": BrandProfileSerializer(profile).data})

    def patch(self, request):
        workspace_id = request.data.get("workspace_id")
        membership = _membership(request.user, workspace_id)
        if not membership:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if not _writer(membership):
            return Response(status=status.HTTP_403_FORBIDDEN)
        profile, _ = BrandProfile.objects.get_or_create(workspace=membership.workspace)
        serializer = BrandProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        return Response({"brand": BrandProfileSerializer(serializer.save()).data})


class GenerationListCreateView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        workspace_id = request.query_params.get("workspace_id")
        if not _membership(request.user, workspace_id):
            return Response(status=status.HTTP_404_NOT_FOUND)
        rows = AIGeneration.objects.filter(workspace_id=workspace_id)[:30]
        return Response({"generations": AIGenerationSerializer(rows, many=True).data})

    def post(self, request):
        workspace_id = request.data.get("workspace_id")
        membership = _membership(request.user, workspace_id)
        if not membership:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if not _writer(membership):
            return Response(status=status.HTTP_403_FORBIDDEN)
        kind = request.data.get("kind")
        brief = str(request.data.get("brief") or "").strip()
        if kind not in AIGeneration.Kind.values:
            return Response({"kind": ["نوع تولید پشتیبانی نمی‌شود."]}, status=status.HTTP_400_BAD_REQUEST)
        if not brief or len(brief) > 5000:
            return Response({"brief": ["شرح درخواست الزامی است و حداکثر ۵۰۰۰ نویسه دارد."]}, status=status.HTTP_400_BAD_REQUEST)
        generation = AIGeneration.objects.create(
            workspace=membership.workspace,
            created_by=request.user,
            kind=kind,
            brief=brief,
        )
        run_generation.delay(str(generation.id))
        return Response({"generation": AIGenerationSerializer(generation).data}, status=status.HTTP_202_ACCEPTED)


class GenerationDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, generation_id):
        generation = AIGeneration.objects.filter(
            id=generation_id,
            workspace__memberships__user=request.user,
        ).first()
        if not generation:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response({"generation": AIGenerationSerializer(generation).data})
