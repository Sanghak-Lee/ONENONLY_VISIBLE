from pyexpat.errors import messages
from django.shortcuts import redirect
from .models import Users
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from user.models import Verification
from datetime import timedelta, datetime
from django.utils.decorators import method_decorator

#핸드폰 인증(4weeks)
def Phone_Verified_Required(func):
    @login_required
    def wrapper(request, *args, **kwargs):
        user = Users.objects.get(pk=request.user.id)
        verification=Verification.objects.get_or_none(user=request.user)
        now=datetime.now()
        try:
            if verification is None:
                messages.info(request, "핸드폰 인증을 완료해주십시오")
                return redirect(reverse('core:verify')+f"?next={request.path}")
            #관리자 PASS
            elif verification.phone and user.is_staff:
                # messages.info(request, "관리자 계정이 인식되어 인증 절차가 생략되었습니다.")
                return func(request, *args, **kwargs)
            elif verification.phone and (now - verification.last_verified) < timedelta(weeks=4):
                return func(request, *args, **kwargs)
            else:
                messages.info(request, "핸드폰 인증을 완료해주십시오")
                return redirect(reverse('core:verify')+f"?next={request.path}")
        except:
            if (now - verification.last_verified) < timedelta(weeks=8):
                messages.warning(request, "인증이력은 있으나, 에러가 발생하였습니다. 다른 인증방식으로 진행해주십시오.")
            else:
                messages.warning(request, "최종 인증이력이 만료되었습니다. 인증을 다시 완료해주십시오.")
            return redirect(reverse('core:verify')+f"?next={request.path}")
    return wrapper

#핸드폰 인증(4weeks)
@method_decorator(login_required, name='dispatch')
class Phone_Verified_Required_Mixin:
    def dispatch(self, request, *args, **kwargs):
        user = Users.objects.get(pk=request.user.id)
        verification=Verification.objects.get_or_none(user=request.user)
        now=datetime.now()
        try:
            if verification is None:
                messages.info(request, "핸드폰 인증을 완료해주십시오")
                return redirect(reverse('core:verify')+f"?next={request.path}")            
            #관리자 PASS            
            elif verification.phone and user.is_staff:
                messages.info(request, "관리자 계정이 인식되어 인증 절차가 생략되었습니다.")            
                return super().dispatch(request, *args, **kwargs)
            elif verification.phone and (now - verification.last_verified) < timedelta(weeks=4):
                return super().dispatch(request, *args, **kwargs)
            else:
                messages.info(request, "핸드폰 인증을 완료해주십시오")
                return redirect(reverse('core:verify')+f"?next={request.path}")
        except:
            if (now - verification.last_verified) < timedelta(weeks=8):
                messages.warning(request, "인증이력은 있으나, 에러가 발생하였습니다. 다른 인증방식으로 진행해주십시오.")
            else:
                messages.warning(request, "최종 인증이력이 만료되었습니다. 인증을 다시 완료해주십시오.")
            return redirect(reverse('core:verify')+f"?next={request.path}")

#핸드폰 번호 존재하는지
def Phone_Exist_Required(func):
    @login_required
    def wrapper(request, *args, **kwargs):
        try:
            vf = request.user.verification
            if vf.phone:
                return func(request, *args, **kwargs)
            else:
                messages.info(request, "핸드폰 번호 입력이 필요합니다")
                return redirect(reverse('core:verify')+f"?next={request.path}")
        except:
            messages.info(request, "핸드폰 번호 입력이 필요합니다")
            return redirect(reverse('core:verify')+f"?next={request.path}")
    return wrapper
@method_decorator(login_required, name='dispatch')
class Phone_Exist_Required_Mixin:
    def dispatch(self, request, *args, **kwargs):
        try:
            vf = request.user.verification
            if vf.phone:
                return super().dispatch(request, *args, **kwargs)                
            else:
                messages.info(request, "핸드폰 번호 입력이 필요합니다")
                return redirect(reverse('core:verify')+f"?next={request.path}")
        except:
            messages.info(request, "핸드폰 번호 입력이 필요합니다")
            return redirect(reverse('core:verify')+f"?next={request.path}")

class Password_Check_Required_Mixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            pw = request.POST.get('password', None)
            if pw and request.user.check_password(pw):
                return super().dispatch(request, *args, **kwargs)
            messages.info(request, "비밀번호가 올바르지 않습니다.")
        return redirect(reverse('core:user')+'?tab=3&msg=비밀번호 정보를 다시 확인해 주세요.')