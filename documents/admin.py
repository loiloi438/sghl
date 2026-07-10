from django.contrib import admin

from documents.models import DocumentSigne


@admin.register(DocumentSigne)
class DocumentSigneAdmin(admin.ModelAdmin):
    list_display = (
        'type_document',
        'numero_reference',
        'signataire_nom',
        'code_verification',
        'signe_le',
    )
    list_filter = ('type_document', 'signataire_role')
    search_fields = ('numero_reference', 'code_verification', 'signataire_nom')
    readonly_fields = (
        'empreinte_sha256',
        'signature',
        'code_verification',
        'signe_le',
        'created_at',
        'updated_at',
    )
