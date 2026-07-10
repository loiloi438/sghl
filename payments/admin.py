from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('reference', 'provider', 'status', 'amount_cents', 'currency', 'created_at')
    list_filter = ('provider', 'status', 'currency')
    search_fields = ('reference', 'external_id')


from .models import PaymentAudit


@admin.register(PaymentAudit)
class PaymentAuditAdmin(admin.ModelAdmin):
    list_display = ('payment', 'previous_status', 'new_status', 'event', 'created_at')
    list_filter = ('previous_status', 'new_status')
    search_fields = ('payment__reference',)
