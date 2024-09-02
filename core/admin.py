import json, copy
from django.contrib import admin
from django.contrib import messages
from core.utils import SeoulToUTC, ToUTC
from .models import Coupon, ElasticInfo, Partnership, Posts, Comments, Article_Comments, Articles, CrowdFundingOrderItem, Questionanswer, Questionnaire, SecretFundingOrderItem, OpenFundingOrderItem, Payment, Kakao_Result
from datetime import datetime, timedelta
from auction.models import Donation
from core.tasks import AdminPhone_SMS_Send, Before_Make_OrderItem_Expired, Biz_KAKAO_Send, Make_OrderItem_Expired
from django_celery_beat.models import PeriodicTask, ClockedSchedule
from django.utils.safestring import mark_safe
from django.contrib.admin import SimpleListFilter

admin.site.register(ElasticInfo)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
                    'id',
                    'user',
                    'imp_uid',
                    'status',
                    'amount',
                    'pay_method',
                    ]
    list_display_links = [
                    'id',
                    'user',
                    'imp_uid',
                    'status',
                    'amount',
                    'pay_method',
    ]
    list_filter = [
                    'id',
                    'user',
                    'imp_uid',
                    'status',
                    'amount',
                    'pay_method',
                   ]
    search_fields = [
                    'id',
                    'user__username',
                    'imp_uid',
                    'status',
                    'amount',
                    'pay_method',
    ]
    ordering = ['-created']
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = [
                    'id',
                    'title',
                    'user',
                    'amount',
                    'expired',
                    ]
    list_display_links = [
                    'id',
                    'title',                    
                    'user',
                    'amount',
                    'expired',
    ]
    list_filter = [
                    'id',
                    'title',                    
                    'user',
                    'placement',
                    'amount',
                    'expired',
                   ]
    search_fields = [
                    'id',
                    'title',
                    'user__username',
                    'placement__title',
                    'amount',
                    'expired',
    ]
    ordering = ['-created']
@admin.register(Questionnaire)
class QuestionnaireAdmin(admin.ModelAdmin):
    list_display = [
                    'id',        
                    'title',
                    ]
    list_display_links = [
                    'id',        
                    'title',
    ]
    list_filter = [
                    'id',        
                    'title',
                   ]
    search_fields = [
                    'id',        
                    'title',
    ]
    ordering = ['-created']
@admin.register(Questionanswer)
class QuestionanswerAdmin(admin.ModelAdmin):
    list_display = [
                    'id',        
                    'questionnaire',
                    'user'
                    ]
    list_display_links = [
                    'id',        
                    'questionnaire',
                    'user'
    ]
    list_filter = [
                    'id',        
                    'questionnaire',
                    'user'
                   ]
    search_fields = [
                    'id',        
                    'questionnaire__title',
                    'user__username'
    ]
    ordering = ['-created']
admin.site.register(Partnership)
def survey_push(modeladmin, request, queryset):
    for orderitem in queryset:
        if (not orderitem.expired):
            qa=Questionanswer.objects.get_or_none(cf_oi=orderitem)
            if qa is None:

                #카카오 메시지 v2_bid_survey_push
                phones_params=[]
                phone=orderitem.user.verification.standardize_phone()
                params={
                    'USERNAME':orderitem.user.username,
                    'TITLE':orderitem.placement.title,
                    'BUTTON':{
                        0:{
                            'SLUG':orderitem.placement.placement_type,
                            'OID': orderitem.id,
                        },
                    }
                }
                phones_params.append({phone:params})
                tmpltCode='v2_bid_survey_push'
                # Biz_KAKAO_Send.run(phones_params=phones_params, tmpltCode=tmpltCode)
                Biz_KAKAO_Send.apply_async(kwargs={'phones_params':phones_params, 'tmpltCode':tmpltCode}, ignore_result=False)
            else:
                pass
