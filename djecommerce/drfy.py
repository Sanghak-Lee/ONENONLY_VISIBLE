#restframework + swagger
import os
from django.conf.urls import url
from django.urls import path, include
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission
from drf_yasg import openapi



# schema_url_patterns=[
#     path('api/v1/user', include('user.urls')),
#     path('api/v1/artist', include('artist.urls'))
# ]
# schema_url_patterns = [
#      path('')
#  ]
schema_view = get_schema_view(
    openapi.Info(
        title="ONE&ONLY REST API DOCS",
        default_version="v1_210930",
        description="원앤온리 홈페이지 RESTAPI 도큐먼트",
        terms_of_service="https://www.django-rest-framework.org/topics/documenting-your-api/",
        contact=openapi.Contact(name="개발매니저 이상학", email="eaa0305@naver.com"),
        license=openapi.License(name="Beyondimension.inc"),
    ),
    validators=['flex'],
    public=True,
    permission_classes=(AllowAny,),
    # patterns=schema_url_patterns,
)