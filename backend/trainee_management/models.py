from django.db import models
from django.conf import settings


class CurriculumChapter(models.Model):
    """カリキュラム章マスタ"""
    chapter_number = models.CharField(
        max_length=10,
        unique=True,
        verbose_name='章番号',
        help_text='例: 00, 01, 12（文字列で管理）'
    )
    title = models.CharField(max_length=200, verbose_name='章タイトル')
    estimated_days = models.PositiveIntegerField(
        default=0,
        verbose_name='想定日数',
        help_text='アラート判定・完了予定日の自動算出に使用'
    )
    display_order = models.PositiveIntegerField(verbose_name='表示順')

    class Meta:
        ordering = ['display_order']
        verbose_name = 'カリキュラム章'
        verbose_name_plural = 'カリキュラム章一覧'

    def __str__(self):
        return f'第{self.chapter_number}章 {self.title}'


class CurriculumItem(models.Model):
    """カリキュラム小項目マスタ（章ごとの学習項目）"""
    chapter = models.ForeignKey(
        CurriculumChapter,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='章'
    )
    item_number = models.CharField(
        max_length=10,
        verbose_name='項目番号',
        help_text='例: 01, 02, 00-1, 00-2'
    )
    title = models.CharField(max_length=200, verbose_name='項目名')
    display_order = models.PositiveIntegerField(verbose_name='表示順')

    class Meta:
        ordering = ['chapter__display_order', 'display_order']
        unique_together = ('chapter', 'item_number')
        verbose_name = 'カリキュラム小項目'
        verbose_name_plural = 'カリキュラム小項目一覧'

    def __str__(self):
        return f'{self.chapter.chapter_number}-{self.item_number} {self.title}'


class TraineeProfile(models.Model):
    """受講生プロフィール（accounts.Userとの1対1対応）"""
    STATUS_NOT_STARTED = 'not_started'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'

    STATUS_CHOICES = [
        (STATUS_NOT_STARTED, '未受講'),
        (STATUS_IN_PROGRESS, '受講中'),
        (STATUS_COMPLETED, '完了'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='trainee_profile',
        verbose_name='受講生ユーザー'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NOT_STARTED,
        verbose_name='ステータス'
    )
    mentor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mentees',
        verbose_name='担当メンバー',
        help_text='主なフォロー担当の連絡窓口。閲覧権限はすべての講師に付与されるため、アクセス制限の意味は持たない'
    )
    start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='学習開始日',
        help_text='ステータスを「受講中」に変更する際に手動入力する'
    )
    expected_completion_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='完了予定日',
        help_text='学習開始日 + 全章の想定日数合計（90日）で自動算出'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '受講生プロフィール'
        verbose_name_plural = '受講生プロフィール一覧'

    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username}（{self.get_status_display()}）'

    @property
    def is_delayed(self):
        """アラート判定：完了予定日から1日超過で遅延とみなす（固定ルール）"""
        from datetime import date, timedelta
        if self.status != self.STATUS_IN_PROGRESS:
            return False
        if not self.expected_completion_date:
            return False
        return date.today() > self.expected_completion_date + timedelta(days=1)


class ChapterProgress(models.Model):
    """受講生ごとの章別進捗"""
    trainee = models.ForeignKey(
        TraineeProfile,
        on_delete=models.CASCADE,
        related_name='chapter_progresses',
        verbose_name='受講生'
    )
    chapter = models.ForeignKey(
        CurriculumChapter,
        on_delete=models.PROTECT,  # 進捗が存在する章は削除不可（要件3-3-d）
        related_name='progresses',
        verbose_name='章'
    )
    is_completed = models.BooleanField(default=False, verbose_name='完了フラグ')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完了日時')
    total_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name='累計学習時間（分）',
        help_text='study_recordsから集計したキャッシュ値。study_record保存時に自動更新される'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('trainee', 'chapter')
        verbose_name = '章別進捗'
        verbose_name_plural = '章別進捗一覧'

    def __str__(self):
        status = '✅' if self.is_completed else '🔄'
        return f'{status} {self.trainee} / {self.chapter}'

    @property
    def is_delayed(self):
        """この章が遅延しているか（完了予定日 + 1日 を超過かつ未完了）"""
        from datetime import date, timedelta
        if self.is_completed:
            return False
        chapter_deadline = self._calc_chapter_deadline()
        if not chapter_deadline:
            return False
        return date.today() > chapter_deadline + timedelta(days=1)

    def _calc_chapter_deadline(self):
        """章ごとの完了予定日を算出（受講生の開始日 + その章までの累計想定日数）"""
        if not self.trainee.start_date:
            return None
        from datetime import timedelta
        chapters_before = CurriculumChapter.objects.filter(
            display_order__lte=self.chapter.display_order
        ).order_by('display_order')
        total_days = sum(c.estimated_days for c in chapters_before)
        return self.trainee.start_date + timedelta(days=total_days)


class ItemProgress(models.Model):
    """受講生ごとの小項目別学習時間（章別進捗の内訳）"""
    trainee = models.ForeignKey(
        TraineeProfile,
        on_delete=models.CASCADE,
        related_name='item_progresses',
        verbose_name='受講生'
    )
    curriculum_item = models.ForeignKey(
        CurriculumItem,
        on_delete=models.PROTECT,
        related_name='progresses',
        verbose_name='カリキュラム小項目'
    )
    total_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name='累計学習時間（分）',
        help_text='study_recordsから集計したキャッシュ値'
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('trainee', 'curriculum_item')
        verbose_name = '小項目別学習時間'
        verbose_name_plural = '小項目別学習時間一覧'

    def __str__(self):
        return f'{self.trainee} / {self.curriculum_item} : {self.total_minutes}分'
