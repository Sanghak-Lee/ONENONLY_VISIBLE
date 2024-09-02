from datetime import timedelta, datetime
from django.utils.safestring import mark_safe
from django.contrib import admin
from auction.forms import PlacementSelectForm
from core.models import OpenFundingOrderItem, SecretFundingOrderItem, CrowdFundingOrderItem
from django.contrib import messages
from core.tasks import AdminPhone_SMS_Send, Auction_Alarm_Push, Auction_Before_Finish_Push, Auction_Encore_Push, Auction_Finish_Push, Before_Make_OrderItem_Expired, Biz_KAKAO_Send, Make_OrderItem_Expired
from core.utils import SeoulToUTC, ToUTC
from .models import Donation, Oney, Placement, PlacementBid, AuctionArtist, AutoBid, AuctionAuthorization, AuctionNftToken, PlacementMemory, TimeStoreItem
from django_celery_beat.models import PeriodicTask, ClockedSchedule
import json
def When_Placement_Created_Push(modeladmin, request, queryset):
    for p in queryset:
        Auction_Alarm_Push.apply_async(kwargs={'pk':p.id}, eta=SeoulToUTC(p.placement_start), expires=SeoulToUTC(p.placement_end))
        # clocked, _ = ClockedSchedule.objects.get_or_create(
        #     clocked_time=ToUTC(p.placement_start)
        # )        
        # PeriodicTask.objects.create(
        #     clocked=clocked,
        #     expires=ToUTC(p.placement_end),
        #     name=f"{p.title[:6]}-Auction_Alarm_Push-{datetime.now()}",
        #     task="core.tasks.Auction_Alarm_Push",
        #     one_off=True,
        #     kwargs=json.dumps({
        #         'pk':p.id,
        #     }),
        # )

        # Auction_Before_Finish_Push.apply_async(kwargs={'pk':p.id}, eta=SeoulToUTC(p.placement_end)-timedelta(hours=1), expires=SeoulToUTC(p.placement_end))
        clocked, _ = ClockedSchedule.objects.get_or_create(
            clocked_time=ToUTC(p.placement_end)-timedelta(hours=1)
        )
        PeriodicTask.objects.create(
            clocked=clocked,
            expires=ToUTC(p.placement_end),
            name=f"{p.title[:6]}-Auction_Before_Finish_Push-{datetime.now()}",
            task="core.tasks.Auction_Before_Finish_Push",
            one_off=True,
            kwargs=json.dumps({
                'pk':p.id,
            }),
        )

        # Auction_Finish_Push.apply_async(kwargs={'pk':p.id}, eta=SeoulToUTC(p.placement_end), expires=SeoulToUTC(p.placement_end)+timedelta(hours=1))
        clocked, _ = ClockedSchedule.objects.get_or_create(
            clocked_time=ToUTC(p.placement_end)
        )
        PeriodicTask.objects.create(
            clocked=clocked,
            expires=ToUTC(p.placement_end)+timedelta(hours=1),
            name=f"{p.title[:6]}-Auction_Finish_Push-{datetime.now()}",
            task="core.tasks.Auction_Finish_Push",
            one_off=True,
            kwargs=json.dumps({
                'pk':p.id,
            }),
        )        
    return

def When_Placement_Created_Encore(modeladmin, request, queryset):
    original_p_id = request.POST.get('placement', None)
    if original_p_id:
        for p in queryset:
            # Auction_Encore_Push.run(original_pk=original_p_id, pk=p.id)
            Auction_Encore_Push.apply_async(kwargs={'original_pk':original_p_id, 'pk':p.id}, expires=SeoulToUTC(p.placement_end))
            # clocked, _ = ClockedSchedule.objects.get_or_create(
            #     clocked_time=ToUTC(p.placement_start)
            # )
            # PeriodicTask.objects.create(
            #     clocked=clocked,
            #     expires=ToUTC(p.placement_end),
            #     name=f"{p.title[:6]}-Auction_Encore_Push-{datetime.now()}",
            #     task="core.tasks.Auction_Encore_Push",
            #     one_off=True,
            #     kwargs=json.dumps({
            #         'original_pk':original_p_id,
            #         'pk':p.id,
            #     }),
            # )

    return

