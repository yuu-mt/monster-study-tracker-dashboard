from django.urls import path
from .views import (
    CurriculumChapterListView,
    TraineeListView,
    TraineeDetailView,
    TraineeRegisterView,
)

urlpatterns = [
    # カリキュラムマスタ
    path("curriculum/chapters/", CurriculumChapterListView.as_view(), name="curriculum-chapters"),

    # 受講生
    path("trainees/", TraineeListView.as_view(), name="trainee-list"),
    path("trainees/register/", TraineeRegisterView.as_view(), name="trainee-register"),
    path("trainees/<int:pk>/", TraineeDetailView.as_view(), name="trainee-detail"),
]