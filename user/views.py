from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
import jwt
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser, AllowAny
from artist.serializers import ArtistSerializer, ReviewSerializer, Reviews
from artist.models import Artists, ArtistProfiles, Reviews
from .models import Users, Verification
from .serializers import UserSerializer
from .permissions import IsSelf

'''
SMS
'''
import time
from core.tasks import Phone_SMS_Send
from django.contrib import messages
from django.views.generic import ListView, DetailView, View
from decouple import config
import base64, hmac, hashlib, json, requests
from random import randint

#SMS 보내기
class PhoneMesssage(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            phone = data['phone_num']
            code = str(randint(100000, 999999))						
            Verification.objects.update_or_create(
                user=request.user,
                defaults={
                    'phone': phone,
                    'code' : code
                }
            )
        	# phone, code 를 인자로 send_verification 메서드를 호출
            content = f'안녕하세요. 1NONLY Auction 입니다. 인증번호 [{code}]를 입력해주세요.'
            res = Phone_SMS_Send.apply_async( args=[phone, content], ignore_result=False)
            return HttpResponse("success")

        except KeyError as e:
            messages.error(request, "keyerror", e)
            return HttpResponse("1")

        except ValueError as e:
            messages.error(request, "ValueError", e)
            return HttpResponse("2")

        except IntegrityError as e:
            messages.error(request, "핸드폰 번호가 중복됩니다", e)
            return HttpResponse("3")

# 문자인증 확인과정
class PhoneCef(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            phone = data['phone_num']
            verification_number = data['phone_cef']
            vf = Verification.objects.get(phone=phone, user=request.user)
            if verification_number == vf.code:
                vf.phone_verified = True
                vf.save()
                messages.info(request, "인증이 완료되었습니다.")
                return HttpResponse("success")

            messages.info(request, "인증번호가 잘못되었습니다")
            return HttpResponse("1")


        except KeyError as e:
            messages.info(request, "keyerror", e)
            return HttpResponse("2")

        except ValueError as e:
            messages.info(request, "ValueError", e)
            return HttpResponse("3")



"""
API server
"""

class UsersViewSet(ModelViewSet):

    queryset = Users.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):

        if self.action == "list":
            permission_classes = [IsAdminUser]

        elif (
            self.action == "create"
#            or self.action == "retrieve"
            or self.action == "artist_like"
            or self.action == "review_like"
        ):
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsSelf]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=["post"])
    def login(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(username=username, password=password)
        if user is not None:
            encoded_jwt = jwt.encode(
                {"pk": user.pk}, settings.SECRET_KEY, algorithm="HS256"
            )
            return Response(data={"token": encoded_jwt, "id": user.pk})
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=True)
    def artist_like(self, request, pk):
        user = self.get_object()
        serializer = ArtistSerializer(user.artist_like.all(), many=True).data
        return Response(serializer)

    @artist_like.mapping.put
    def toggle_artist_like(self, request, pk):
        pk = request.data.get("pk", None)
        user = self.get_object()
        if pk is not None:
            try:
                artist = Artists.objects.get(pk=pk)
                if artist in user.artist_like.all():
                    user.artist_like.remove(artist)
                else:
                    user.artist_like.add(artist)
                return Response(status=status.HTTP_200_OK)
            except Artists.DoesNotExist:
                pass
        return Response(status=status.HTTP_400_BAD_REQUEST)


    @action(detail=True)
    def review_like(self, request, pk):
        user = self.get_object()
        serializer = ReviewSerializer(user.review_like.all(), many=True).data
        return Response(serializer)

    @review_like.mapping.put
    def toggle_review_like(self, request, pk):
        pk = request.data.get("pk", None)
        user = self.get_object()
        if pk is not None:
            try:
                review = Reviews.objects.get(pk=pk)
                if review in user.review_like.all():
                    user.review_like.remove(review)
                else:
                    user.review_like.add(review)
                return Response(status=status.HTTP_200_OK)
            except Reviews.DoesNotExist:
                pass
        return Response(status=status.HTTP_400_BAD_REQUEST)