def f_refund_complete(orderitem):
    if orderitem.refund_granted and orderitem.expired:            
        #카카오 메시지 bid_refund
        phones_params=[]
        phone=orderitem.user.verification.standardize_phone()
        params={
            'USERNAME':orderitem.user.username,
            'TITLE':orderitem.placement.title,
            'PRICE':orderitem.get_final_price()
        }
        phones_params.append({phone:params})
        tmpltCode='v2_bid_refund'
        # Biz_KAKAO_Send.run(phones_params=phones_params, tmpltCode=tmpltCode)
        Biz_KAKAO_Send.apply_async(kwargs={'phones_params':phones_params, 'tmpltCode':tmpltCode}, ignore_result=False)
        AdminPhone_SMS_Send.apply_async(args=[f"결제금-환불완료\n유저:{orderitem.user.username}\n상품:{orderitem.placement.title[:5]+'...'}\n주문번호:{orderitem.id}\n*별도환불작업 必"], ignore_result=False)
        return True
    else:
        return False
def refund_complete(modeladmin, request, queryset):
    for orderitem in queryset:
        if not f_refund_complete(orderitem):
            messages.info(request, f'{orderitem}은 만료되지 않거나 환불요청이 승인되지 않은 주문서 입니다.')


def grant_withdraw(modeladmin, request, queryset):
    for orderitem in queryset:
        if orderitem.expired:
            messages.info(request, f'{orderitem}은 만료된 주문서입니다')
        if (not orderitem.refund_granted) and orderitem.refund_requested:
            #쿠폰 revert
            if orderitem.coupon:
                orderitem.coupon.expired=False
            #당첨자제거
            if orderitem.placement.placement_type=='crowdfunding':
                orderitem.placement.placement_win_crowdfunding.remove(orderitem.donation)
                orderitem.placement.save()
            else:
                if orderitem.placement.placement_win.id == orderitem.placementbid.id:
                    orderitem.placement.placement_win = None
                    orderitem.placement.save()


            orderitem.refund_granted = True
            orderitem.expired = True
            orderitem.save()
            #카카오 메시지 v2_crowd_bid_3_y
            #관리자 메시지
            phones_params=[]
            phone=orderitem.user.verification.standardize_phone()
            params={
                'USERNAME':orderitem.user.username,
                'TITLE':orderitem.placement.title,
                'PRICE':orderitem.get_final_price()
            }
            phones_params.append({phone:params})
            tmpltCode='v2_bid_withdraw'
            # Biz_KAKAO_Send.run(phones_params=phones_params, tmpltCode=tmpltCode)
            Biz_KAKAO_Send.apply_async(kwargs={'phones_params':phones_params, 'tmpltCode':tmpltCode}, ignore_result=False)
            AdminPhone_SMS_Send.apply_async(args=[f"주문서-환불완료\n유저:{orderitem.user.username}\n상품:{orderitem.placement.title[:5]+'...'}\n주문번호:{orderitem.id}"], ignore_result=False)

