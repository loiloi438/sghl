from django.contrib import admin

from messagerie.models import MessageInterne


@admin.register(MessageInterne)
class MessageInterneAdmin(admin.ModelAdmin):
    list_display = ('sujet', 'expediteur', 'destinataire', 'lu', 'created_at')
    list_filter = ('lu',)
    search_fields = ('sujet', 'corps')
