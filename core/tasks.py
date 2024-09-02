from celery import shared_task
from decouple import config
from random import randint
from datetime import datetime, timedelta
import time, base64, hmac, hashlib, json, requests
import os, copy
from auction.models import Placement, PlacementBid
from user.models import AdminPhone
from .models import CrowdFundingOrderItem, OpenFundingOrderItem, Questionanswer, SecretFundingOrderItem, Kakao_Result
from user.models import Users

file_path1 = os.path.join(os.path.dirname(__file__), 'KAKAO_TEMPLATE.json')
with open(file_path1, 'r') as f:
    KAKAO_TEMPLATE = json.load(f)
file_path2 = os.path.join(os.path.dirname(__file__), 'SMS_TEMPLATE.json')
with open(file_path2, 'r') as f:
    SMS_TEMPLATE = json.load(f)


import time, functools
from django.core.cache import cache

CACHE_LOCK_EXPIRE = 1*60

def no_simultaneous_execution(f):
    """
    LOCK을 걸어 제한시간내, 다시 실행되지 못하게 하는 decorator
    (60초 이상 delay를 가진 work에만 적용)
    """
    @functools.wraps(f)
    def wrapper(self, *args, **kwargs):
        # Create lock_id used as cache key
        lock_id = '{}-{}-{}'.format(self.name, args, kwargs)

        # Timeout with a small diff, so we'll leave the lock delete
        # to the cache if it's close to being auto-removed/expired
        timeout_at = time.monotonic() + CACHE_LOCK_EXPIRE - 3

        # Try to acquire a lock, or put task back on queue
        lock_acquired = cache.add(lock_id, True, CACHE_LOCK_EXPIRE)
        if not lock_acquired:
            print(f"LOCKED, {self.name}")
             # self.apply_async(args=args, kwargs=kwargs, countdown=3)
            return
        try:
            f(self, *args, **kwargs)
        finally:
            # Release the lock
            if time.monotonic() > timeout_at:
                cache.delete(lock_id)
    return wrapper



@shared_task(bind=True)
@no_simultaneous_execution
def simulation(self, *args, **kwargs):
    print('동시성 작업/TEST')
    return

@shared_task(bind=True)
@no_simultaneous_execution
def DeleteUser(self, *args, **kwargs):
    id=kwargs['id']
    try:
        User=Users.objects.get(id=id)
        User.delete()
    except Users.DoesNotExist:
        pass

@shared_task(bind=True)
@no_simultaneous_execution
def AdminPhone_SMS_Send(self, *args, **kwargs):
    AUTH_SECRET_KEY = config('AUTH_SECRET_KEY')
    AUTH_ACCESS_KEY = config('AUTH_ACCESS_KEY')
    SERVICEID = config('SERVICEID')
    SMS_URL = 'https://sens.apigw.ntruss.com/sms/v2/services/' + f'{SERVICEID}' + '/messages'
    SMS_SEND_PHONE_NUMBER = config('SMS_SEND_PHONE_NUMBER')

    content=args[0]
    timestamp = str(int(time.time() * 1000))
    secret_key = bytes(AUTH_SECRET_KEY, 'utf-8')
    method = 'POST'
    uri = '/sms/v2/services/' + f'{SERVICEID}' + '/messages'
    message = method + ' ' + uri + '\n' + timestamp + '\n' + AUTH_ACCESS_KEY
    message = bytes(message, 'utf-8')
    # 알고리즘으로 암호화 후, base64로 인코딩
    signingKey = base64.b64encode(
        hmac.new(secret_key, message, digestmod=hashlib.sha256).digest())
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'x-ncp-apigw-timestamp': timestamp,
        'x-ncp-iam-access-key': AUTH_ACCESS_KEY,
        'x-ncp-apigw-signature-v2': signingKey,
    }
    admin_phones = AdminPhone.objects.filter(activate=True)
    body = {
        'type': 'SMS',
        'contentType': 'COMM',
        'countryCode': '82',
        'from': f'{SMS_SEND_PHONE_NUMBER}',
        'content': f'{content}',
        'messages': [{'to':admin_phone.standardize_phone()} for admin_phone in admin_phones]
    }

    # body를 json으로 변환
    encoded_data = json.dumps(body)

    # post 메서드로 데이터를 보냄
    try:
        res = requests.post(SMS_URL, headers=headers, data=encoded_data)
    except:
        pass


