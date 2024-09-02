from core.tasks import GET_KAKAO_RESULT, AdminPhone_SMS_Send, Biz_KAKAO_Send, simulation
from user.models import Users
from allauth.socialaccount.models import SocialAccount
from django.core import files
import requests, tempfile

class TEST:
  def avatar(self):
    for instance in SocialAccount.objects.all():
      user = Users.objects.get(id=instance.user.id)
      if instance.provider == "kakao":
        print(instance, user)
        extra_data = instance.extra_data['kakao_account']
        if extra_data['profile']['profile_image_url']:
            image_url=extra_data['profile']['profile_image_url']
            response=requests.get(image_url, stream=True)
            # Was the request OK?
            if response.status_code != requests.codes.ok:
                print("이게뭐람!", instance, user, response.status_code, requests.codes.ok)
                # Nope, error handling, skip file etc etc etc
                continue
            # Get the filename from the url, used for saving later  
            img_n=image_url.split('/')[-1]            
            ext = img_n.split('.')[-1]
            file_name=f"{user.username}.{ext}"
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
            lf.close()

  def simulation_test(self):
    simulation.apply_async(kwargs={'a':'d'}, countdown=5)
    
  def phone_send(self):
    AdminPhone_SMS_Send.run("TEST")
    
  def kakao_result(self):
    GET_KAKAO_RESULT()

  def kakao_send(self):
    phones_params=[]
    tmpltCode = input("템플릿 코드 입력 : ")    
    users = Users.objects.filter(id__in=['5'])
    for u in users:
        phone=u.verification.standardize_phone()
        if tmpltCode=='v2_signup':
          params={
              'USERNAME':u.username
          }
        elif tmpltCode=='v2_bid_withdraw':
          params={
              'USERNAME':u.username,
              'TITLE':'title',
              'PRICE':10000,                
          }
        elif tmpltCode=='v2_bid_refund':
          params={
              'USERNAME':u.username,
              'TITLE':'title',
              'PRICE':100000,                              
          }
        elif tmpltCode=='v2_bid_finish_push':
          params={
              'USERNAME':u.username,
              'TITLE':'title',
          }
        elif tmpltCode=='v3_bid_before_finish_push':
          params={
              'USERNAME':u.username,
              'TITLE':'title',
              'BUTTON':{
                0:1
              }
          }          
        elif tmpltCode=='v2_bid_pay_push':
          params={
              'USERNAME':u.username,
              'TITLE':'title',
              'TIME':'10분',
          }
        elif tmpltCode=='v2_bid_encore_push':
          params={
              'USERNAME':u.username,
              'TITLE':'title'
          }
        elif tmpltCode=='v2_bid_alarm_push':
          params={
              'USERNAME':u.username,
              'TITLE':'title',
              'BUTTON':{
                0:1
              }
          }
        elif tmpltCode=='v2_bid_survey_push':
          params={
              'USERNAME':u.username,
              'TITLE':'title',
              'BUTTON':{
                0:{
                  'SLUG':'crowdfunding',
                  'OID':11,
                }
              }
          }
        elif tmpltCode=='v2_bid_ticket':
          params={
              'USERNAME':u.username,
              'TITLE':'title',
              'PLACE':'강남구 서초동',
              'TIME':"2022. 10. 5. 6시",
              'BUTTON':{
                0:{
                  'SLUG':'crowdfunding',
                  'OID':51,
                }
              }
          }          
        elif tmpltCode=='v2_crowd_bid_1':
          params={
              'USERNAME':u.username,
              'TITLE':'title\n\rtitle',
              'PRICE':10000
          }
        elif tmpltCode=='v2_crowd_bid_3_y':
          params={
              'USERNAME':u.username,
              'TITLE':'title',
              'PRICE':10000
          }
        elif tmpltCode=='v2_crowd_bid_3_n':
          params={
              'USERNAME':u.username,
              'TITLE':'title',
              'PRICE':10000,
              'BUTTON':{
                  1:1,
              },
          }
        elif tmpltCode=='v2_crowd_bid_4_y':
          params={
              'USERNAME':u.username,
              'TITLE':'title',
              'BUTTON':{
                1:{
                  'SLUG':'crowdfunding',
                  'OID':51,
                }
              }
          }
        elif tmpltCode=='crowd_bid_4_n':
          params={
              'USERNAME':u.username,
              'TITLE':'title'
          }
        elif tmpltCode=='v2_secret_bid_0':
          params={
              'USERNAME':u.username,
              'TITLE':'title',
              'PRICE':10000,
          }
        elif tmpltCode=='v2_secret_bid_1_n':
          params={
              'USERNAME':u.username,
              'TITLE':'title'
          }
        elif tmpltCode=='v2_secret_bid_1_y':
          params={
              'USERNAME':u.username,
              'TITLE':'title',
              'PRICE':10000,
              'DEPOSIT':3000000,
          }
        elif tmpltCode=='v2_secret_bid_2_n':
          params={
              'USERNAME':u.username,
              'TITLE':'title',
              'PRICE':10000,              
          }
        elif tmpltCode=='v2_secret_bid_2_y':
          params={
              'USERNAME':u.username,
              'TITLE':'title',
              'PRICE':100000,
              'PRICE_CALC':300000,
          }
        elif tmpltCode=='v2_secret_bid_3_n':
          params={
              'USERNAME':u.username,
              'TITLE':'title',
              'PRICE':10000,              
          }
        elif tmpltCode=='v2_secret_bid_3_y':
          params={
              'USERNAME':u.username,
              'TITLE':'title',
          }
        elif tmpltCode=='v2_secret_bid_4_y':
          params={
              'USERNAME':u.username,
              'TITLE':'title',
              'BUTTON':{
                1:{
                  'SLUG':'crowdfunding',
                  'OID':11,
                }
              }
          }
        phones_params.append({phone:params})

    Biz_KAKAO_Send.run(phones_params=phones_params, tmpltCode=tmpltCode)
    # Biz_KAKAO_Send.apply_async(kwargs={'phones_params':phones_params, 'tmpltCode':tmpltCode}, ignore_result=False)