def f_crowd_make3_checkmake4(orderitem):
    f_crowd_make3(orderitem)
    f_crowd_checkmake4(orderitem.placement)
    # if (not orderitem.expired) and orderitem.placement.placement_type == 'crowdfunding':
    #     cp=orderitem.placement
    #     u=orderitem.user

    #     #make3
    #     orderitem.deliver_detail=3
    #     orderitem.save()

    #     #카카오 메시지 v2_crowd_bid_3_y
    #     #관리자 메시지
    #     phones_params=[]
    #     phone=u.verification.standardize_phone()
    #     params={
    #         'USERNAME':u.username,
    #         'TITLE':cp.title,
    #         'PRICE':orderitem.get_final_price()
    #     }
    #     phones_params.append({phone:params})
    #     tmpltCode='v2_crowd_bid_3_y'
    #     # Biz_KAKAO_Send.run(phones_params=phones_params, tmpltCode=tmpltCode)
    #     # AdminPhone_SMS_Send.run(f"입금확인\n유저:{u.username}\n상품:{cp.title[:5]}\n주문번호:{orderitem.id}")
    #     Biz_KAKAO_Send.apply_async(kwargs={'phones_params':phones_params, 'tmpltCode':tmpltCode}, ignore_result=False)
    #     AdminPhone_SMS_Send.apply_async(args=[f"입금확인\n유저:{u.username}\n상품:{cp.title[:5]+'...'}\n주문번호:{orderitem.id}"], ignore_result=False)

    #     #checkmake4
    #     users=[]
    #     win_donations=[]
    #     win_ois=[]
    #     cnt=0
    #     for donation in cp.donation_set.all():
    #         user=donation.user
    #         try:
    #             if user.verification.standardize_phone() and (user not in users):
    #                 users.append(user)
    #         except:
    #             continue
    #         try: 
    #             if (not donation.crowdfundingorderitem.expired) and donation.crowdfundingorderitem.deliver_detail>=3:
    #                 cnt+=donation.get_total_price()
    #                 #이번에 새로발굴
    #                 if donation.crowdfundingorderitem.deliver_detail==3:
    #                     win_donations.append(donation)
    #                     win_ois.append(donation.crowdfundingorderitem)
    #         except:
    #             pass            
    #     #크라우드 모금완료
    #     if cnt >= cp.placement_price:
    #         cp.placement_win_crowdfunding.add(*win_donations)
    #         cp.save()

    #         #make 4
    #         win_oi_list=CrowdFundingOrderItem.objects.filter(id__in=[oi.id for oi in win_ois])
    #         win_oi_list.update(deliver_detail=4)

    #         #카카오 메시지(v2_crowd_bid_4_y)
    #         #관리자 메시지
    #         phones_params=[]
    #         win_donations_user=[] 
    #         for user in [d.user for d in win_donations]:
    #             try:
    #                 if user.verification.standardize_phone() and (user not in win_donations_user):
    #                     win_donations_user.append(user)
    #             except:
    #                 continue

    #         for u in win_donations_user:
    #             phone=u.verification.standardize_phone()
    #             params={
    #                 'USERNAME':u.username,
    #                 'TITLE':cp.title,
    #                 'BUTTON':{
    #                     1:{
    #                         'SLUG':orderitem.placement.placement_type,
    #                         'OID':orderitem.id,
    #                     }
    #                 }
    #             }
    #             phones_params.append({phone:params})
    #         tmpltCode='v2_crowd_bid_4_y'
    #         Biz_KAKAO_Send.apply_async(kwargs={'phones_params':phones_params, 'tmpltCode':tmpltCode}, ignore_result=False)
    #         AdminPhone_SMS_Send.apply_async(args=[f"모금완료\n옥션:{cp.title[:5]}\n낙찰자:{len(win_donations_user)}명"], ignore_result=False)
    #     else:
    #         pass

def f_crowd_make3(orderitem):
    if (not orderitem.expired) and orderitem.placement.placement_type == 'crowdfunding':
        cp=orderitem.placement
        u=orderitem.user

        #make3(주문상태, 쿠폰)
        if orderitem.coupon:
            orderitem.coupon.expired=True
        orderitem.deliver_detail=3
        orderitem.save()

        #카카오 메시지 v2_crowd_bid_3_y
        #관리자 메시지
        phones_params=[]
        phone=u.verification.standardize_phone()
        params={
            'USERNAME':u.username,
            'TITLE':cp.title,
            'PRICE':orderitem.get_final_price()
        }
        phones_params.append({phone:params})
        tmpltCode='v2_crowd_bid_3_y'
        # Biz_KAKAO_Send.run(phones_params=phones_params, tmpltCode=tmpltCode)
        # AdminPhone_SMS_Send.run(f"입금확인\n유저:{u.username}\n상품:{cp.title[:5]}\n주문번호:{orderitem.id}")
        Biz_KAKAO_Send.apply_async(kwargs={'phones_params':phones_params, 'tmpltCode':tmpltCode}, ignore_result=False)
        AdminPhone_SMS_Send.apply_async(args=[f"입금확인\n유저:{u.username}\n상품:{cp.title[:5]+'...'}\n주문번호:{orderitem.id}"], ignore_result=False)

        return orderitem.placement
    else:
        return