@shared_task
def Phone_SMS_Send(phone, content):
    AUTH_SECRET_KEY = config('AUTH_SECRET_KEY')
    AUTH_ACCESS_KEY = config('AUTH_ACCESS_KEY')
    SERVICEID = config('SERVICEID')
    SMS_URL = 'https://sens.apigw.ntruss.com/sms/v2/services/' + f'{SERVICEID}' + '/messages'
    SMS_SEND_PHONE_NUMBER = config('SMS_SEND_PHONE_NUMBER')

    timestamp = str(int(time.time() * 1000))
    secret_key = bytes(AUTH_SECRET_KEY, 'utf-8')
    method = 'POST'
    uri = '/sms/v2/services/' + f'{SERVICEID}' + '/messages'
    message = method + ' ' + uri + '\n' + timestamp + '\n' + AUTH_ACCESS_KEY
    message = bytes(message, 'utf-8')
    # 알고리즘으로 암호화 후, base64로 인코딩
    signingKey = base64.b64encode(
        hmac.new(secret_key, message, digestmod=hashlib.sha256).digest())
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'x-ncp-apigw-timestamp': timestamp,
        'x-ncp-iam-access-key': AUTH_ACCESS_KEY,
        'x-ncp-apigw-signature-v2': signingKey,
    }

    body = {
        'type': 'SMS',
        'contentType': 'COMM',
        'countryCode': '82',
        'from': f'{SMS_SEND_PHONE_NUMBER}',
        'content': f'{content}',
        'messages': [
            {
                'to': phone
            }
        ]
    }

    # body를 json으로 변환
    encoded_data = json.dumps(body)

    # post 메서드로 데이터를 보냄
    try:
        res = requests.post(SMS_URL, headers=headers, data=encoded_data)
    except:
        pass

BSID="revenor"
PASSWD="a5113e571e6b0b6898f9474e4e5f872ce3cbc019"
SENDERKEY="e21cfa2fd0450fc5168b317c3eae4d986271ed25"
def GET_KAKAO_TOKEN():
    url = "https://www.biztalk-api.com/v2/auth/getToken"
    data = {
        "bsid" : BSID,
        "passwd" : PASSWD,
        "expire" : "1440",
    }
    headers={
        "Content-Type" : "application/json"
    }
    response = requests.post(url, json=data, headers=headers)
    res = response.json()
    return res

@shared_task(bind=True)
def GET_KAKAO_RESULT(self, *args, **kwargs):
    token = GET_KAKAO_TOKEN()['token']
    url = "https://www.biztalk-api.com/v2/kko/getResultAll"
    headers = {
        "bt-token" : token,
        "Content-Type" : "application/json;charset=utf-8"
    }
    response = requests.get(url, headers=headers)
    if response.json().get('responseCode') == '1000':
        GW=response.json().get('responseCode')
        res=response.json().get('response')
        #RESULT 객체 만들기
        klist=[]
        for r in res:
            klist.append(Kakao_Result(
                status=r.get('resultCode'),
                text=r
            ))
        Kakao_Result.objects.bulk_create(klist)
    else:
        pass
        # print('메시지를 성공적으로 보내지 못했습니다. 오류메시지 : ' + str(response.json()))    

