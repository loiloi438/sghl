from django.contrib import admin

from notifications.models import DeviceToken, NotificationInbox


@admin.register(DeviceToken)
class DeviceTokenAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'plateforme', 'actif', 'updated_at')
    list_filter = ('plateforme', 'actif')
    search_fields = ('token', 'utilisateur__username')


@admin.register(NotificationInbox)
class NotificationInboxAdmin(admin.ModelAdmin):
    list_display = ('titre', 'utilisateur', 'categorie', 'lu', 'created_at')
    list_filter = ('lu', 'categorie')
    readonly_fields = ('created_at',)
