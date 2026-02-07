from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('dj-admin/', admin.site.urls),
    path('', include('portal.urls')),
]
