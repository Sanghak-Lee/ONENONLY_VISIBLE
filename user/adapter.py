from logging import raiseExceptions
from xml.dom import ValidationErr
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.http import HttpResponse
from core.tasks import Biz_KAKAO_Send
from core.utils import Phone_Number_Standardize
from user.models import UserPrivacy, Users, Verification
from django.contrib import messages
from datetime import datetime
import json
class MyAccountAdapter(DefaultAccountAdapter):
    def confirm_email(self, request, email_address):
        """
        Marks the email address as confirmed on the db
        """
        email=email_address.email
        if super().is_email_verified(request, email) == False:
            #이메일전송
            subject = 'account/email/email_welcome'
            email = email
            ctx = {
                "user":email_address.user,
            }
            super().send_mail(subject, email, ctx)

            #카카오메시지 전송
            try:
                _phones_params=[]
                phone=email_address.user.verification.standardize_phone()
                _tmpltCode = 'v2_signup'
                _params={
                    'USERNAME':email_address.user.username
                }
                _phones_params.append({phone:_params})
                # Biz_KAKAO_Send.run(phones_params=_phones_params, tmpltCode=_tmpltCode)
                Biz_KAKAO_Send.apply_async(kwargs={'phones_params':_phones_params, 'tmpltCode':_tmpltCode}, ignore_result=False)
            except:
                pass

        email_address.verified = True
        email_address.set_as_primary(conditional=True)
        email_address.save()
    def ajax_response(self, request, response, redirect_to=None, form=None,
                      data=None):
        resp = {}
        status = response.status_code

        if redirect_to:
            status = 200
            resp['location'] = redirect_to
        if form:
            if request.method == 'POST':
                if form.is_valid():
                    status = 200
                else:
                    status = 400
                    resp['form_errors'] = form._errors
            else:
                status = 200
            resp['form'] = self.ajax_response_form(form)
            if hasattr(response, 'render'):
                response.render()
            resp['html'] = response.content.decode('utf8')
        if data is not None:
            resp['data'] = data
        return HttpResponse(json.dumps(resp),
                            status=status,
                            content_type='application/json')    

    def save_user(self, request, user, form, commit=True, social=False):
        #회원가입 절차에서 verification 이루어졌는지 확인
        #소셜 회원가입이 아닐때만
        if not social:
            user = super().save_user(request, user, form, commit)
            #필수동의 사항 확인
            data = form.cleaned_data
            agreement_1 = data.get('agreement_1', True)
            agreement_2 = data.get('agreement_2', True)
            agreement_3 = data.get('agreement_3', True)
            agreement_4 = data.get('agreement_4', True)
            up = UserPrivacy.objects.get_or_none(user=user.id)
            if up is None:
                try:
                    up=UserPrivacy.objects.create(
                        user=user,
                        agreement_1=agreement_1,
                        agreement_2=agreement_2,
                        agreement_3=agreement_3,
                        agreement_4=agreement_4,
                    )

                except ValidationErr:
                    return None

            unique_key = request.session.get('onenonly_user_unique_key', None)
            vf = Verification.objects.get_or_none(unique_key=unique_key)
            if vf == None:
                messages.info(request, '호환되지 않는 브라우저 입니다. 인증을 한번 더 진행할 수 있습니다.')
            else:
                vf.user=user
                vf.save()

                #인증세션
                if vf.phone:
                    vf.last_verified = datetime.now()
                    vf.save()
                    request.session['phone_verified_user'] = user.id
                    
            return user

        #Social Auto Signup
        else:
            user = super().save_user(request, user, form, commit)
            return user

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):

        #super().save_user
        from allauth.account.adapter import get_adapter as get_account_adapter
        user = sociallogin.user
        user.set_unusable_password()
        if form:
            # user.set_password(form.cleaned_data["password1"])
            # user.username=form.cleaned_data["username"]
            # user.email=form.cleaned_data["email"]
            # user.save()
            get_account_adapter().save_user(request, user, form, commit=True, social=True)
        else:
            get_account_adapter().populate_username(request, user)
        sociallogin.save(request)

        up, created = UserPrivacy.objects.update_or_create(
            user=user,
            defaults={
                'agreement_1':True,
                'agreement_2':True,
                'agreement_3':True,
                'agreement_4':True,
            }
        )
        #인증세션
        phone=''
        if sociallogin.account.provider == 'kakao':
            if sociallogin.account.extra_data.get('kakao_account').get('has_phone_number'):
                request.session['phone_verified_user'] = user.id
                phone=Phone_Number_Standardize(sociallogin.account.extra_data.get('kakao_account').get('phone_number'))

        elif sociallogin.account.provider == 'naver':
            if sociallogin.account.extra_data.get('mobile'):
                request.session['phone_verified_user'] = user.id
                phone=Phone_Number_Standardize(sociallogin.account.extra_data.get('mobile'))

        #카카오메시지 전송
        try:
            _phones_params=[]
            _phone = phone
            _tmpltCode = 'v2_signup'
            _params={
                'USERNAME':user.username
            }
            _phones_params.append({phone:_params})
            # Biz_KAKAO_Send.run(phones_params=_phones_params, tmpltCode=_tmpltCode)
            Biz_KAKAO_Send.apply_async(kwargs={'phones_params':_phones_params, 'tmpltCode':_tmpltCode}, ignore_result=False)
        except:
            pass

        return user

