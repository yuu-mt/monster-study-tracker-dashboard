from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import UserRegisterSerializer, UserSerializer
from .models import Friendship
from django.contrib.auth import get_user_model
import resend
import os
from .tokens import generate_reset_token, is_token_valid
from .models import PasswordResetToken

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """新規登録API"""
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_class = [permissions.AllowAny] # 未ログインでもアクセス可

class UserDetailView(generics.RetrieveUpdateAPIView):
    """ログイン中のユーザー情報取得・更新API"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated] # ログイン必須

    def get_object(self):
        return self.request.user # ログイン中のユーザーを返す
    
class LogoutView(APIView):
    """ログアウトAPI"""
    permission_classes = [permissions.IsAuthenticated] 

    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist() # トークンを無効化
            return Response({'message': 'ログアウトしました'}, status=status.HTTP_200_OK)
        except Exception:
            return Response({'error': '無効なトークンです'}, status=status.HTTP_400_BAD_REQUEST)
        
class FriendListView(generics.ListAPIView):
    """友達一覧取得API"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(
            followers__from_user=self.request.user
        )


class FriendRequestView(APIView):
    """友達追加・削除API"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        try:
            to_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'ユーザーが見つかりません'}, status=status.HTTP_404_NOT_FOUND)

        if to_user == request.user:
            return Response({'error': '自分自身は追加できません'}, status=status.HTTP_400_BAD_REQUEST)

        friendship, created = Friendship.objects.get_or_create(
            from_user=request.user,
            to_user=to_user
        )

        if created:
            return Response({'message': f'{to_user.username}を友達追加しました'}, status=status.HTTP_201_CREATED)
        else:
            friendship.delete()
            return Response({'message': f'{to_user.username}を友達削除しました'}, status=status.HTTP_200_OK)


class UserSearchView(generics.ListAPIView):
    """ユーザー検索API"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        if query:
            return User.objects.filter(
                username__icontains=query
            ).exclude(id=self.request.user.id)
        return User.objects.none()
    
class PasswordResetRequestView(APIView):
    """パスワードリセットメール送信API"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'メールアドレスを入力してください'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # セキュリティのため存在しない場合も同じレスポンスを返す
            return Response({'message': 'パスワードリセットメールを送信しました'})

        # トークン生成
        token = generate_reset_token()
        PasswordResetToken.objects.create(user=user, token=token)

        # リセットURL
        frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
        reset_url = f'{frontend_url}/reset-password?token={token}'

        # メール送信
        resend.api_key = os.environ.get('RESEND_API_KEY')
        resend.Emails.send({
            'from': 'onboarding@resend.dev',
            'to': email,
            'subject': '【StudyTracker】パスワードリセット',
            'html': f'''
                <h2>パスワードリセット</h2>
                <p>{user.username} さん</p>
                <p>以下のリンクからパスワードをリセットしてください。</p>
                <p>リンクの有効期限は1時間です。</p>
                <a href="{reset_url}" style="background:#2563eb;color:white;padding:12px 24px;border-radius:8px;text-decoration:none;">
                    パスワードをリセット
                </a>
                <p>このメールに心当たりがない場合は無視してください。</p>
            '''
        })

        return Response({'message': 'パスワードリセットメールを送信しました'})


class PasswordResetConfirmView(APIView):
    """パスワードリセット確認API"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = request.data.get('token')
        password = request.data.get('password')

        if not token or not password:
            return Response({'error': '必要な情報が不足しています'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            reset_token = PasswordResetToken.objects.get(token=token, is_used=False)
        except PasswordResetToken.DoesNotExist:
            return Response({'error': '無効なトークンです'}, status=status.HTTP_400_BAD_REQUEST)

        if not is_token_valid(reset_token.created_at):
            return Response({'error': 'トークンの有効期限が切れています'}, status=status.HTTP_400_BAD_REQUEST)

        # パスワード更新
        user = reset_token.user
        user.set_password(password)
        user.save()

        # トークンを使用済みにする
        reset_token.is_used = True
        reset_token.save()

        return Response({'message': 'パスワードをリセットしました'})