def ticket_send(modeladmin, request, queryset):
    for placement in queryset:
        #티켓 메시지 전송
        phones_params=[]
        tmp=[]
        users=[]
        ois=[]
        if placement.placement_type =='crowdfunding':
            for donation in placement.placement_win_crowdfunding.all():
                user=donation.user
                u_oi=donation.crowdfundingorderitem
                try:
                    if user.verification.standardize_phone() and (u_oi is not None):
                        ois.append(u_oi)
                        # if user not in users:
                        users.append(user)
                except:
                    continue
        else:
            win_pbd=placement.placement_win
            user=win_pbd.user
            if placement.placement_type=='secretfunding':
                u_oi=win_pbd.secretfundingorderitem
            else:
                u_oi=win_pbd.openfundingorderitem
            try:
                if user.verification.standardize_phone() and (u_oi is not None):
                    ois.append(u_oi)
                    if user not in users:
                        users.append(user)
            except:
                continue
        for o in ois:
            phone=o.user.verification.standardize_phone()
            params={
                'USERNAME':o.user.username,
                'TITLE':placement.title,
                'PLACE':placement.d_place,
                'TIME':placement.d_day.strftime("%Y. %m. %d. %H시"),
                'BUTTON':{
                    0:{
                        'SLUG':placement.placement_type,
                        'OID':o.id                        
                    }
                }
            }
            phones_params.append({phone:params})
        tmpltCode='v2_bid_ticket'
        
        # Biz_KAKAO_Send.run(phones_params=phones_params, tmpltCode=tmpltCode)
        Biz_KAKAO_Send.apply_async(kwargs={'phones_params':phones_params, 'tmpltCode':tmpltCode}, ignore_result=False)
        AdminPhone_SMS_Send.apply_async(args=[f"초대장전송\n옥션:{placement.title[:5]}...\n전송주문서:{len(ois)}개\n유저수:{len(users)}명"], ignore_result=False)