def f_crowd_checkmake4(cp):
    #checkmake4
    users=[]
    win_donations=[]
    win_ois=[]
    cnt=0
    for donation in cp.donation_set.all():
        user=donation.user
        try:
            if user.verification.standardize_phone() and (user not in users):
                users.append(user)
        except:
            continue
        try: 
            if (not donation.crowdfundingorderitem.expired) and donation.crowdfundingorderitem.deliver_detail>=3:
                cnt+=donation.get_total_price()

                #이번에 새로발굴
                if donation.crowdfundingorderitem.deliver_detail==3:
                    win_donations.append(donation)
                    win_ois.append(donation.crowdfundingorderitem)                
        except:
            pass            
    #크라우드 모금완료
    if cnt >= cp.placement_price:
        cp.placement_win_crowdfunding.add(*win_donations)
        cp.save()

        #make 4
        win_oi_list=CrowdFundingOrderItem.objects.filter(id__in=[oi.id for oi in win_ois])
        if win_oi_list.count()==1:
            win_oi_list.first().deliver_detail=4
            win_oi_list.first().save()
        else:
            win_oi_list.update(deliver_detail=4)

        #카카오 메시지(v2_crowd_bid_4_y)
        #관리자 메시지
        phones_params=[]
        win_donations_user=[]
        _win_ois=[]
        for idx, user in enumerate([d.user for d in win_donations]):
            try:
                if user.verification.standardize_phone() and (user not in win_donations_user):
                    win_donations_user.append(user)
                    _win_ois.append(win_donations[idx].crowdfundingorderitem)
            except:
                continue

        for orderitem in _win_ois:
            phone=orderitem.user.verification.standardize_phone()
            params={
                'USERNAME':orderitem.user.username,
                'TITLE':cp.title,
                'BUTTON':{
                    1:{
                        'SLUG':cp.placement_type,
                        'OID':orderitem.id,
                    }
                }
            }
            phones_params.append({phone:params})
        tmpltCode='v2_crowd_bid_4_y'
        Biz_KAKAO_Send.apply_async(kwargs={'phones_params':phones_params, 'tmpltCode':tmpltCode}, ignore_result=False)
        AdminPhone_SMS_Send.apply_async(args=[f"모금완료\n옥션:{cp.title[:5]}...\n낙찰자:{len(win_donations_user)}명"], ignore_result=False)
    else:
        pass

def crowd_make3_checkmake4(modeladmin, request, queryset):
    placements=[]
    for orderitem in queryset:
        p=f_crowd_make3(orderitem)
        if p not in placements:
            placements.append(p)
    for placement in placements:
        f_crowd_checkmake4(placement)

def f_secret_open_make2(orderitem):
    if (not orderitem.expired)  and (orderitem.placement.placement_type == 'openfunding' or orderitem.placement.placement_type == 'secretfunding'):
        #쿠폰만료
        if orderitem.coupon:
            orderitem.coupon.expired=True

        orderitem.deliver_detail=2
        orderitem.due_date=datetime.now()+timedelta(days=7)
        orderitem.save()
        
        #카카오메시지 v2_secret_bid_2_y
        #관리자문자
        phones_params=[]
        phone=orderitem.user.verification.standardize_phone()
        params={
            'USERNAME':orderitem.user.username,
            'TITLE':orderitem.placement.title,
            'PRICE':orderitem.get_final_price(),
            'PRICE_CALC':orderitem.get_final_price()-orderitem.placement.deposit
        }
        phones_params.append({phone:params})
        tmpltCode='v2_secret_bid_2_y'
        Biz_KAKAO_Send.apply_async(kwargs={'phones_params':phones_params, 'tmpltCode':tmpltCode}, ignore_result=False)
        AdminPhone_SMS_Send.apply_async(args=[f"예약금입금완료\n유저:{orderitem.user.username}\n상품:{orderitem.placement.title[:5]+'...'}\n주문번호:{orderitem.id}"], ignore_result=False)

        #Expire 2개
        Before_Make_OrderItem_Expired.apply_async(kwargs={'pk':orderitem.id, 'slug':orderitem.placement.placement_type}, eta=SeoulToUTC(datetime.now())+timedelta(days=6, hours=23), expires=SeoulToUTC(datetime.now())+timedelta(days=7, hours=6))
        # clocked, _ = ClockedSchedule.objects.get_or_create(
        #     clocked_time=ToUTC(datetime.now()+timedelta(days=6, hours=23))
        # )
        # PeriodicTask.objects.create(
        #     clocked=clocked,
        #     expires=ToUTC(datetime.now()+timedelta(days=7, hours=6)),
        #     name=f"{orderitem.placement.title[:6]}-{orderitem.id}-Before_Make_OrderItem_Expired-{datetime.now()}",
        #     task="core.tasks.Before_Make_OrderItem_Expired",
        #     one_off=True,
        #     kwargs=json.dumps({
        #         'pk':orderitem.id,
        #         'slug':orderitem.placement.placement_type,
        #     }),
        # )
        Make_OrderItem_Expired.apply_async(kwargs={'pk':orderitem.id, 'slug':orderitem.placement.placement_type}, eta=SeoulToUTC(datetime.now())+timedelta(days=7), expires=SeoulToUTC(datetime.now())+timedelta(days=7, hours=6))
        # clocked, _ = ClockedSchedule.objects.get_or_create(
        #     clocked_time=ToUTC(datetime.now()+timedelta(days=7))
        # )
        # PeriodicTask.objects.create(
        #     clocked=clocked,
        #     expires=ToUTC(datetime.now()+timedelta(days=7, hours=6)),
        #     name=f"{orderitem.placement.title[:6]}-{orderitem.id}-Make_OrderItem_Expired-{datetime.now()}",
        #     task="core.tasks.Make_OrderItem_Expired",
        #     one_off=True,
        #     kwargs=json.dumps({
        #         'pk':orderitem.id,
        #         'slug':orderitem.placement.placement_type,
        #     }),
        # )