def Enrich_Message(tmpltCode, params):
    message=KAKAO_TEMPLATE[tmpltCode]['message']
    if tmpltCode == "v2_signup":
        message=message.replace("#{USERNAME}", params['USERNAME'])
    elif tmpltCode == "v2_bid_withdraw":
        message=message.replace("#{USERNAME}", params['USERNAME']).replace("#{TITLE}",params['TITLE']).replace("#{PRICE}", format(int(params['PRICE']),","))
    elif tmpltCode == "v2_bid_refund":
        message=message.replace("#{USERNAME}", params['USERNAME']).replace("#{TITLE}",params['TITLE']).replace("#{PRICE}", format(int(params['PRICE']),","))
    elif tmpltCode == "v3_bid_before_finish_push":
        message=message.replace("#{USERNAME}", params['USERNAME']).replace("#{TITLE}",params['TITLE'])
    elif tmpltCode == "v2_bid_finish_push":
        message=message.replace("#{USERNAME}", params['USERNAME']).replace("#{TITLE}",params['TITLE'])
    elif tmpltCode == "v2_bid_pay_push":
        message=message.replace("#{USERNAME}", params['USERNAME']).replace("#{TITLE}",params['TITLE']).replace("#{TIME}",params['TIME'])
    elif tmpltCode == "v2_bid_encore_push":
        message=message.replace("#{USERNAME}", params['USERNAME']).replace("#{TITLE}",params['TITLE'])                
    elif tmpltCode == "v2_bid_alarm_push":
        message=message.replace("#{USERNAME}", params['USERNAME']).replace("#{TITLE}",params['TITLE'])
    elif tmpltCode == "v2_bid_survey_push":
        message=message.replace("#{USERNAME}", params['USERNAME']).replace("#{TITLE}",params['TITLE'])
    elif tmpltCode == "v2_bid_ticket":
        message=message.replace("#{USERNAME}", params['USERNAME']).replace("#{TITLE}",params['TITLE']).replace("#{PLACE}",params['PLACE']).replace("#{TIME}",params['TIME'])     
    elif tmpltCode == "v2_crowd_bid_1":
        message=message.replace("#{USERNAME}", params['USERNAME']).replace("#{TITLE}",params['TITLE']).replace("#{PRICE}", format(int(params['PRICE']),","))
    elif tmpltCode == "v2_crowd_bid_3_y":
        message=message.replace("#{USERNAME}", params['USERNAME']).replace("#{TITLE}",params['TITLE']).replace("#{PRICE}", format(int(params['PRICE']),","))
    elif tmpltCode == "v2_crowd_bid_3_n":
        message=message.replace("#{USERNAME}", params['USERNAME']).replace("#{TITLE}",params['TITLE']).replace("#{PRICE}", format(int(params['PRICE']),","))
    elif tmpltCode == "v2_crowd_bid_4_y":
        message=message.replace("#{USERNAME}", params['USERNAME']).replace("#{TITLE}",params['TITLE'])
    elif tmpltCode == "crowd_bid_4_n":
        message=message.replace("#{USERNAME}", params['USERNAME']).replace("#{TITLE}",params['TITLE'])
    elif tmpltCode == "v2_secret_bid_0":
        message=message.replace("#{USERNAME}", params['USERNAME']).replace("#{TITLE}",params['TITLE']).replace("#{PRICE}", format(int(params['PRICE']),","))
    elif tmpltCode == "v2_secret_bid_1_n":
        message=message.replace("#{USERNAME}", params['USERNAME']).replace("#{TITLE}",params['TITLE'])
    elif tmpltCode == "v2_secret_bid_1_y":
        message=message.replace("#{USERNAME}", params['USERNAME']).replace("#{TITLE}",params['TITLE']).replace("#{PRICE}", format(int(params['PRICE']),",")).replace("#{DEPOSIT}", format(int(params['DEPOSIT']),","))
    elif tmpltCode == "v2_secret_bid_2_n":
        message=message.replace("#{USERNAME}", params['USERNAME']).replace("#{TITLE}",params['TITLE']).replace("#{PRICE}", format(int(params['PRICE']),","))
    elif tmpltCode == "v2_secret_bid_2_y":
        message=message.replace("#{USERNAME}", params['USERNAME']).replace("#{TITLE}",params['TITLE']).replace("#{PRICE}", format(int(params['PRICE']),",")).replace("#{PRICE_CALC}", format(int(params['PRICE_CALC']),","))
    elif tmpltCode == "v2_secret_bid_3_n":
        message=message.replace("#{USERNAME}", params['USERNAME']).replace("#{TITLE}",params['TITLE']).replace("#{PRICE}", format(int(params['PRICE']),","))
    elif tmpltCode == "v2_secret_bid_3_y":
        message=message.replace("#{USERNAME}", params['USERNAME']).replace("#{TITLE}",params['TITLE'])
    elif tmpltCode == "v2_secret_bid_4_y":
        message=message.replace("#{USERNAME}", params['USERNAME']).replace("#{TITLE}",params['TITLE'])
    else:
        #Error
        raise NameError("메시지 템플릿이 올바르지 않습니다")
    return message


