from accounts.jwt_service import create_access_token
from accounts.models import Role, User


def payment_auth_headers() -> dict:
    user, created = User.objects.get_or_create(
        username='payments_test_user',
        defaults={
            'role': Role.COMPTABLE,
            'mfa_enabled': True,
            'email': 'payments_test_user@test.local',
        },
    )
    if created:
        user.set_password('Comptable@SGHL2026')
        user.save()
    return {'Authorization': f'Bearer {create_access_token(user)}'}
