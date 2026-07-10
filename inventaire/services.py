from django.db import transaction

from inventaire.models import ArticleStock


class InventaireError(Exception):
    def __init__(self, message: str, code: str = 'error'):
        self.message = message
        self.code = code
        super().__init__(message)


@transaction.atomic
def ajuster_stock(*, article: ArticleStock, delta: int, version: int) -> ArticleStock:
    if article.version != version:
        raise InventaireError('Conflit de version.', code='version_conflict')
    new_qty = article.quantite + delta
    if new_qty < 0:
        raise InventaireError('Stock insuffisant.', code='stock_insuffisant')
    article.quantite = new_qty
    article.bump_version()
    article.save()
    return article
