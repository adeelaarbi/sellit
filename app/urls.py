from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings
from . import views
app_name = "app"
urlpatterns = [    
    path('myads/', views.MyAds.as_view(), name='my-ads'),
    path('make/url', views.make_url, name='make-url'),
    path('ads/<str:query>', views.search_list, name='search-list'),
    path('post/add', views.PostAddView.as_view(), name='add-post'),
    path('post/<int:pk>/update', views.PostUpdateView.as_view(), name='update-post'),
    path('post/<slug:slug>', views.PostDetailView.as_view(), name='post-detail'),
    path('load-locations/', views.load_locations_categories, name='load-locations'),
    path('', views.PostListView.as_view(), name='posts'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)