def f_secret_open_make1(request, pbd):
    #오픈펀딩(Depreciated)
    if pbd.placement.placement_type == 'openfunding':
        try : 
            I_orderitem, created = OpenFundingOrderItem.objects.update_or_create(
                user=pbd.user,
                placement = pbd.placement,
                placementbid=pbd,
                price=pbd.offer,
                expired=False,
                deliver_detail=1,
                due_date=datetime.now()+timedelta(hours=3),
            )
            #Winner
            pbd.placement.placement_win=pbd
            pbd.placement.placement_price=pbd.offer
            pbd.placement.save()

            #카카오메시지 전송 open_bid_1_y
            #관리자문자
            phones_params=[]
            phone=pbd.user.verification.standardize_phone()
            params={
                'USERNAME':pbd.user.username,
                'TITLE':pbd.placement.title,
                'PRICE':I_orderitem.get_final_price(),
                'PRICE_CALC':I_orderitem.get_final_price()*0.3,
            }
            phones_params.append({phone:params})
            tmpltCode='open_bid_1_y'
            Biz_KAKAO_Send.apply_async(kwargs={'phones_params':phones_params, 'tmpltCode':tmpltCode}, ignore_result=False)
            AdminPhone_SMS_Send.apply_async(args=[f"오픈낙찰확정\n유저:{pbd.user.username}\n상품:{pbd.placement.title[:5]+'...'}\n주문번호:{I_orderitem.id}"], ignore_result=False)

            #Expire 2개
            Before_Make_OrderItem_Expired.apply_async(kwargs={'pk':I_orderitem.id, 'slug':I_orderitem.placement.placement_type}, eta=SeoulToUTC(datetime.now())+timedelta(hours=23), expires=SeoulToUTC(datetime.now())+timedelta(days=1, hours=6))
            # clocked, _ = ClockedSchedule.objects.get_or_create(
            #     clocked_time=ToUTC(datetime.now())+timedelta(hours=23)
            # )
            # PeriodicTask.objects.create(
            #     clocked=clocked,
            #     expires=ToUTC(datetime.now()+timedelta(days=1, hours=6)),
            #     name=f"{I_orderitem.placement.title[:6]}-{I_orderitem.id}-Before_Make_OrderItem_Expired-{datetime.now()}",
            #     task="core.tasks.Before_Make_OrderItem_Expired",
            #     one_off=True,
            #     kwargs=json.dumps({
            #         'pk':I_orderitem.id,
            #         'slug':I_orderitem.placement.placement_type,
            #     }),
            # )

            Make_OrderItem_Expired.apply_async(kwargs={'pk':I_orderitem.id, 'slug':I_orderitem.placement.placement_type}, eta=SeoulToUTC(datetime.now())+timedelta(hours=24), expires=SeoulToUTC(datetime.now())+timedelta(days=1, hours=6))
            # clocked, _ = ClockedSchedule.objects.get_or_create(
            #     clocked_time=ToUTC(datetime.now())+timedelta(hours=24)
            # )
            # PeriodicTask.objects.create(
            #     clocked=clocked,
            #     expires=ToUTC(datetime.now()+timedelta(days=1, hours=6)),
            #     name=f"{I_orderitem.placement.title[:6]}-{I_orderitem.id}-Make_OrderItem_Expired-{datetime.now()}",
            #     task="core.tasks.Make_OrderItem_Expired",
            #     one_off=True,
            #     kwargs=json.dumps({
            #         'pk':I_orderitem.id,
            #         'slug':I_orderitem.placement.placement_type,
            #     }),
            # )


            tmpltCode='open_bid_1_n'
        except:
            messages.error(request, "[옥션경매] orderitem 생성 & order 생성 Error occurred")
    #시크릿펀딩
    elif pbd.placement.placement_type == 'secretfunding':
        try : 
            I_orderitem, created = SecretFundingOrderItem.objects.update_or_create(
                user=pbd.user,
                placement = pbd.placement,
                placementbid=pbd,
                defaults={
                    'price':pbd.offer,
                    'expired':False,
                    'deliver_detail':1,
                    'due_date':datetime.now()+timedelta(hours=3),
                }
            )

            #Winner
            pbd.placement.placement_win=pbd
            pbd.placement.save()

            #카카오메시지 전송 v2_secret_bid_1_y
            #관리자문자
            phones_params=[]
            phone=pbd.user.verification.standardize_phone()
            params={
                'USERNAME':pbd.user.username,
                'TITLE':pbd.placement.title,
                'PRICE':I_orderitem.get_final_price(),
                'DEPOSIT':I_orderitem.placement.deposit,
            }
            phones_params.append({phone:params})
            tmpltCode='v2_secret_bid_1_y'
            Biz_KAKAO_Send.apply_async(kwargs={'phones_params':phones_params, 'tmpltCode':tmpltCode}, ignore_result=False)
            AdminPhone_SMS_Send.apply_async(args=[f"시크릿낙찰확정\n유저:{pbd.user.username}\n상품:{pbd.placement.title[:5]+'...'}\n주문번호:{I_orderitem.id}"], ignore_result=False)

            #Expire 2개
            Before_Make_OrderItem_Expired.apply_async(kwargs={'pk':I_orderitem.id, 'slug':I_orderitem.placement.placement_type}, eta=SeoulToUTC(datetime.now())+timedelta(hours=2), expires=SeoulToUTC(datetime.now())+timedelta(days=1))
            # clocked, _ = ClockedSchedule.objects.get_or_create(
            #     clocked_time=ToUTC(datetime.now())+timedelta(hours=23)
            # )
            # PeriodicTask.objects.create(
            #     clocked=clocked,
            #     expires=ToUTC(datetime.now()+timedelta(days=1, hours=6)),
            #     name=f"{I_orderitem.placement.title[:6]}-{I_orderitem.id}-Before_Make_OrderItem_Expired-{datetime.now()}",
            #     task="core.tasks.Before_Make_OrderItem_Expired",
            #     one_off=True,
            #     kwargs=json.dumps({
            #         'pk':I_orderitem.id,
            #         'slug':I_orderitem.placement.placement_type,
            #     }),
            # )
            Make_OrderItem_Expired.apply_async(kwargs={'pk':I_orderitem.id, 'slug':I_orderitem.placement.placement_type}, eta=SeoulToUTC(datetime.now())+timedelta(hours=3), expires=SeoulToUTC(datetime.now())+timedelta(days=1))
            # clocked, _ = ClockedSchedule.objects.get_or_create(
            #     clocked_time=ToUTC(datetime.now())+timedelta(hours=24)
            # )
            # PeriodicTask.objects.create(
            #     clocked=clocked,
            #     expires=ToUTC(datetime.now()+timedelta(days=1, hours=6)),
            #     name=f"{I_orderitem.placement.title[:6]}-{I_orderitem.id}-Make_OrderItem_Expired-{datetime.now()}",
            #     task="core.tasks.Make_OrderItem_Expired",
            #     one_off=True,
            #     kwargs=json.dumps({
            #         'pk':I_orderitem.id,
            #         'slug':I_orderitem.placement.placement_type,
            #     }),
            # )
        except:
            messages.error(request, "[옥션경매] orderitem 생성 & order 생성 Error occurred")

