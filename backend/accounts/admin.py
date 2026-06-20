from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from.models import User, Friendship


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ['email']
    list_display = ['email', 'username', 'is_staff','created_at' ]
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password',)}),
        ('権限', {'fields':('is_active', 'is_staff','is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes':('wide',),
            'fields': ('email', 'username', 'password1','password2' )
        })
    )

@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ['from_user', 'to_user']