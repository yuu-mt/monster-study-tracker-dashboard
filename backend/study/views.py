from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from .models import Category, StudyRecord, Stamp
from .serializers import CategorySerializer, StudyRecordSerializer, StampSerializer


class CategoryListView(generics.ListAPIView):
    """カテゴリー一覧取得API"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class StudyRecordListCreateView(generics.ListCreateAPIView):
    """学習記録一覧取得・新規作成API"""
    serializer_class = StudyRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = StudyRecord.objects.filter(user=self.request.user)
        # カテゴリーで絞り込み
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__name=category)
        return queryset

    def perform_create(self, serializer):
        record = serializer.save(user=self.request.user)
        
        from .slack import check_milestone, check_monster_evolution
        from django.db.models import Sum
        from django.utils import timezone

        # 全期間の累計（モンスター進化用）
        total_all = StudyRecord.objects.filter(
            user=self.request.user
        ).aggregate(total=Sum('duration_minutes'))['total'] or 0
        prev_total_all = total_all - record.duration_minutes

        # 今月の累計（マイルストーン通知用）
        today = timezone.now().date()
        month_start = today.replace(day=1)
        total_monthly = StudyRecord.objects.filter(
            user=self.request.user,
            study_date__gte=month_start,
            study_date__lte=today
        ).aggregate(total=Sum('duration_minutes'))['total'] or 0
        prev_total_monthly = total_monthly - record.duration_minutes

        # マイルストーン通知（月間）
        check_milestone(self.request.user, prev_total_monthly, total_monthly)

        # モンスター進化通知（全期間）
        check_monster_evolution(self.request.user, prev_total_all, total_all)

class StudyRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    """学習記録詳細・更新・削除API"""
    serializer_class = StudyRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # 自分の記録のみ操作可能
        return StudyRecord.objects.filter(user=self.request.user)
    
    def perform_update(self, serializer):
        from .slack import check_monster_evolution, check_milestone
        from django.db.models import Sum
        from django.utils import timezone

        # 更新前の累計
        prev_total_all = StudyRecord.objects.filter(
            user=self.request.user
        ).aggregate(total=Sum('duration_minutes'))['total'] or 0

        # 今月の更新前累計
        today = timezone.now().date()
        month_start = today.replace(day=1)
        prev_total_monthly = StudyRecord.objects.filter(
            user=self.request.user,
            study_date__gte=month_start,
            study_date__lte=today
        ).aggregate(total=Sum('duration_minutes'))['total'] or 0

        serializer.save()

        # 更新後の累計
        new_total_all = StudyRecord.objects.filter(
            user=self.request.user
        ).aggregate(total=Sum('duration_minutes'))['total'] or 0

        # 今月の更新後累計
        new_total_monthly = StudyRecord.objects.filter(
            user=self.request.user,
            study_date__gte=month_start,
            study_date__lte=today
        ).aggregate(total=Sum('duration_minutes'))['total'] or 0

        # マイルストーン通知（月間）
        check_milestone(self.request.user, prev_total_monthly, new_total_monthly)

        # モンスター進化通知（全期間）
        check_monster_evolution(self.request.user, prev_total_all, new_total_all)

class StudySummaryView(APIView):
    """学習時間集計API（週間・月間）"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()

        # 週間集計（今日から7日前）
        week_start = today - timedelta(days=6)
        weekly = StudyRecord.objects.filter(
            user=request.user,
            study_date__gte=week_start,
            study_date__lte=today
        ).aggregate(total=Sum('duration_minutes'))

        # 月間集計（今月1日から今日）
        month_start = today.replace(day=1)
        monthly = StudyRecord.objects.filter(
            user=request.user,
            study_date__gte=month_start,
            study_date__lte=today
        ).aggregate(total=Sum('duration_minutes'))

        # 連続学習日数
        streak = self.calculate_streak(request.user, today)

        return Response({
            'weekly_minutes': weekly['total'] or 0,
            'monthly_minutes': monthly['total'] or 0,
            'streak_days': streak,
        })

    def calculate_streak(self, user, today):
        streak = 0
        check_date = today
        while True:
            exists = StudyRecord.objects.filter(
                user=user,
                study_date=check_date
            ).exists()
            if exists:
                streak += 1
                check_date -= timedelta(days=1)
            else:
                break
        return streak