def secret_open_make2(modeladmin, request, queryset):
    for orderitem in queryset:
        f_secret_open_make2(orderitem)


def f_secret_open_make3(orderitem):
    if (not orderitem.expired) and (orderitem.placement.placement_type == 'openfunding' or orderitem.placement.placement_type == 'secretfunding'):
        #쿠폰만료
        if orderitem.coupon:
            orderitem.coupon.expired=True        
        orderitem.deliver_detail=3
        orderitem.save()
        
        #카카오메시지 v2_secret_bid_3_y
        #관리자문자
        phones_params=[]
        phone=orderitem.user.verification.standardize_phone()
        params={
            'USERNAME':orderitem.user.username,
            'TITLE':orderitem.placement.title,
            'PRICE':orderitem.get_final_price(),
        }
        phones_params.append({phone:params})
        tmpltCode='v2_secret_bid_3_y'
        Biz_KAKAO_Send.apply_async(kwargs={'phones_params':phones_params, 'tmpltCode':tmpltCode}, ignore_result=False)
        AdminPhone_SMS_Send.apply_async(args=[f"잔금입금완료\n유저:{orderitem.user.username}\n상품:{orderitem.placement.title[:5]+'...'}\n주문번호:{orderitem.id}"], ignore_result=False)

def secret_open_make3(modeladmin, request, queryset):
    for orderitem in queryset:
        f_secret_open_make3(orderitem)
        
def secret_open_make4(modeladmin, request, queryset):
    for orderitem in queryset:
        if (not orderitem.expired) and (orderitem.placement.placement_type == 'openfunding' or orderitem.placement.placement_type == 'secretfunding'):
            orderitem.deliver_detail=4
            orderitem.save()
            #카카오메시지 v2_secret_bid_4_y
            #관리자문자
            phones_params=[]
            phone=orderitem.user.verification.standardize_phone()
            params={
                'USERNAME':orderitem.user.username,
                'TITLE':orderitem.placement.title,
                'PRICE':orderitem.get_final_price(),
                'BUTTON':{
                    1:{
                        'SLUG':'secretfunding',
                        'OID':orderitem.id,
                    }
                }
            }
            phones_params.append({phone:params})
            tmpltCode='v2_secret_bid_4_y'
            Biz_KAKAO_Send.apply_async(kwargs={'phones_params':phones_params, 'tmpltCode':tmpltCode}, ignore_result=False)
            AdminPhone_SMS_Send.apply_async(args=[f"진행확정\n유저:{orderitem.user.username}\n상품:{orderitem.placement.title[:5]+'...'}\n주문번호:{orderitem.id}"], ignore_result=False)

