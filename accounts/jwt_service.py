import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from django.conf import settings
from django.contrib.auth import authenticate

from accounts.models import RefreshToken, User


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_access_token(user: User) -> str:
    expires = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_LIFETIME_MINUTES
    )
    payload = {
        'user_id': user.id,
        'username': user.username,
        'role': user.role,
        'exp': expires,
        'type': 'access',
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm='HS256')


def create_refresh_token(user: User) -> str:
    raw_token = secrets.token_urlsafe(48)
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_LIFETIME_DAYS)
    RefreshToken.objects.create(
        user=user,
        token_hash=_hash_token(raw_token),
        expires_at=expires_at,
    )
    return raw_token


def rotate_refresh_token(old_raw_token: str) -> tuple[str, str] | None:
    token_hash = _hash_token(old_raw_token)
    try:
        stored = RefreshToken.objects.select_related('user').get(
            token_hash=token_hash,
            revoked=False,
        )
    except RefreshToken.DoesNotExist:
        return None

    if stored.expires_at < datetime.now(timezone.utc):
        stored.revoked = True
        stored.save(update_fields=['revoked'])
        return None

    user = stored.user
    stored.revoked = True
    stored.save(update_fields=['revoked'])

    access = create_access_token(user)
    refresh = create_refresh_token(user)
    return access, refresh


def decode_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=['HS256'])
    except jwt.PyJWTError:
        return None
    if payload.get('type') != 'access':
        return None
    return payload


def login_user(username: str, password: str) -> tuple[User, str, str] | None:
    user = authenticate(username=username, password=password)
    if user is None or not user.is_active:
        return None
    access = create_access_token(user)
    refresh = create_refresh_token(user)
    return user, access, refresh


def revoke_refresh_token(raw_token: str) -> bool:
    token_hash = _hash_token(raw_token)
    updated = RefreshToken.objects.filter(token_hash=token_hash, revoked=False).update(revoked=True)
    return updated > 0
