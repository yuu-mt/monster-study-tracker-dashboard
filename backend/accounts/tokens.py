import secrets
from django.utils import timezone
from datetime import timedelta


def generate_reset_token():
    return secrets.token_urlsafe(32)


def is_token_valid(token_created_at):
    """トークンの有効期限は1時間"""
    return timezone.now() < token_created_at + timedelta(hours=1)