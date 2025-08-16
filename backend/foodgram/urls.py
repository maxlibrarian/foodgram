from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from recipes.views import shortlink_redirect

urlpatterns = [
    path("s/<str:code>", shortlink_redirect, name="shortlink-no-slash"),
    path("s/<str:code>/", shortlink_redirect, name="shortlink"),
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('api/', include('recipes.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