#Button URL PC기준
def Enrich_Attach_Url(tmpltCode, params):
    _new_attach=KAKAO_TEMPLATE[tmpltCode].get('attach', {})
    new_attach=copy.deepcopy(_new_attach)
    if new_attach == {}:
        pass
    else:
        if tmpltCode == "v2_bid_alarm_push" or tmpltCode == "v2_crowd_bid_3_n" or tmpltCode == 'v3_bid_before_finish_push':
            for button_index, value in params['BUTTON'].items():
                new_attach['button'][int(button_index)]['url_mobile']=new_attach['button'][int(button_index)]['url_mobile'].replace("#{PID}", str(value))
                new_attach['button'][int(button_index)]['url_pc']=new_attach['button'][int(button_index)]['url_pc'].replace("#{PID}", str(value))

        elif tmpltCode == "v2_bid_survey_push" or tmpltCode == "v2_bid_ticket" or tmpltCode =="v2_crowd_bid_4_y" or tmpltCode == "v2_secret_bid_4_y":
            for button_index, value in params['BUTTON'].items():
                new_attach['button'][int(button_index)]['url_mobile']=new_attach['button'][int(button_index)]['url_mobile'].replace("#{SLUG}", str(value['SLUG'])).replace("#{OID}", str(value['OID']))
                new_attach['button'][int(button_index)]['url_pc']=new_attach['button'][int(button_index)]['url_pc'].replace("#{SLUG}", str(value['SLUG'])).replace("#{OID}", str(value['OID']))
        else:
            pass
    return new_attach

#BATCH
@shared_task(bind=True)
@no_simultaneous_execution
def Biz_KAKAO_Send(self, *args, **kwargs):
    try :
        phones_parmas = kwargs['phones_params']
        tmpltCode = kwargs['tmpltCode']
        res = GET_KAKAO_TOKEN()
        _msgList=[]
        for p_dict in phones_parmas:
            key=list(p_dict.keys())[0]
            if tmpltCode == 'signup':
                _msgList.append({
                    "msgIdx" : f"{int(datetime.now().timestamp()/3600)}",
                    "countryCode" : "82",
                    "resMethod" : "PUSH",
                    "senderKey" : SENDERKEY,
                    "tmpltCode" : tmpltCode,
                    "message" : Enrich_Message(tmpltCode, p_dict[key]),
                    "messageType" : KAKAO_TEMPLATE[tmpltCode].get('messageType', 'AT'),
                    "recipient" : key,
                    "attach": Enrich_Attach_Url(tmpltCode, p_dict[key]),
                    # "supplement": KAKAO_TEMPLATE[tmpltCode].get('supplement', {})
                })
            else:
                _msgList.append({
                    "msgIdx" : f"{int(datetime.now().timestamp()/3600)}",
                    "countryCode" : "82",
                    "resMethod" : "PUSH",
                    "senderKey" : SENDERKEY,
                    "tmpltCode" : tmpltCode,
                    "message" : Enrich_Message(tmpltCode, p_dict[key]),
                    "messageType" : KAKAO_TEMPLATE[tmpltCode].get('messageType', 'AT'),
                    "recipient" : key,
                    "attach": Enrich_Attach_Url(tmpltCode, p_dict[key]),
                    # "supplement": KAKAO_TEMPLATE[tmpltCode].get('supplement', {}),
                    "title" : KAKAO_TEMPLATE[tmpltCode].get('title', ''),
                })

        url = "https://www.biztalk-api.com/v2/kko/sendAlimTalkBatch"
        headers = {
            "bt-token" : res["token"],
            "Content-Type" : "application/json;charset=utf-8"
        }
        data = {
            "msgList":_msgList
        }
        response = requests.post(url, json=data, headers=headers)
    except Exception as e:
        print(e)
        #결과저장->
        pass