def f_ticket_send(_oi=None, _queryset=None):
    phones_params=[]
    errors=[]
    if _queryset is not None and _oi is None:
        for oi in _queryset:
            if not oi.expired:
                phone=oi.user.verification.standardize_phone()
                params={
                    'USERNAME':oi.user.username,
                    'TITLE':oi.placement.title,
                    'PLACE':oi.placement.d_place,
                    'TIME':oi.placement.d_day.strftime("%Y. %m. %d. %H시"),
                    'BUTTON':{
                        0:{
                            'SLUG':oi.placement.placement_type,
                            'OID':oi.id
                        }
                    }
                }
                phones_params.append({phone:params})
            else:
                errors.append(oi.id)
                # messages.error(request, f"{oi.id}번 주문서는 만료되어 티켓을 보낼 수 없습니다.")
                continue

    elif _oi is not None and _queryset is None:
        if not _oi.expired:
            phone=_oi.user.verification.standardize_phone()
            params={
                'USERNAME':_oi.user.username,
                'TITLE':_oi.placement.title,
                'PLACE':_oi.placement.d_place,
                'TIME':_oi.placement.d_day.strftime("%Y. %m. %d. %H시"),
                'BUTTON':{
                    0:{
                        'SLUG':_oi.placement.placement_type,
                        'OID':_oi.id
                    }
                }
            }
            phones_params.append({phone:params})
        else:
            errors.append(_oi.id)
            # messages.error(request, f"{oi.id}번 주문서는 만료되어 티켓을 보낼 수 없습니다.")
            pass
    else: #에러
        return errors

    tmpltCode='v2_bid_ticket'    
    # Biz_KAKAO_Send.run(phones_params=phones_params, tmpltCode=tmpltCode)
    Biz_KAKAO_Send.apply_async(kwargs={'phones_params':phones_params, 'tmpltCode':tmpltCode}, ignore_result=False)
    AdminPhone_SMS_Send.apply_async(args=[f"초대장 개별 전송\n전송주문서:{len(phones_params)}개"], ignore_result=False)    
    return errors

def ticket_send(modeladmin, request, queryset):
    errors=f_ticket_send(_oi=None, _queryset=queryset)
    for e in errors:
        messages.error(request, f"{e}번 주문서는 만료되어 티켓을 보낼 수 없습니다.")




crowd_make3_checkmake4.short_description = '일반티켓 입금확인 & 종료확인'
secret_open_make2.short_description = '오픈&경쟁티켓 1차 예약금 완납'
secret_open_make3.short_description = '오픈&경쟁티켓 2차 잔금 완납'
secret_open_make4.short_description = '오픈&경쟁티켓 진행확정'
survey_push.short_description = '설문조사 PUSH(응답지 없을때만)'
grant_withdraw.short_description = '환불요청 수락(구매취소 완료)'
refund_complete.short_description = '환불완료'
ticket_send.short_description = '티켓 전송'

class BaseOrderItemAdmin(admin.ModelAdmin):
    def not_expired(self, post):
        if post.expired:
            return mark_safe(f"<span style='color:#d49d9d;' class='icon-cross'></span>")
        else:
            return mark_safe(f"<span style='color:#82b982;' class='icon-tick'></span>")
    not_expired.short_description='유효'
    def not_expired(self, post):
        if post.expired:
            return mark_safe(f"<span style='color:#d49d9d;' class='icon-cross'></span>")
        else:
            return mark_safe(f"<span style='color:#82b982;' class='icon-tick'></span>")
    not_expired.short_description='유효'
    list_display = [
                    'id',
                    'user',
                    'quantity',
                    'price',
                    'deliver_detail',
                    'not_expired',
                    ]
    list_display_links = [
                    'id',
                    'user',
                    'quantity',
                    'not_expired',
    ]
    list_filter = [
                    # 'id',
                    # 'user',
                    # 'quantity',
                    # 'price',
                    'deliver_detail',
                    'expired',
                    'refund_requested',
                    'refund_granted',
                   ]
    search_fields = [
                    'id',
                    'user__username',
                    'quantity',
                    'price',
                    'expired',
                    'deliver_detail',
                    'refund_account',                    
    ]
    ordering = ['expired','-updated']
    actions=[
        survey_push,grant_withdraw,
        refund_complete,
        ticket_send,
    ]
class PlacementFilter(SimpleListFilter):
    title = 'placement' # or use _('country') for translated title
    parameter_name = 'placement'

    def lookups(self, request, model_admin):
        placements=[]
        donations = set([oi.donation for oi in model_admin.model.objects.all().select_related('placement')])
        for d in donations:
            if not d.placement in placements:
                placements.append(d.placement)
        return [('yet','예정인 상품'),('start','진행중인 상품'),('done','종료된 상품')]+[(p.id, p.title) for p in placements]

    def queryset(self, request, queryset):
        if self.value() == 'yet':
            return queryset.filter(donation__placement__placement_start__gte=datetime.now())        
        elif self.value() == 'start':
            return queryset.filter(donation__placement__placement_start__lte=datetime.now(), donation__placement__placement_end__gte=datetime.now())
        elif self.value() == 'done':
            return queryset.filter(donation__placement__placement_end__lte=datetime.now())
        elif self.value():
            return queryset.filter(donation__placement__id__exact=self.value())

