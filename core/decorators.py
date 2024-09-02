from ssl import SSL_ERROR_SSL
from django.shortcuts import redirect
from auction.models import AuctionAuthorization
from core.models import CrowdFundingOrderItem, OpenFundingOrderItem, SecretFundingOrderItem
from user.models import Users
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

def authorization_required(func):
    def wrapper(request, *args, **kwargs):
        user = Users.objects.get(pk=request.user.id)
        placement_pk=kwargs['pk']
        #Session 확인
        if request.session.get('NFT-verify', None) == request.user.id:
          return func(request, *args, **kwargs)
          
        elif request.session.get('E-verify', None) == request.user.id:
          return func(request, *args, **kwargs)

        #Model 확인
        else:

          try:
            au = AuctionAuthorization.objects.filter(placement__id=placement_pk)
            if au.exists(): #해당 옥션에 초대장이 존재하는지
              try:
                    user_au=au.filter(user=request.user) #해당 옥션에 등록된 초대장이 있는지
                    if user_au[0].is_authorized:
                        # messages.info(request, f'[초대손님]{request.user}님 입장하셨습니다. 옥션에 참가하신걸 환영합니다.')
                        return func(request, *args, **kwargs)
                    else:
                        messages.info(request, "초대장이 등록되어있으나 인가되지 않은 초대장입니다. 관리자에게 문의 바랍니다.")
                        return redirect('auction:home')
              except :
                      messages.info(request, "옥션은 초대장을 받은 분들에 한해서 진행중입니다. 귀하의 초대코드를 입력해주세요.")
                      return redirect('auction:invi-auth', placement_pk)
            else: #해당옥션에 모두에게 초대장없음
              messages.info(request, "초대장이 발급되지 않은 옥션입니다")
              return redirect('auction:invi-auth', placement_pk)

          except: 
            messages.info(request, "에러가 발생했습니다")
            return redirect('auction:home')

    return wrapper

class Admin_Authorization_Required_Mixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
          return super().dispatch(request, *args, **kwargs)
        else:
          messages.info(request, "관리자만 접근 가능합니다")
          return redirect('auction:plv')

class Fake_Admin_Authorization_Required_Mixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
          return super().dispatch(request, *args, **kwargs)
        else:
          messages.info(request, "관리자만 접근 가능합니다")
          return redirect('/admin/')