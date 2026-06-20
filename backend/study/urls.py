from django.urls import path
from .views import (
    CategoryListView,
    StudyRecordListCreateView,
    StudyRecordDetailView,
    StudySummaryView,
    StampView,
    WeeklyChartView,
    WeeklyRankingView,
    FriendRecordListView,
    FriendSummaryView,
    TotalSummaryView,
    MonthlyChartView,
)

urlpatterns = [
    # カテゴリー一覧
    path('categories/', CategoryListView.as_view(), name='categories'),
    # 学習記録一覧・新規作成
    path('records/', StudyRecordListCreateView.as_view(), name='study_records'),
    path('friends/<int:user_id>/records/', FriendRecordListView.as_view(), name='friend_records'),
    path('friends/<int:user_id>/summary/', FriendSummaryView.as_view(), name='friend_summary'),
    # 学習記録詳細・更新・削除
    path('records/<int:pk>/', StudyRecordDetailView.as_view(), name='study_record_detail'),
    # 学習時間集計
    path('summary/', StudySummaryView.as_view(), name='study_summary'),
    # スタンプ
    path('records/<int:record_id>/stamp/', StampView.as_view(), name='stamp'),
    path('weekly-chart/', WeeklyChartView.as_view(), name='weekly_chart'),
    path('ranking/', WeeklyRankingView.as_view(), name='weekly_ranking'),
    path('total-summary/', TotalSummaryView.as_view(), name='total_summary'),
    path('monthly-chart/', MonthlyChartView.as_view(), name='monthly_chart'),
]