class StampView(APIView):
    """スタンプ送信・取り消しAPI"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, record_id):
        try:
            record = StudyRecord.objects.get(id=record_id)
        except StudyRecord.DoesNotExist:
            return Response({'error': '記録が見つかりません'}, status=status.HTTP_404_NOT_FOUND)

        stamp_type = request.data.get('stamp_type', 'good')
        stamp, created = Stamp.objects.get_or_create(
            from_user=request.user,
            study_record=record,
            defaults={'stamp_type': stamp_type}
        )

        if created:
            return Response({'message': 'スタンプを送りました', 'stamp_type': stamp_type}, status=status.HTTP_201_CREATED)
        else:
            # すでにスタンプ済みなら取り消し
            stamp.delete()
            return Response({'message': 'スタンプを取り消しました'}, status=status.HTTP_200_OK)

class WeeklyChartView(APIView):
    """週間グラフ用データAPI"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        result = []

        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            total = StudyRecord.objects.filter(
            user=request.user,
            study_date=date
        ).aggregate(total=Sum('duration_minutes'))['total'] or 0

            result.append({
                'date': date.strftime('%m/%d'),
                'minutes': total
        })

        return Response(result)
    
class WeeklyRankingView(APIView):
    """週間学習時間ランキングAPI（友達と自分）"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from accounts.models import Friendship
        today = timezone.now().date()
        week_start = today - timedelta(days=6)

        # 友達のIDリストを取得
        friend_ids = Friendship.objects.filter(
            from_user=request.user
        ).values_list('to_user_id', flat=True)

        # 自分と友達を合わせたユーザーリスト
        from django.contrib.auth import get_user_model
        User = get_user_model()
        users = User.objects.filter(
            id__in=list(friend_ids) + [request.user.id]
        )

        ranking = []
        for user in users:
            total = StudyRecord.objects.filter(
                user=user,
                study_date__gte=week_start,
                study_date__lte=today
            ).aggregate(total=Sum('duration_minutes'))['total'] or 0

            ranking.append({
                'user_id': user.id,
                'username': user.username,
                'weekly_minutes': total,
                'is_me': user.id == request.user.id,
            })

        # 学習時間で降順ソート
        ranking.sort(key=lambda x: x['weekly_minutes'], reverse=True)

        # 順位を追加
        for i, item in enumerate(ranking):
            item['rank'] = i + 1

        return Response(ranking)
    
class FriendRecordListView(generics.ListAPIView):
    """友達の学習記録一覧取得API"""
    serializer_class = StudyRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        from accounts.models import Friendship
        user_id = self.kwargs['user_id']

        # 友達かどうか確認
        is_friend = Friendship.objects.filter(
            from_user=self.request.user,
            to_user_id=user_id
        ).exists()

        if not is_friend:
            return StudyRecord.objects.none()
        
        return StudyRecord.objects.filter(
            user_id=user_id
        ).order_by('-study_date')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
class FriendSummaryView(APIView):
    """友達の学習集計API"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        from accounts.models import Friendship
        # 友達かどうか確認
        is_friend = Friendship.objects.filter(
            from_user=request.user,
            to_user_id=user_id
        ).exists()

        if not is_friend:
            return Response({'error': '友達ではありません'}, status=status.HTTP_403_FORBIDDEN)

        today = timezone.now().date()
        week_start = today - timedelta(days=6)
        month_start = today.replace(day=1)

        weekly = StudyRecord.objects.filter(
            user_id=user_id,
            study_date__gte=week_start,
            study_date__lte=today
        ).aggregate(total=Sum('duration_minutes'))['total'] or 0

        monthly = StudyRecord.objects.filter(
            user_id=user_id,
            study_date__gte=month_start,
            study_date__lte=today
        ).aggregate(total=Sum('duration_minutes'))['total'] or 0

        # 連続学習日数
        streak = 0
        check_date = today
        while True:
            exists = StudyRecord.objects.filter(
                user_id=user_id,
                study_date=check_date
            ).exists()
            if exists:
                streak += 1
                check_date -= timedelta(days=1)
            else:
                break

        return Response({
            'weekly_minutes': weekly,
            'monthly_minutes': monthly,
            'streak_days': streak,
        })

class TotalSummaryView(APIView):
    """全期間累計学習時間API"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        total = StudyRecord.objects.filter(
            user=request.user
        ).aggregate(total=Sum('duration_minutes'))['total'] or 0

        return Response({'total_minutes': total})
    
class MonthlyChartView(APIView):
    """月別学習時間グラフAPI"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from django.db.models import Sum
        from django.db.models.functions import TruncMonth

        results = (
            StudyRecord.objects
            .filter(user=request.user)
            .annotate(month=TruncMonth('study_date'))
            .values('month')
            .annotate(total=Sum('duration_minutes'))
            .order_by('month')
        )

        data = []
        for r in results:
            data.append({
                'month': r['month'].strftime('%Y/%m'),
                'minutes': r['total'] or 0,
            })

        return Response(data)