#주문서 생성 후(crowd=20분 후, open&secret=3시간 후, 7일 뒤)
@shared_task(bind=True)
@no_simultaneous_execution
def Make_OrderItem_Expired(self, *args, **kwargs):
    pk=kwargs['pk']
    slug=kwargs['slug']
    try:
        phones_params=[]
        tmpltCode=''
        if slug == 'crowdfunding':
            oi = CrowdFundingOrderItem.objects.get(pk=pk)
            if oi.deliver_detail == 1 and oi.expired == False:
                oi.expired = True
                oi.save()                
                tmpltCode='v2_crowd_bid_3_n'

        elif slug == 'secretfunding':
            oi = SecretFundingOrderItem.objects.get(pk=pk)
            if oi.deliver_detail == 1 and oi.expired == False:
                oi.expired = True
                oi.save()

                oi.placement.placement_win = None
                oi.placement.save()
                tmpltCode='v2_secret_bid_2_n'

            elif oi.deliver_detail == 2 and oi.expired == False:
                oi.expired = True
                oi.save()

                oi.placement.placement_win = None
                oi.placement.save()                
                tmpltCode='v2_secret_bid_3_n'

        elif slug == 'openfunding':
            oi = OpenFundingOrderItem.objects.get(pk=pk)
            if oi.deliver_detail == 1 and oi.expired == False:
                oi.expired = True
                oi.save()            
                tmpltCode=''                

            elif oi.deliver_detail == 2 and oi.expired == False:
                oi.expired = True
                oi.save()                
                tmpltCode=''
        #한꺼번에
        if tmpltCode != '':
            if tmpltCode == 'v2_crowd_bid_3_n':
                phone=oi.user.verification.standardize_phone()
                params={
                    'USERNAME':oi.user.username,
                    'TITLE':oi.placement.title,
                    'PRICE':oi.get_final_price(),
                    'BUTTON':{
                        1:oi.placement.id,
                    },                    
                }
                phones_params.append({phone:params})
            else:
                phone=oi.user.verification.standardize_phone()
                params={
                    'USERNAME':oi.user.username,
                    'TITLE':oi.placement.title,
                    'PRICE':oi.get_final_price(),
                }
                phones_params.append({phone:params})

            AdminPhone_SMS_Send.apply_async(args=[f"시간만료[{oi.id}]\n유저:{oi.user.username}[{oi.user.id}]\n상품:{oi.placement.title[:5]}..."], ignore_result=False)
            Biz_KAKAO_Send.apply_async(kwargs={'phones_params':phones_params, 'tmpltCode':tmpltCode}, ignore_result=False)
            # print(phones_params)
            # Biz_KAKAO_Send.run(phones_params=phones_params, tmpltCode=tmpltCode)
            
    except: #주문서가 없을때
        pass

    return

#주문서 생성 후(crowd=15분 후, open&secret=2시간 후)
@shared_task(bind=True)
@no_simultaneous_execution
def Before_Make_OrderItem_Expired(self, *args, **kwargs):
    pk=kwargs['pk']
    slug=kwargs['slug']
    tmpltCode=''
    timelimit=''
    try:
        phones_params=[]        
        if slug == 'crowdfunding':
            oi = CrowdFundingOrderItem.objects.get(pk=pk)
            if oi.deliver_detail == 1 and oi.expired == False:
                tmpltCode='v2_bid_pay_push'
                timelimit='5분'

        elif slug == 'secretfunding':
            oi = SecretFundingOrderItem.objects.get(pk=pk)
            if oi.deliver_detail == 1 and oi.expired == False:
                tmpltCode='v2_bid_pay_push'
                timelimit='1시간'
                
            elif oi.deliver_detail == 2 and oi.expired == False:
                tmpltCode='v2_bid_pay_push'
                timelimit='1시간'

        elif slug == 'openfunding':
            oi = OpenFundingOrderItem.objects.get(pk=pk)
            if oi.deliver_detail == 1 and oi.expired == False:
                tmpltCode='v2_bid_pay_push'
                timelimit='1시간'
                
            elif oi.deliver_detail == 2 and oi.expired == False:
                tmpltCode='v2_bid_pay_push'
                timelimit='1시간'

        if tmpltCode != '' and timelimit != '':
            phone=oi.user.verification.standardize_phone()
            params={
                'USERNAME':oi.user.username,
                'TITLE':oi.placement.title,
                'TIME':timelimit,
            }
            phones_params.append({phone:params})
            Biz_KAKAO_Send.apply_async(kwargs={'phones_params':phones_params, 'tmpltCode':tmpltCode}, ignore_result=False)
    except: #주문서가 없을때
        pass
            
    return

@shared_task(bind=True)
@no_simultaneous_execution
def Auction_Encore_Push(self, *args, **kwargs):
    original_p = Placement.objects.get(pk=kwargs['original_pk'])
    p=Placement.objects.get(pk=kwargs['pk'])
    users=[]
    for user in original_p.encores.all():
        try:
            if user.verification.standardize_phone():
                users.append(user)
        except:
            continue

    phones_params=[]
    for u in users:
        phone=u.verification.standardize_phone()
        params={
            'USERNAME':u.username,
            'TITLE':p.title,
        }
        phones_params.append({phone:params})
    tmpltCode='v2_bid_encore_push'
    Biz_KAKAO_Send.apply_async(kwargs={'phones_params':phones_params, 'tmpltCode':tmpltCode}, ignore_result=False)
    AdminPhone_SMS_Send.apply_async(args=[f"앵콜설정발송\n유저:{len(users)}명\n본상품:{original_p.title[:5]}...\n앵콜상품:{p.title[:5]}..."], ignore_result=False)

