from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, UserDetailView, LogoutView, FriendListView, FriendRequestView, UserSearchView
from .views import (
    RegisterView, UserDetailView, LogoutView,
    FriendListView, FriendRequestView, UserSearchView,
    PasswordResetRequestView, PasswordResetConfirmView
)

urlpatterns = [
    #新規登録
    path('register/', RegisterView.as_view(), name='register'),
    #ログイン
    path('login/', TokenObtainPairView.as_view(), name='login'),
    #トークンリフレッシュ
    path('token/refresh/', TokenRefreshView.as_view(), 
    name='token_refresh'),
    #ログアウト
    path('logout/', LogoutView.as_view(), name='logout'),
    #ユーザー情報・取得
    path('me/', UserDetailView.as_view(), name='user_detail'),
    # 友達一覧
    path('friends/', FriendListView.as_view(), name='friend_list'),
    # 友達追加・削除
    path('friends/<int:user_id>/', FriendRequestView.as_view(), name='friend_request'),
    # ユーザー検索
    path('search/', UserSearchView.as_view(), name='user_search'),
    # パスワードリセット
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]