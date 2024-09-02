from django.contrib.sitemaps.views import sitemap
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from djecommerce.sitemaps import PlacementSitemap
from djecommerce.feeds import PlacementFeed
from django.views.generic.base import TemplateView
from core.views import FakeHomeView
from .drfy import *
# from jet.dashboard.dashboard_modules import google_analytics_views
# Temporary
# urlpatterns =[
#     path('', TemplateView.as_view(template_name="article/auction/info/fake_home.html"), name='fake_home'),
#     path('admin/', admin.site.urls),
# ]

sitemaps = {
    'blog':PlacementSitemap, 
}

urlpatterns = [
    #django-library
    path('jet/', include('jet.urls', 'jet')),
    path('jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),

    #core
    path('', include('core.urls')),
 
    # ##--
    #user
    path('user/', include('user.urls')),

    #Auction APP
    path('auction/', include('auction.urls')),
    # ##--


    # rest api
    # path('api/v1/user/', include('user.urls')),
    # path('api/v1/artist/', include('artist.urls')),



    #swagger with drfg_ysg (rest api document)
    path('swagger<str:format>', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('docs/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    


    #sitemap.xml, robots.txt
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps, 'template_name': 'search/google_sitemap.html'}, name='django.contrib.sitemaps.views.sitemap'),
    path('naver/sitemap.xml', sitemap, {'sitemaps': sitemaps, 'template_name': 'search/naver_sitemap.html'}, name='django.contrib.sitemaps.views.sitemap'),
    path("robots.txt",TemplateView.as_view(template_name="search/robots.txt", content_type="text/plain"), name='robots'),
    path('feeds/', PlacementFeed(), name='feeds'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)

handler400 = 'core.views.bad_request_400'
handler403 = 'core.views.permission_denied_403'
handler404 = 'core.views.page_not_found_404'
handler500 = 'core.views.server_error_500'