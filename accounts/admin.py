from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.hashers import make_password
from django.utils.crypto import get_random_string

from accounts.emails import notifier_validation_code_user
from accounts.models import AccountValidation, RefreshToken, Role, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('SGHL', {'fields': ('role', 'mfa_enabled')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('SGHL', {'fields': ('role',)}),
    )

    def save_model(self, request, obj, form, change):
        is_new = obj.pk is None
        if is_new and obj.role != Role.PATIENT:
            obj.is_active = False
            obj.mfa_enabled = True
        super().save_model(request, obj, form, change)
        if is_new and obj.role != Role.PATIENT:
            code = get_random_string(length=6, allowed_chars='0123456789')
            AccountValidation.objects.create(user=obj, code_hash=make_password(code))
            notifier_validation_code_user(obj.id, code)


@admin.register(RefreshToken)
class RefreshTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'expires_at', 'revoked')
    list_filter = ('revoked',)
