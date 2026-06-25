from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404

from .models import CurriculumChapter, TraineeProfile
from .serializers import (
    CurriculumChapterSerializer,
    TraineeListSerializer,
    TraineeDetailSerializer,
    TraineeRegisterSerializer,
)


# 1. カリキュラムマスタAPI

class CurriculumChapterListView(generics.ListAPIView):
    """
    GET /api/curriculum/chapters/
    アクティブな章を order 順に返す（小項目ネスト済み）
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CurriculumChapterSerializer

    def get_queryset(self):
        return (
            CurriculumChapter.objects
            .prefetch_related("items")
            .order_by("display_order")
        )


# 2. 受講生一覧API

class TraineeListView(generics.ListAPIView):
    """
    GET /api/trainees/
    インストラクター（is_staff）のみアクセス可。
    クエリパラメータ:
    - status: active / completed / on_hold
    - instructor: instructor の user_id
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = TraineeListSerializer

    def get_queryset(self):
        qs = TraineeProfile.objects.select_related("user", "mentor").all()  # instructor → mentor

        status_param = self.request.query_params.get("status")
        if status_param:
            qs = qs.filter(status=status_param)

        mentor_param = self.request.query_params.get("mentor")  # instructor → mentor
        if mentor_param:
            qs = qs.filter(mentor__id=mentor_param)

        return qs.order_by("start_date")

# 3. 受講生詳細API

class TraineeDetailView(generics.RetrieveAPIView):
    """
    GET /api/trainees/<id>/
    章別進捗・小項目進捗をネストして返す
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = TraineeDetailSerializer

    def get_queryset(self):
        return TraineeProfile.objects.select_related("user", "mentor").prefetch_related(
            "chapter_progresses__chapter",
        )

# 4. 受講生登録API

class TraineeRegisterView(APIView):
    """
    POST /api/trainees/register/
    User + TraineeProfile を同時作成する
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        serializer = TraineeRegisterSerializer(data=request.data)
        if serializer.is_valid():
            profile = serializer.save()
            return Response(
                TraineeDetailSerializer(profile).data,
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)