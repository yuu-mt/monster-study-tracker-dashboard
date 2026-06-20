from django.contrib import admin
from .models import Category, StudyRecord, Stamp


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(StudyRecord)
class StudyRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'category', 'study_date', 'duration_minutes']
    list_filter = ['category', 'study_date']
    search_fields = ['title', 'description']


@admin.register(Stamp)
class StampAdmin(admin.ModelAdmin):
    list_display = ['from_user', 'study_record', 'stamp_type']