@admin.register(CrowdFundingOrderItem)
class CrowdFundingOrderItemAdmin(BaseOrderItemAdmin):
    # def not_expired(self, post):
    #     if post.expired:
    #         return mark_safe(f"<span style='color:#d49d9d;' class='icon-cross'></span>")
    #     else:
    #         return mark_safe(f"<span style='color:#82b982;' class='icon-tick'></span>")
    # not_expired.short_description='유효'
    # def not_expired(self, post):
    #     if post.expired:
    #         return mark_safe(f"<span style='color:#d49d9d;' class='icon-cross'></span>")
    #     else:
    #         return mark_safe(f"<span style='color:#82b982;' class='icon-tick'></span>")
    # not_expired.short_description='유효'
    # list_display = [
    #                 'id',        
    #                 'user',
    #                 'quantity',
    #                 'price',
    #                 'deliver_detail',
    #                 'not_expired',
    #                 'donation',
    #                 ]
    # list_display_links = [
    #                 'id',
    #                 'user',
    #                 'quantity',
    #                 'not_expired',
    #                 'donation',                    
    # ]
    # list_filter = [
    #                 'id',        
    #                 'user',
    #                 'quantity',
    #                 'price',
    #                 'deliver_detail',
    #                 'expired',
    #                 'refund_requested',
    #                 'refund_granted',
    #                ]
    # search_fields = [
    #                 'id',
    #                 'user__username',
    #                 'quantity',                    
    #                 'price',
    #                 'expired',
    #                 'deliver_detail',
    #                 'refund_account',
    #                 'donation__id',                    
    # ]
    # ordering = ['expired','-updated']
    # actions=[
    #     survey_push,grant_withdraw,
    #     refund_complete,
    #     ticket_send,
    #     crowd_make3_checkmake4,
    # ]
    def get_list_display(self, request):
        _list_display=copy.deepcopy(super().get_list_display(request))
        _list_display.append('donation')
        return _list_display
    def get_list_filter(self, request):
        _list_filter=copy.deepcopy(super().get_list_filter(request))
        _list_filter.append(PlacementFilter)
        return _list_filter
    def get_search_fields(self, request):
        _search_fields=copy.deepcopy(super().get_search_fields(request))
        _search_fields.append('donation__id')
        return _search_fields
    def get_actions(self,request):
        _actions=copy.deepcopy(super().get_actions(request))
        _actions['crowd_make3_checkmake4']=(crowd_make3_checkmake4, 'crowd_make3_checkmake4', crowd_make3_checkmake4.short_description)
        _actions.move_to_end('crowd_make3_checkmake4', last=False)
        return _actions

    # def get_field_queryset(self, db, db_field, request):
    #     queryset = super().get_field_queryset(db, db_field, request)
    #     if db_field.name == 'order':
    #         if queryset is not None:
    #             queryset = queryset.order_by('user')
    #     return queryset

@admin.register(OpenFundingOrderItem)
class OpenFundingOrderItemAdmin(BaseOrderItemAdmin):
    def get_list_display(self, request):
        _list_display=copy.deepcopy(super().get_list_display(request))
        _list_display.append('placementbid')
        return _list_display
    # def get_list_filter(self, request):
    #     _list_filter=copy.deepcopy(super().get_list_filter(request))
    #     _list_filter.append('placementbid')
    #     return _list_filter
    def get_search_fields(self, request):
        _search_fields=copy.deepcopy(super().get_search_fields(request))
        _search_fields.append('placementbid__id')
        return _search_fields
    def get_actions(self,request):
        _actions=copy.deepcopy(super().get_actions(request))
        new_actions={
            'secret_open_make2':(secret_open_make2, 'secret_open_make2', secret_open_make2.short_description),
            'secret_open_make3':(secret_open_make3, 'secret_open_make3', secret_open_make3.short_description),
            'secret_open_make4':(secret_open_make4, 'secret_open_make4', secret_open_make4.short_description),            
        }
        _actions.update(new_actions)
        _actions.move_to_end('secret_open_make4', last=False)
        _actions.move_to_end('secret_open_make3', last=False)
        _actions.move_to_end('secret_open_make2', last=False)
        return _actions

