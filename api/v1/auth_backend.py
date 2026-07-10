from ninja.security import HttpBearer

from accounts.jwt_service import decode_access_token
from accounts.models import User


class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        payload = decode_access_token(token)
        if payload is None:
            return None
        try:
            return User.objects.get(id=payload['user_id'], is_active=True)
        except User.DoesNotExist:
            return None
 