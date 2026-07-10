"""
URL configuration for sghl project.
"""

from django.conf import settings
from django.contrib import admin
from django.urls import path, re_path
from django.conf.urls.static import static
from django.views.generic import RedirectView, TemplateView
from api.v1.router import api
from .views import health_check

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^api/v1/$', RedirectView.as_view(url='/api/v1/docs/')),  # redirect API root to docs
    path('api/v1/', api.urls),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('healthz/', health_check, name='healthz'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
