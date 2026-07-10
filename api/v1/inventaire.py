from decimal import Decimal
from typing import Optional
from uuid import UUID

from django.db.models import Q
from ninja import Router, Schema
from ninja.errors import HttpError

from accounts.models import Role, User
from api.v1.auth_backend import JWTAuth
from audit.services import get_client_ip, log_audit
from inventaire.models import ArticleStock
from inventaire.services import InventaireError, ajuster_stock

router = Router(tags=['Inventaire'])
jwt_auth = JWTAuth()

ROLES = {Role.ADMIN, Role.PHARMACIEN}


def _check(user: User):
    if user.role not in ROLES:
        raise HttpError(403, 'Accès refusé.')


def _handle_error(exc: InventaireError):
    status_map = {'version_conflict': 409, 'stock_insuffisant': 400}
    raise HttpError(status_map.get(exc.code, 400), exc.message)


class ArticleOut(Schema):
    id: UUID
    code: str
    name: str
    category: str
    quantity: int
    minLevel: int
    unit: str
    stockLevel: str
    value: str
    actif: bool
    version: int


class ArticleIn(Schema):
    code: str
    nom: str
    categorie: str = 'consumable'
    quantite: int = 0
    seuil_alerte: int = 10
    unite: str = 'unité'
    valeur_unitaire: Decimal = Decimal('0')


class AjustementIn(Schema):
    version: int
    delta: int


class StatsInventaireOut(Schema):
    total_items: int
    critical_levels: int
    total_value: str


def _serialize(a: ArticleStock) -> ArticleOut:
    return ArticleOut(
        id=a.id,
        code=a.code,
        name=a.nom,
        category=a.categorie,
        quantity=a.quantite,
        minLevel=a.seuil_alerte,
        unit=a.unite,
        stockLevel=a.stock_level,
        value=str(a.valeur_totale),
        actif=a.actif,
        version=a.version,
    )


@router.get('/inventaire/stats/', response=StatsInventaireOut, auth=jwt_auth)
def stats_inventaire(request):
    _check(request.auth)
    articles = ArticleStock.objects.filter(actif=True)
    critical = sum(1 for a in articles if a.stock_level in {'critical', 'low'})
    total_val = sum((a.valeur_totale for a in articles), Decimal('0'))
    return StatsInventaireOut(
        total_items=articles.count(),
        critical_levels=critical,
        total_value=str(total_val),
    )


@router.get('/inventaire/articles/', response=list[ArticleOut], auth=jwt_auth)
def list_articles(request, search: str | None = None, categorie: str | None = None):
    _check(request.auth)
    qs = ArticleStock.objects.filter(actif=True)
    if search:
        qs = qs.filter(Q(nom__icontains=search) | Q(code__icontains=search))
    if categorie:
        qs = qs.filter(categorie=categorie)
    return [_serialize(a) for a in qs]


@router.post('/inventaire/articles/', response=ArticleOut, auth=jwt_auth)
def create_article(request, payload: ArticleIn):
    _check(request.auth)
    article = ArticleStock.objects.create(
        code=payload.code,
        nom=payload.nom,
        categorie=payload.categorie,
        quantite=payload.quantite,
        seuil_alerte=payload.seuil_alerte,
        unite=payload.unite,
        valeur_unitaire=payload.valeur_unitaire,
    )
    log_audit(
        user=request.auth,
        action='create',
        model_name='ArticleStock',
        object_id=article.id,
        new_value=payload.dict(),
        ip_address=get_client_ip(request),
    )
    return _serialize(article)


@router.post('/inventaire/articles/{article_id}/ajuster/', response=ArticleOut, auth=jwt_auth)
def ajuster_article(request, article_id: UUID, payload: AjustementIn):
    _check(request.auth)
    try:
        article = ArticleStock.objects.get(id=article_id)
    except ArticleStock.DoesNotExist:
        raise HttpError(404, 'Article introuvable.')
    try:
        article = ajuster_stock(article=article, delta=payload.delta, version=payload.version)
    except InventaireError as exc:
        _handle_error(exc)
    return _serialize(article)


class ArticleUpdateIn(Schema):
    version: int
    nom: Optional[str] = None
    categorie: Optional[str] = None
    seuil_alerte: Optional[int] = None
    unite: Optional[str] = None
    valeur_unitaire: Optional[Decimal] = None
    actif: Optional[bool] = None


@router.patch('/inventaire/articles/{article_id}/', response=ArticleOut, auth=jwt_auth)
def update_article(request, article_id: UUID, payload: ArticleUpdateIn):
    _check(request.auth)
    try:
        article = ArticleStock.objects.get(id=article_id)
    except ArticleStock.DoesNotExist:
        raise HttpError(404, 'Article introuvable.')
    if article.version != payload.version:
        raise HttpError(409, 'Conflit de version.')
    for key, value in payload.dict(exclude={'version'}, exclude_none=True).items():
        setattr(article, key, value)
    article.bump_version()
    article.save()
    return _serialize(article)
