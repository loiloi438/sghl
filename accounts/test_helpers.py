from accounts.jwt_service import create_access_token
from accounts.models import User


def auth_headers(user: User) -> dict:
    return {'Authorization': f'Bearer {create_access_token(user)}'}
