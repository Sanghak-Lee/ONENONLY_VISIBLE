import os
from decouple import config
import jwt
from rest_framework import authentication
from user.models import Users

class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        try:
            token = request.META.get("HTTP_AUTHORIZATION")
            if token is None:
                return None
            xjwt, jwt_token = token.split(" ")
            decoded = jwt.decode(jwt_token, config('SECRET_KEY'), algorithms=["HS256"])
            pk = decoded.get("pk")
            user = Users.objects.get(pk=pk)
            return (user, None)
        except (ValueError, jwt.exceptions.DecodeError, Users.DoesNotExist):
            return None
