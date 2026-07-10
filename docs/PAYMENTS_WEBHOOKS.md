Payments webhooks — signature verification
=========================================

Résumé
------
Les webhooks entrants sont vérifiés via HMAC-SHA256 en utilisant une clé secrète
spécifique au fournisseur. Si aucune clé n'est configurée, la vérification est
ignorée (pratique pour le développement local).

Variables d'environnement (exemples)
-----------------------------------
- `PAYMENTS_STRIPE_WEBHOOK_SECRET` — clé HMAC pour Stripe (hex string)
- `PAYMENTS_MTN_WEBHOOK_SECRET` — clé HMAC pour MTN / Mobile Money

Header attendu
---------------
L'API attend un header `X-Payments-Signature` contenant le HMAC-SHA256 hex
digest calculé sur le corps brut de la requête (bytes). Exemple en pseudo‑Python:

```
import hmac, hashlib, json
secret = 'ma_cle'
payload = {'provider': 'mtn', 'external_id': 'mtn_ref_123', 'status': 'success'}
raw = json.dumps(payload).encode('utf-8')
signature = hmac.new(secret.encode('utf-8'), raw, hashlib.sha256).hexdigest()
```

Comportement
------------
- Si la variable d'environnement `PAYMENTS_<PROVIDER>_WEBHOOK_SECRET` est définie,
  la signature est requise et validée. Une signature invalide renvoie `400`.
- Si elle n'est pas définie, le webhook est accepté (comportement rétrocompatible
  pour tests locaux).

Idempotency & client_secret
---------------------------
- Le serveur génère une `Idempotency-Key` basée sur `provider:reference` et la
  transmet aux appels vers les PSP/agrégateurs via l'en-tête `Idempotency-Key`.
- Pour les paiements par carte (`provider=stripe`), l'API renvoie directement
  `client_secret` (si disponible) dans le JSON de réponse pour que le
  frontend puisse finaliser le paiement via Stripe.js.

Tester localement
-----------------
Avec `curl` (remplace `SECRET` et `BODY`):

```
BODY='{"provider":"mtn","external_id":"mtn_ref_1","status":"success"}'
SIG=$(python -c "import hmac,hashlib;print(hmac.new(b'SECRET', b'$BODY', hashlib.sha256).hexdigest())")
curl -X POST http://localhost:8000/payments/webhook/ -H "Content-Type: application/json" -H "X-Payments-Signature: $SIG" -d "$BODY"
```

Sécurité
--------
- Stocker les secrets de webhooks dans un gestionnaire de secrets en production
  (Vault, AWS Secrets Manager, etc.), et ne pas committer les clés dans le repo.
- Faire tourner la rotation des clés et mettre en place des alertes/logs pour
  rejeter les webhooks mal signés.
