import json

from django.core.serializers.json import DjangoJSONEncoder

from audit.models import AuditLog


def get_client_ip(request) -> str | None:
    if request is None:
        return None
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def log_audit(
    *,
    user,
    action: str,
    model_name: str,
    object_id: str,
    old_value=None,
    new_value=None,
    ip_address=None,
):
    def _json_safe(value):
        if value is None:
            return None
        return json.loads(json.dumps(value, cls=DjangoJSONEncoder))

    AuditLog.objects.create(
        user=user,
        action=action,
        model_name=model_name,
        object_id=str(object_id),
        old_value=_json_safe(old_value),
        new_value=_json_safe(new_value),
        ip_address=ip_address,
    )
