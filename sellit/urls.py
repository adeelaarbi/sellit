"""sellit URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
# from django.conf import settings
from django.contrib.sitemaps import views
import app.urls
import user.urls
from app.sitemaps import (
    PostSitemap,
    CategorySitemap,
    LocationSitemap,
    TagLocationSitemap,
    CategoryLocationSitemap
)

sitemaps = {
    'posts': PostSitemap,
    'categories': CategorySitemap,
    'locations': LocationSitemap,
    'tag-location': TagLocationSitemap,
    'location-category': CategoryLocationSitemap
}

# MEDIA_FILE_PATHS = static(
    # settings.MEDIA_URL,
    # document_root=settings.MEDIA_ROOT
# )


urlpatterns = [
    path('user/', include(user.urls)),
    path('admin/', admin.site.urls),
    path('sitemaps.xml', views.index, {'sitemaps': sitemaps}),
    path('sitemaps-<section>', views.sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('', include(app.urls, namespace='app')),
]
