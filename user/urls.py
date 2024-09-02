from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

app_name = "user"

router = DefaultRouter()
router.register("api/user/", views.UsersViewSet)

# 예시
# router.register("<int:pk>/enrollment/", views.Enrollment)

urlpatterns = [
    path("verify/phone/", views.PhoneMesssage.as_view(), name="PhoneMessage"),
    path("verify/cef/", views.PhoneCef.as_view(), name="PhoneCef"),
]