def secret_open_make1(modeladmin, request, queryset):
    for pbd in queryset:
        f_secret_open_make1(request, pbd)
#크라우드펀딩 win_crowdfunding 채우기
def crowd_wincrowdfunding(modeladmin, request, queryset):
    for p in queryset:
        if p.placement_type == 'crowdfunding':        
            #checkmake4
            win_donations=[]
            win_ois=[]
            cnt=0
            for donation in p.donation_set.all():
                try: 
                    if (not donation.crowdfundingorderitem.expired) and donation.crowdfundingorderitem.deliver_detail >=3:
                        cnt+=donation.get_total_price()
                        win_donations.append(donation)
                        win_ois.append(donation.crowdfundingorderitem)
                except:
                    pass
            #win_crowdfunding에 추가
            if len(win_donations)>0 and len(win_ois)>0:
                p.placement_win_crowdfunding.add(*win_donations)
                p.save()

                #make 4
                win_oi_list=CrowdFundingOrderItem.objects.filter(id__in=[oi.id for oi in win_ois])
                win_oi_list.update(deliver_detail=4)

#크라우드펀딩 실패
def crowd_bid_4_n(modeladmin, request, queryset):
    for p in queryset:
        if p.placement_type == 'crowdfunding':        
            #checkmake4
            users=[]
            win_donations=[]
            win_ois=[]
            cnt=0
            for donation in p.donation_set.all():
                user=donation.user
                try:
                    if user.verification.standardize_phone() and (user not in users):
                        users.append(user)
                except:
                    continue
                try: 
                    if (not donation.crowdfundingorderitem.expired) and donation.crowdfundingorderitem.deliver_detail >=3:
                        cnt+=donation.get_total_price()
                        win_donations.append(donation)
                        win_ois.append(donation.crowdfundingorderitem)
                except:
                    pass            
            #크라우드 모금완료
            if cnt >= p.placement_price:
                messages.info(request, '모금에 성공한 상품입니다. 구매성공메시지가 전송됐는지 확인하십시오.')
                pass
                # p.placement_win_crowdfunding.add(*win_donations)
                # p.save()

                # #make 4
                # win_oi_list=CrowdFundingOrderItem.objects.filter(id__in=[oi.id for oi in win_ois])
                # win_oi_list.update(deliver_detail=4)

                # #카카오 메시지(v2_crowd_bid_4_y)
                # #관리자 메시지
                # phones_params=[]
                # for u in [d.user for d in win_donations]:
                #     phone=u.verification.standardize_phone()
                #     params={
                #         'USERNAME':u.username,
                #         'TITLE':p.title,
                #     }
                #     phones_params.append({phone:params})
                # tmpltCode='v2_crowd_bid_4_y'
                # Biz_KAKAO_Send.apply_async(kwargs={'phones_params':phones_params, 'tmpltCode':tmpltCode}, ignore_result=False)
                # AdminPhone_SMS_Send.apply_async(args=[f"모금완료\n옥션:{p.title[:5]}\n낙찰자:{len(win_donations)}명"], ignore_result=False)
            else:
                # 카카오 메시지(crowd_bid_4_n)
                # 관리자 메시지
                phones_params=[]
                win_donations_user=[] 
                for user in [d.user for d in win_donations]:
                    try:
                        if user.verification.standardize_phone() and (user not in win_donations_user):
                            win_donations_user.append(user)
                    except:
                        continue

                for u in win_donations_user:
                    phone=u.verification.standardize_phone()
                    params={
                        'USERNAME':u.username,
                        'TITLE':p.title,
                    }
                    phones_params.append({phone:params})
                tmpltCode='crowd_bid_4_n'
                # Biz_KAKAO_Send.run(phones_params=phones_params, tmpltCode=tmpltCode)
                Biz_KAKAO_Send.apply_async(kwargs={'phones_params':phones_params, 'tmpltCode':tmpltCode}, ignore_result=False)
                AdminPhone_SMS_Send.apply_async(args=[f"모금실패\n옥션:{p.title[:5]}...\n(결제O)낙찰실패자:{len(win_donations_user)}명"], ignore_result=False)