@admin.register(SecretFundingOrderItem)
class SecretFundingOrderItemAdmin(BaseOrderItemAdmin):
    def get_list_display(self, request):
        _list_display=copy.deepcopy(super().get_list_display(request))
        _list_display.append('placementbid')
        return _list_display
    # def get_list_filter(self, request):
    #     _list_filter=copy.deepcopy(super().get_list_filter(request))
    #     _list_filter.append('placementbid')
    #     return _list_filter
    def get_search_fields(self, request):
        _search_fields=copy.deepcopy(super().get_search_fields(request))
        _search_fields.append('placementbid__id')
        return _search_fields
    def get_actions(self,request):
        _actions=copy.deepcopy(super().get_actions(request))
        new_actions={
            'secret_open_make2':(secret_open_make2, 'secret_open_make2', secret_open_make2.short_description),
            'secret_open_make3':(secret_open_make3, 'secret_open_make3', secret_open_make3.short_description),
            'secret_open_make4':(secret_open_make4, 'secret_open_make4', secret_open_make4.short_description),            
        }
        _actions.update(new_actions)
        _actions.move_to_end('secret_open_make4', last=False)
        _actions.move_to_end('secret_open_make3', last=False)
        _actions.move_to_end('secret_open_make2', last=False)
        return _actions

@admin.register(Kakao_Result)
class KakaoResultAdmin(admin.ModelAdmin):
    def BizTalkStatus(self, post):
        if post.status == 1000:
            s='성공'
        else:
            s='실패'
        return mark_safe(f"<u>{s}</u>")
    BizTalkStatus.short_description = '진행상황'    
    list_display = [
        'status',
        'BizTalkStatus'
                    ]
    list_display_links = [
        'status',
        'BizTalkStatus'
    ]
    list_filter = [
        'status',
                   ]
    search_fields = [
        'status',
        'BizTalkStatus'
    ]
@admin.register(Article_Comments)
class ArticleCommentAdmin(admin.ModelAdmin):
    list_display = [
                    'id',        
                    'article',
                    'user',
                    'text',
                    'parent_article_comment',
                    ]
    list_display_links = [
                    'id',        
                    'article',
                    'user',
                    'text',
                    'parent_article_comment',
    ]
    list_filter = [
                    'id',        
                    'article',
                    'user',
                    'text',
                    'parent_article_comment',
                   ]
    search_fields = [
                    'id',        
                   'article__title',
                    'user__username',
                    'text',
                    'parent_article_comment__id',
    ]

@admin.register(Articles)
class ArticleAdmin(admin.ModelAdmin):
    def toggle_soldout(modeladmin, request, queryset):
        for article in queryset:
            article.is_soldout=not article.is_soldout
            article.save()
    toggle_soldout.short_description="판매중<->판매완료"

    list_display = [
        'id',
        'title',
        'user',
        'is_soldout',
        'category',
        'n_hit',
        'display_day',
    ]
    list_display_links = [
        'id',
        'title',
        'user',
        'category',
        'n_hit',
        'display_day',
    ]
    list_filter = [
        'id',
        'title',        
        'user',
        'category',
        'display_day',
    ]
    search_fields = [
        'id',
        'title',
        'user__username',
        'category',
    ]
    actions=[toggle_soldout]
    ordering=['-display_day']

@admin.register(Posts)
class PostAdmin(admin.ModelAdmin):
    list_display = [
                    'id',
                    'user',
                    'text',
                    ]
    list_display_links = [
    'id',        
      'user',
      'text',
    ]
    list_filter = [
        'id',
        'user',
                   ]
    search_fields = [
        'id',        
        'user',
        'text',
    ]


@admin.register(Comments)
class CommentAdmin(admin.ModelAdmin):
    list_display = [
                    'id',
                    'post',
                    'user',
                    'text',
                    'parent_comment',
                    ]

    list_display_links = [
        'id',
        'post',
        'user',
        'text',
        'parent_comment',
    ]
    list_filter = [
        'id',
        'post',
        'user',
        'text',
        'parent_comment',
                   ]
    search_fields = [
        'id',
        'post',
        'user',
        'text',
        'parent_comment',
    ]

# def make_refund_accepted(modeladmin, request, queryset):
#     queryset.update(refund_requested=False, refund_granted=True)
# make_refund_accepted.short_description = 'Update orders to refund granted'

