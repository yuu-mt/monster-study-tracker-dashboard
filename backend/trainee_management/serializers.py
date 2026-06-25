from rest_framework import serializers
from .models import (
    CurriculumChapter,
    CurriculumItem,
    TraineeProfile,
    ChapterProgress,
    ItemProgress,
)
from django.contrib.auth import get_user_model

User = get_user_model()


# ──────────────────────────────────────────
# カリキュラムマスタ
# ──────────────────────────────────────────

class CurriculumItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurriculumItem
        fields = [
            "id",
            "chapter",
            "item_number",
            "title",
            "display_order",
        ]


class CurriculumChapterSerializer(serializers.ModelSerializer):
    items = CurriculumItemSerializer(many=True, read_only=True)

    class Meta:
        model = CurriculumChapter
        fields = [
            "id",
            "chapter_number",
            "title",
            "estimated_days",
            "display_order",
            "items",
        ]


# ──────────────────────────────────────────
# 受講生一覧
# ──────────────────────────────────────────

class TraineeListSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    full_name = serializers.SerializerMethodField()
    email = serializers.EmailField(source="user.email", read_only=True)
    overall_progress_percent = serializers.SerializerMethodField()
    is_delayed = serializers.BooleanField(read_only=True)

    class Meta:
        model = TraineeProfile
        fields = [
            "id",
            "user_id",
            "username",
            "full_name",
            "email",
            "status",
            "start_date",
            "expected_completion_date",
            "mentor",
            "overall_progress_percent",
            "is_delayed",
        ]

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

    def get_overall_progress_percent(self, obj):
        total = CurriculumChapter.objects.count()
        if total == 0:
            return 0
        completed = ChapterProgress.objects.filter(
            trainee=obj,
            is_completed=True,
        ).count()
        return round(completed / total * 100)


# ──────────────────────────────────────────
# 受講生詳細
# ──────────────────────────────────────────

class ItemProgressSerializer(serializers.ModelSerializer):
    item_title = serializers.CharField(source="curriculum_item.title", read_only=True)
    item_number = serializers.CharField(source="curriculum_item.item_number", read_only=True)
    display_order = serializers.IntegerField(source="curriculum_item.display_order", read_only=True)

    class Meta:
        model = ItemProgress
        fields = [
            "id",
            "curriculum_item",
            "item_number",
            "item_title",
            "display_order",
            "total_minutes",
        ]


class ChapterProgressSerializer(serializers.ModelSerializer):
    chapter_number = serializers.CharField(source="chapter.chapter_number", read_only=True)
    chapter_title = serializers.CharField(source="chapter.title", read_only=True)
    display_order = serializers.IntegerField(source="chapter.display_order", read_only=True)
    is_delayed = serializers.BooleanField(read_only=True)
    item_progresses = serializers.SerializerMethodField()

    class Meta:
        model = ChapterProgress
        fields = [
            "id",
            "chapter",
            "chapter_number",
            "chapter_title",
            "display_order",
            "is_completed",
            "completed_at",
            "total_minutes",
        ]

class ChapterProgressSerializer(serializers.ModelSerializer):
    chapter_number = serializers.CharField(source="chapter.chapter_number", read_only=True)
    chapter_title = serializers.CharField(source="chapter.title", read_only=True)
    display_order = serializers.IntegerField(source="chapter.display_order", read_only=True)
    is_delayed = serializers.BooleanField(read_only=True)
    item_progresses = serializers.SerializerMethodField()

    class Meta:
        model = ChapterProgress
        fields = [
            "id",
            "chapter",
            "chapter_number",
            "chapter_title",
            "display_order",
            "is_completed",
            "completed_at",
            "total_minutes",
            "is_delayed",
            "item_progresses",
        ]

    def get_item_progresses(self, obj):
        items = ItemProgress.objects.filter(
            trainee=obj.trainee,
            curriculum_item__chapter=obj.chapter,
        ).select_related("curriculum_item").order_by("curriculum_item__display_order")
        return ItemProgressSerializer(items, many=True).data


class TraineeDetailSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    full_name = serializers.SerializerMethodField()
    email = serializers.EmailField(source="user.email", read_only=True)
    is_delayed = serializers.BooleanField(read_only=True)
    chapter_progresses = ChapterProgressSerializer(many=True, read_only=True)

    class Meta:
        model = TraineeProfile
        fields = [
            "id",
            "user_id",
            "username",
            "full_name",
            "email",
            "status",
            "start_date",
            "expected_completion_date",
            "mentor",
            "is_delayed",
            "chapter_progresses",
        ]

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username


# ──────────────────────────────────────────
# 受講生登録
# ──────────────────────────────────────────

class TraineeRegisterSerializer(serializers.Serializer):
    # User フィールド
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=150, required=False, default="")
    last_name = serializers.CharField(max_length=150, required=False, default="")

    # TraineeProfile フィールド
    start_date = serializers.DateField(required=False, allow_null=True)
    expected_completion_date = serializers.DateField(required=False, allow_null=True)
    mentor = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_staff=True),
        required=False,
        allow_null=True,
    )

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("このユーザー名はすでに使用されています。")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("このメールアドレスはすでに登録されています。")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        profile = TraineeProfile.objects.create(
            user=user,
            start_date=validated_data.get("start_date"),
            expected_completion_date=validated_data.get("expected_completion_date"),
            mentor=validated_data.get("mentor"),
            status=TraineeProfile.STATUS_NOT_STARTED,
        )
        return profile