#시크릿,오픈 실패
def secret_open_1_n(modeladmin, request, queryset):
    for placement in queryset:

        #응찰 탈락 알림
        phones_params=[]
        tmp=[]
        users=[]
        for _pbd in placement.placementbid_set.all():
            user=_pbd.user
            try:
                if user.verification.standardize_phone() and (user not in users):
                    users.append(user)
            except:
                continue
        for idx, u in enumerate(users):
            if u == placement.placement_win.user:
                tmp.append(idx)
        if tmp != []:
            for t in tmp:
                users.pop(t)

        for u in users:
            phone=u.verification.standardize_phone()
            params={
                'USERNAME':u.username,
                'TITLE':placement.title,
            }
            phones_params.append({phone:params})
        tmpltCode='v2_secret_bid_1_n'
        Biz_KAKAO_Send.apply_async(kwargs={'phones_params':phones_params, 'tmpltCode':tmpltCode}, ignore_result=False)
        AdminPhone_SMS_Send.apply_async(args=[f"응찰탈락\n옥션:{placement.title[:5]}...\n탈락유저:{len(users)}명"], ignore_result=False)

When_Placement_Created_Push.short_description='옥션상품 생성시(알람&좋아요, 끝나기 1시간 전, 끝났을 때)'
When_Placement_Created_Encore.short_description='옥션상품 생성시 앵콜요청자들에게 알림'
crowd_bid_4_n.short_description='옥션 종료시 실패 메시지 발송'
crowd_wincrowdfunding.short_description='크라우드 펀딩 win 채우기'
secret_open_make1.short_description = '응찰객체 당첨시키기'
secret_open_1_n.short_description = '응찰 탈락문자'
ticket_send.short_description = '티켓 초대장 문자'
@admin.register(Placement)
class PlacementAdmin(admin.ModelAdmin):
    def display_placement_type(self, post):
        if post.placement_type == 'crowdfunding':
            if post.get_ready_cnt == '1':
                return '일반티켓(단독)'
            else:
                return '일반티켓'
        elif post.placement_type == 'secretfunding':
            return '경쟁티켓'
        else:
            return '오픈펀딩(depreciated)'
    display_placement_type.short_description = '종류'    
    def yet_start_done(self, post):
        if post.placement_order == 0:
            s='숨김'
        elif post.placement_start > datetime.now():
            s='예정'
        elif post.placement_start <= datetime.now() and datetime.now() < post.placement_end:
            s='진행중'
        else:
            s='종료'
        return mark_safe(f"<u>{s}</u>")
    yet_start_done.short_description = '진행상황'
    def alarm_encore_like_total(self, post):
        a = len(post.alarms.all())
        e = len(post.encores.all())
        l = len(post.plikes.all())
        return mark_safe(f"{a} | {e} | {l}")
    alarm_encore_like_total.short_description = '알람/앵콜/좋아요'

    def funding_total(self, post):
        if post.placement_type == 'crowdfunding':
            return '없음'
        else:
            return len(post.placementbid_set.all())
    funding_total.short_description = '응찰객체수'

    def crowdfunding_total(self, post):
        if post.placement_type == 'crowdfunding':
            donation=len(post.donation_set.all())
            price=post.get_crowdfunding_total_really()
            num=0
            return mark_safe(f"{donation} | {0 if price==0 else int(price*100/post.placement_price)}% | {num}")
        else:
            return '없음'
    crowdfunding_total.short_description = '응찰객체/실결제률/총 인원'
    def get_field_queryset(self, db, db_field, request):
        queryset = super().get_field_queryset(db, db_field, request)
        id=request.resolver_match.kwargs.get('object_id')
        if db_field.name == 'placement_win':
            if queryset is not None:
                queryset = queryset.filter(placement__id=id).order_by('placement__id','-offer','-id','user__id')
        elif db_field.name == 'placement_win_crowdfunding':
            if queryset is not None:
                queryset = queryset.filter(placement__id=id, crowdfundingorderitem__expired=False).order_by('user__id')
        return queryset

    action_form = PlacementSelectForm
    actions=[
        When_Placement_Created_Push,
        When_Placement_Created_Encore,
        crowd_wincrowdfunding,        
        # crowd_bid_4_n,
        ticket_send,
    ]
    list_display = [
                    'id',
                    'display_placement_type',
                    'title',
                    'placement_artist',
                    'yet_start_done',
                    'alarm_encore_like_total',
                    'funding_total',
                    'crowdfunding_total',
                    'placement_order',
                    'is_encore',
                    'placement_price',
                    'unit_price',
                    ]
    list_display_links = [
                    'id',
                    'display_placement_type',        
                    'title',
                    'placement_artist',
                    'yet_start_done',
                    'placement_order',
                    'is_encore',
                    'placement_price',
                    'unit_price',
    ]
    list_filter = [
                    'id',
                    'title',
                    'placement_artist',
                    'placement_order',                    
                    'is_encore',
                    'placement_price',
                    'unit_price',
                   ]
    search_fields = [
                    'id',   
                    'title',
                    'placement_artist__name',
                    'placement_order',
                    'is_encore',
                    'placement_price',
                    'unit_price',
                    ]
    ordering = ['-placement_start','-placement_end','-placement_order','-id']
    
