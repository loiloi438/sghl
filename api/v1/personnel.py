from django.db.models import Q
from ninja import Router, Schema

from accounts.models import Role, User
from api.v1.auth_backend import JWTAuth

router = Router(tags=['Personnel'])
jwt_auth = JWTAuth()


def get_default_profile_photo(user: User) -> str:
    img = (user.id % 68) + 1
    return f'https://i.pravatar.cc/128?img={img}'


class PersonnelOut(Schema):
    id: int
    username: str
    first_name: str
    last_name: str
    full_name: str
    email: str
    role: str
    role_label: str
    mfa_enabled: bool
    photo_url: str


ROLE_FILTERS = {
    'medecin': Role.MEDECIN,
    'infirmier': Role.INFIRMIER,
}


def _serialize_user(user: User) -> PersonnelOut:
    full_name = f'{user.first_name} {user.last_name}'.strip() or user.username
    return PersonnelOut(
        id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        full_name=full_name,
        email=user.email,
        role=user.role,
        role_label=user.get_role_display(),
        mfa_enabled=user.mfa_enabled,
        photo_url=get_default_profile_photo(user),
    )


def _list_personnel(role: str, search: str | None = None):
    qs = User.objects.filter(role=role).order_by('last_name', 'first_name', 'username')
    if search:
        qs = qs.filter(
            Q(username__icontains=search)
            | Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(email__icontains=search)
        )
    return [_serialize_user(user) for user in qs]


@router.get('/personnel/medecins/', response=list[PersonnelOut], auth=jwt_auth)
def list_medecins(request, search: str | None = None):
    return _list_personnel(Role.MEDECIN, search)


@router.get('/personnel/infirmiers/', response=list[PersonnelOut], auth=jwt_auth)
def list_infirmiers(request, search: str | None = None):
    return _list_personnel(Role.INFIRMIER, search)