#When Start
@shared_task(bind=True)
@no_simultaneous_execution
def Auction_Alarm_Push(self, *args, **kwargs):
    p=Placement.objects.get(pk=kwargs['pk'])
    users=[]
    for user in p.alarms.all():
        try:
            if user.verification.standardize_phone() and (user not in users):
                users.append(user)
        except:
            continue
    for user in p.plikes.all():
        try:
            if user.verification.standardize_phone() and (user not in users):
                users.append(user)
        except:
            continue
    phones_params=[]
    for u in users:
        phone=u.verification.standardize_phone()
        params={
            'USERNAME':u.username,
            'TITLE':p.title,
            'BUTTON':{
                0:p.id
            }
        }
        phones_params.append({phone:params})
    tmpltCode='v2_bid_alarm_push'
    Biz_KAKAO_Send.apply_async(kwargs={'phones_params':phones_params, 'tmpltCode':tmpltCode}, ignore_result=False)
    AdminPhone_SMS_Send.apply_async(args=[f"알림설정발송\n유저:{len(users)}명\n상품:{p.title[:5]}..."], ignore_result=False)


#Before Finish before 1h
@shared_task(bind=True)
@no_simultaneous_execution
def Auction_Before_Finish_Push(self, *args, **kwargs):
    p=Placement.objects.get(pk=kwargs['pk'])
    users=[]
    if p.placement_type == 'crowdfunding':
        for donation in p.donation_set.all():
            user=donation.user
            try:
                if user.verification.standardize_phone() and (user not in users):
                    users.append(user)
            except:
                continue

    #OPEN, SECRET
    else:
        for pbd in p.placementbid_set.all():
            user=pbd.user
            try:
                if user.verification.standardize_phone() and (user not in users):
                    users.append(user)
            except:
                continue

    phones_params=[]
    for u in users:
        phone=u.verification.standardize_phone()
        params={
            'USERNAME':u.username,
            'TITLE':p.title,
            'BUTTON':{
                0:p.id
            },
        }
        phones_params.append({phone:params})
    tmpltCode='v3_bid_before_finish_push'
    Biz_KAKAO_Send.apply_async(kwargs={'phones_params':phones_params, 'tmpltCode':tmpltCode}, ignore_result=False)

#When Finish
@shared_task(bind=True)
@no_simultaneous_execution
def Auction_Finish_Push(self, *args, **kwargs):
    p=Placement.objects.get(pk=kwargs['pk'])
    users=[]
    # placement_win_crowdfunding
    if p.placement_type == 'crowdfunding':
        for donation in p.donation_set.all():
            user=donation.user
            try:
                if user.verification.standardize_phone() and (user not in users):
                    users.append(user)
            except:
                continue

        #종료 알림
        phones_params=[]
        for u in users:
            try:
                phone=u.verification.standardize_phone()
                params={
                    'USERNAME':u.username,
                    'TITLE':p.title,
                }
                phones_params.append({phone:params})
            except:
                pass
        tmpltCode='v2_bid_finish_push'
        Biz_KAKAO_Send.apply_async(kwargs={'phones_params':phones_params, 'tmpltCode':tmpltCode}, ignore_result=False)
        AdminPhone_SMS_Send.apply_async(args=[f"판매종료\n옥션:{p.title[:5]}...\n유저:{len(users)}명"], ignore_result=False)

    #OPEN, SECRET
    else:
        for pbd in p.placementbid_set.all():
            user=pbd.user
            try:
                if user.verification.standardize_phone() and (user not in users):
                    users.append(user)
            except:
                continue

        #종료 알림
        phones_params=[]
        for u in users:
            try:
                phone=u.verification.standardize_phone()
                params={
                    'USERNAME':u.username,
                    'TITLE':p.title,
                }
                phones_params.append({phone:params})
            except:
                pass
        tmpltCode='v2_bid_finish_push'
        Biz_KAKAO_Send.apply_async(kwargs={'phones_params':phones_params, 'tmpltCode':tmpltCode}, ignore_result=False)
        AdminPhone_SMS_Send.apply_async(args=[f"판매종료\n옥션:{p.title[:5]}...\n유저:{len(users)}명"], ignore_result=False)