admin.site.register(PlacementMemory)
admin.site.register(Oney)
admin.site.register(AuctionNftToken)
admin.site.register(TimeStoreItem)
@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = [
                    'id',        
                    'user',
                    'placement',
                    'offer',
                    'quantity'
                    ]
    list_display_links = [
                    'id',        
                    'user',
                    'placement',
                    'offer',
                    'quantity'
    ]
    list_filter = [
                    'id',        
                    'user',
                    'placement',
                    'offer',
                    'quantity'
                   ]
    search_fields = [
                    'id',        
                    'user__username',
                    'placement__title',
                    'offer',
                    'quantity'
    ]
    ordering = ['placement','user']

@admin.register(PlacementBid)
class PlacementBidAdmin(admin.ModelAdmin):
    list_display = [
                    'id',        
                    'user',
                    'placement',
                    'offer',
                    'confirmed',
                    'is_autobid'
                    ]
    list_display_links = [
                    'id',        
                    'user',
                    'placement',
                    'offer',
                    'confirmed',
                    'is_autobid'
    ]
    list_filter = [
                    'id',        
                    'user',
                    'placement',
                    'confirmed',
                    'is_autobid'
                   ]
    search_fields = [
                    'id',        
                    'user__username',
                    'placement__title',
                    'offer',
                    'confirmed',
                    'is_autobid'           
    ]
    ordering = ['placement','-offer']
    actions=[
        secret_open_make1,
        secret_open_1_n,
        ]


admin.site.register(AuctionArtist)
@admin.register(AutoBid)
class AutoBidAdmin(admin.ModelAdmin):
    list_display = [
                    'id',        
                    'user',
                    'limit',
                    'placement',
                    'created',
                    ]
    list_display_links = [
                    'id',        
                    'user',
                    'limit',
                    'placement',
                    'created',
    ]
    list_filter = [
                    'id',        
                    'user',
                    'limit',
                    'placement',
                    'created',
                   ]
    search_fields = [
                    'id',        
                    'user__username',
                    'limit',
                    'placement__title',
    ]
    ordering = ['placement']
@admin.register(AuctionAuthorization)
class AuctionAuthorizationAdmin(admin.ModelAdmin):
    list_display = [
                    'id',        
                    'user',
                    'code',
                    'placement',
                    'is_authorized',
                    ]
    list_display_links = [
                    'id',        
                    'user',
                    'code',
                    'placement',
                    'is_authorized',
    ]
    list_filter = [
                    'id',        
                    'user',
                    'code',
                    'placement',
                    'is_authorized',
                   ]
    search_fields = [
                    'id',        
                    'user__username',
                    'code',
                    'placement__title',
                    'is_authorized',
    ]
    ordering = ['placement', 'is_authorized', 'user']