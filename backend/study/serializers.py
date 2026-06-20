from rest_framework import serializers
from .models import Category, StudyRecord, Stamp

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'get_name_display']

    get_name_display = serializers.SerializerMethodField()

    def get_get_name_display(self, obj):
        return obj.get_name_display()
    

class StudyRecordSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    stamp_count = serializers.SerializerMethodField()
    duration_display = serializers.SerializerMethodField()
    my_stamp = serializers.SerializerMethodField() 



    class Meta:
        model = StudyRecord
        fields = [
            'id', 'user', 'username', 'category', 'category_name','title', 'description', 'study_date', 'duration_minutes',
            'duration_display', 'stamp_count','my_stamp','created_at','understanding','questions', 'struggles', 'achievements', 'solutions',
        ]
        read_only_fields = ['user', 'created_at']

    def get_category_name(self, obj):
        return obj.category.get_name_display() if obj.category else None
    
    def get_username(self, obj):
        return obj.user.username
    
    def get_stamp_count(self, obj):
        return obj.stamps.count()
    
    def get_duration_display(self, obj):
        hours = obj.duration_minutes // 60
        minutes = obj.duration_minutes % 60
        if hours > 0:
            return f'{hours}時間{minutes}分' if minutes > 0 else f'{hours}時間'
        return f'{minutes}分'
    
    def get_my_stamp(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.stamps.filter(from_user=request.user).exists()
        return False
        
class StampSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stamp
        fields = ['id', 'from_user', 'study_record', 'stamp_type','created_at']
        read_only_fields = ['from_user', 'created_at']
        
