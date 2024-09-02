from datetime import timedelta
from decouple import config
from django.contrib import messages
from decouple import config
from random import randint
import time, base64, hmac, hashlib, json, requests, re, pytz

def Phone_Number_Standardize(phone):

    '''
    010 1234 5678
    010-1234-5678
    01012345678
    +82 10 1234 5678
    +82 010 1234 5678
    +82) 10 1234 5678
    +82) 010 1234 5678
    +82)1012345678
    +82-10-1234-5678
    +8201012345678
    +821012345678
    '''
    
    phone=phone.replace('-','').replace(' ','')    
    #E.164
    p=re.compile('^\+(?:[0-9]?){6,14}[0-9]$')
    if p.match(phone):
        if phone[0] == '+':
            phone='0'+phone[3:]
        else:
            phone='0'+phone[2:]

    '''
    Standardized Phone Number
    '''
    return phone

def SeoulToUTC(t):
    bj_tz = pytz.timezone('Asia/Seoul')
    bj_dt = bj_tz.localize(t)
    return bj_dt.astimezone(pytz.UTC)

def ToUTC(dt):
    return dt-timedelta(hours=9)

def is_mobile(request):
    """
    Return True if the request comes from a mobile device.
    """
    MOBILE_AGENT_RE=re.compile(r".*(iPhone|iPad|iPad|Android|Windows CE|BlackBerry|Symbian|Windows Phone|webOS|Opera Mini|Opera Mobi|POLARIS|IEMobile|lgtelecom|nokia|SonyEricsson|LG|SAMSUNG|Samsung)",re.IGNORECASE)

    if MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
        return True
    else:
        return False
    
def remove_tags(string):
    # remove all tags

    # as per recommendation from @freylis, compile once only
    CLEANR = re.compile('<.*?>')        
    string = re.sub(CLEANR, '', string)
    return string