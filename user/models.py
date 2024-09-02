from django.contrib.auth.models import AbstractUser
from django.db import models
from django.shortcuts import reverse
from django.db.models.signals import post_save
from django.core.validators import RegexValidator
from django.db.models.deletion import CASCADE
from allauth.socialaccount.models import SocialAccount
from django.dispatch.dispatcher import receiver
from django.db.models.signals import post_save, pre_delete, pre_save
from django.contrib import messages
from core.managers import TimeStampedModel
from core.utils import Phone_Number_Standardize
from user.validators import validate_agreement
from phonenumber_field.modelfields import PhoneNumberField
from django.core import files
import requests
import tempfile

def custom_avatar_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    u=instance.username
    # fileName, fileExtension = os.path.splitext(filename)
    return 'Users/{0}/{1}'.format(u, filename)
class Users(AbstractUser):
    #id=models.AutoField(primary_key=True)
    is_artist = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to=custom_avatar_path, help_text = "50x50 사이즈 작은 프로필이미지", blank=True)
    alarm = models.ManyToManyField("auction.Placement", blank=True, related_name="alarms")
    encore = models.ManyToManyField("auction.Placement", blank=True, related_name="encores")
    plike = models.ManyToManyField("auction.Placement", blank=True, related_name="plikes")

    class Meta:
        ordering = ["-pk"]
        verbose_name = '워니'
        verbose_name_plural = '워니들'

    def __str__(self):
        return self.username
     
class UserPrivacy(TimeStampedModel):
    user = models.OneToOneField(Users, on_delete=CASCADE)
    agreement_1=models.BooleanField(default=True, help_text="만 14세 이상", validators=[validate_agreement])
    agreement_2=models.BooleanField(default=True, help_text="이용약관 동의", validators=[validate_agreement])
    agreement_3=models.BooleanField(default=True, help_text="개인정보 처리방침 동의", validators=[validate_agreement])
    agreement_4=models.BooleanField(default=False, help_text="광고성 정보 수신 및 마케팅 활용 동의")
    class Meta:
        ordering = ["-pk"]
        verbose_name = '워니 동의정보'
        verbose_name_plural = '워니 동의정보들'

    def __str__(self):
        return '{0}님 동의정보'.format(self.user)

class Verification(TimeStampedModel):    
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(Users, on_delete=CASCADE, null=True)

    #인증에서 받아온 정보 저장
    unique_key = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length = 50, null=True)
    phone = PhoneNumberField(null=True, blank=True, help_text="핸드폰 번호")
    birthday = models.DateField(null=True)
    code = models.CharField(max_length=6, null=True, blank=True)
    last_verified = models.DateTimeField(auto_now_add=True, help_text="마지막 인증날짜")
    class Meta:
        ordering = ["-pk"]    
        verbose_name = '인증'
        verbose_name_plural = '인증들'

    def __str__(self):
        return '{0}-{1}'.format(self.user, self.name)

    def standardize_phone(self):
        if self.phone:
            return f"0{self.phone.national_number}"

class AdminPhone(TimeStampedModel):
    label = models.CharField(max_length = 50)
    phone = PhoneNumberField(help_text="관리자 핸드폰 번호")
    activate = models.BooleanField(default=True, help_text='관리 알람 활성화')    
    class Meta:
        ordering = ["-pk"]
        verbose_name = '관리자 번호'
        verbose_name_plural = '관리자 번호들'
    def __str__(self):
        return f"{self.label}/{self.phone}"
    def standardize_phone(self):
        if self.phone:
            return f"0{self.phone.national_number}"        
# @receiver(post_save, sender = Users)
# def UserInstanceCreated(sender, instance, **kwargs):
#     up = UserPrivacy.objects.get_or_none(user=instance.id)
#     if up is None:
#         up=UserPrivacy.objects.create(
#             user=sender.id,
#             agreement_1=True,
#             agreement_2=True,
#             agreement_3=True,
#             agreement_4=False,
#         )

@receiver(post_save, sender = SocialAccount)
def SocialAccount_Phone_Connect_User(sender, instance, **kwargs):
    user = Users.objects.get(id=instance.user.id)
    if instance.provider == "kakao":
        extra_data = instance.extra_data['kakao_account']
        if extra_data['profile']['profile_image_url']:
            image_url=extra_data['profile']['profile_image_url']
            response=requests.get(image_url, stream=True)
            # Was the request OK?
            if response.status_code != requests.codes.ok:
                # Nope, error handling, skip file etc etc etc
                return            
            # Get the filename from the url, used for saving later
            file_name = image_url.split('/')[-1]
            # Create a temporary file
            lf = tempfile.NamedTemporaryFile()
            # Read the streamed image in sections
            for block in response.iter_content(1024 * 8):                
                # If no more file then stop
                if not block:
                    break
                # Write image block to temporary file
                lf.write(block)
            user.avatar.save(file_name, files.File(lf))

        # if extra_data['has_phone_number'] == True:
        #     phone_number = extra_data['phone_number']
        #     name = extra_data.get('name')
        #     vf, created = Verification.objects.update_or_create(
        #         user=user,
        #         defaults={
        #             'phone': phone_number,
        #             'name':name
        #             }
        #     )
        # else:
        #     pass
    elif instance.provider == "naver":
        pass
        # extra_data = instance.extra_data
        # if extra_data.get('mobile', None) is not None:
        #     phone_number = extra_data['mobile'].replace('-','')
        #     name = extra_data.get('name')
        #     vf, created = Verification.objects.update_or_create(
        #         user=user,
        #         defaults={
        #             'phone': phone_number,
        #             'name': name,
        #         }
        #     )
        # else:
        #     pass
    return

