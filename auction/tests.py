from django.shortcuts import get_object_or_404
from django.test import TestCase
from core.tasks import Phone_SMS_Send
from django.db.models.signals import post_save
from user.models import Users, Verification
from .models import AutoBid, Placement, PlacementBid

import datetime, random
# Create your tests here.
def vf_unit_price(offer):
    if offer < 1000000:
        unit_price = 50000
    elif 1000000 <= offer and offer < 3000000:
        unit_price = 100000
    elif 3000000 <= offer and offer < 5000000:
        unit_price = 200000
    elif 5000000 <= offer and offer < 10000000:
        unit_price = 300000
    elif 10000000 <= offer and offer < 30000000:
        unit_price = 500000
    elif 30000000 <= offer and offer < 50000000:
        unit_price = 1000000
    elif 50000000 <= offer and offer < 100000000:
        unit_price = 2000000
    elif 100000000 <= offer and offer < 200000000:
        unit_price = 3000000
    elif 200000000 <= offer:
        unit_price = 5000000  
    return unit_price
def placement_detail(method, pk, user_id, bid, money):
    user=Users.objects.get(id=user_id)
    my_autobid = AutoBid.objects.filter(user=user, placement=pk).first()
    placement = get_object_or_404(Placement, pk=pk)
    pbd=PlacementBid.objects.filter(user=user, placement=pk)
    all_pbd=PlacementBid.objects.filter(placement=pk).order_by('-offer','-id')
    max_autobid = AutoBid.objects.filter(placement=pk)
    p_name='TEST 아티스트'
    #현최고자동응찰금액 산정
    if len(max_autobid) != 0:
        max_autobid = max_autobid.order_by('-limit')[0]

    #자동응찰, 1회응찰
    if method == 'POST':

        # 바로구매
        if 'buynow-bid' == bid and placement.placement_buynow_price != 0:
            try:
                buynow_pbd, created = PlacementBid.objects.get_or_create(
                    user=user,
                    placement=placement,
                    offer=placement.placement_buynow_price,
                )
                placement.placement_end=datetime.datetime.now()
                placement.placement_win=buynow_pbd
                placement.placement_price=placement.placement_buynow_price
                placement.save()
                print("바로구매가 완료되어 옥션이 종료되었습니다. 낙찰정보는 '낙찰 확인하기' 페이지에서 확인 가능합니다. 감사합니다")
                return

            except:
                if created:
                    print('바로구매는 등록되었으나 오류가 발생했습니다')
                    return
                else:
                    print('바로구매중 오류가 발생했습니다.')
                    return

            
        # 자동응찰
        elif 'auto-bid' == bid:
            submitted_limit = money
            # if submitted_limit % placement.unit_price != 0: #호가단위 검사
            #     tmp = format(placement.unit_price, ',')
            #     messages.info(request,f'호가 단위에 맞는 금액을 넣어주십시오. 호가 단위는 {tmp}원 입니다')
            #     return redirect('auction:placement-detail', placement.pk)
            if submitted_limit >= placement.placement_price+placement.unit_price:
                #update or create autobid                                                        
                try:
                    autobidObject, created = AutoBid.objects.update_or_create(
                    user=user,
                    placement=placement,
                    defaults={"limit": submitted_limit}
                    )
                    #당장 비교할값은 다음 step 가격이기 때문에
                    offer=placement.placement_price + placement.unit_price

                    #문자보내기
                    n = format(submitted_limit, ',')
                    if created:
                        content=f'[원앤온리] {user.username}님\n[자동응찰 등록]\n[{p_name}]님 경매품\n자동응찰가 {n}원'
                        #응찰시각 {datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")}
                    else:
                        content=f'[원앤온리] {user.username}님\n[자동응찰가 변경]\n[{p_name}]님 경매품\n자동응찰가 {n}원'
                    try:
                        phone=user.verification.standardize_phone
                        # Phone_SMS_Send.apply_async( args=[phone, content], ignore_result=False)
                        print('문자보내기', phone, content, '\n')
                    except:
                        print('메시지 발송실패')
                except:
                    print('자동응찰에러')
                    return
            else:
                print('상대방 응찰로 현재가가 변경되었습니다. 더 높은 금액으로 시도해주십시오')
                return
        # 1회응찰
        elif 'one-bid' == bid:
            submitted_amount = money
            # if submitted_amount % placement.unit_price != 0: #호가단위 검사
            #     tmp = format(placement.unit_price, ',')
            #     messages.info(request,f'호가 단위에 맞는 금액을 넣어주십시오. 호가 단위는 {tmp}원 입니다')
            #     return redirect('auction:placement-detail', placement.pk)            
            if submitted_amount >= placement.placement_price+placement.unit_price:                        
                placement_bid, created = PlacementBid.objects.get_or_create(user=user, 
                                                                    placement=placement, 
                                                                    offer=submitted_amount)
                offer = submitted_amount + placement.unit_price
                if created:
                    #문자보내기
                    n = format(submitted_amount, ',')
                    content=f'[원앤온리] {user.username}님\n[1회 응찰]\n[{p_name}]님 경매품\n1회 응찰가 {n}원'
                    try:
                        phone=user.verification.standardize_phone
                        # Phone_SMS_Send.apply_async( args=[phone, content], ignore_result=False)
                        print('문자보내기', phone, content, '\n')
                    except:
                        # messages.info(request,'알림메시지 발송에 실패하였습니다')
                        pass
            else:
                print('더 높은 금액으로 시도해주십시오')
                return
        else:
                print('잘못된 요청입니다')
                return
        # 자동응찰기 동작 offer=당장 비교할값, placement_bid=첫째 응찰객체
        autobids = AutoBid.objects.filter(placement=placement, limit__gte=offer)
        placement_bid = all_pbd.first()
        bulk_create_list=[]
        again=True
        while again == True:
            again=False
            for a in autobids:
                if placement_bid is not None:
                  vf_u = vf_unit_price(placement_bid.offer)
                  if placement.unit_price != vf_u:
                    placement.unit_price = vf_u
                    placement.save()
                  print(f'unit_price:{placement.unit_price}, placement_bid:{placement_bid}')
                print(f'a.limit:{a.limit}, offer:{offer}')
                if a.limit >= offer:
                    if placement_bid is None: #init(자동응찰)
                        placement_bid=PlacementBid(user=a.user, 
                                    placement=placement,
                                    offer=placement.placement_price,
                                    is_autobid = True,
                                    )
                        bulk_create_list.append(placement_bid)
                        offer+=placement.unit_price
                        print("init append", placement_bid, "init", bulk_create_list)                                        
                    elif placement_bid.user != a.user: #스스로가 아닐때
                        if placement_bid.is_autobid: #자동응찰에 대항
                            if a.limit >= offer and a.limit > placement_bid.offer:
                                placement_bid = PlacementBid(user=a.user, 
                                        placement=placement,
                                        offer=offer,
                                        is_autobid = True,
                                        )
                                bulk_create_list.append(placement_bid)
                                offer+=placement.unit_price
                                print("against autobid append", placement_bid, "is_autobid", bulk_create_list)                                        
                        else: #1회 응찰에 대항
                            print(a.limit, offer)
                            if a.limit == placement_bid.offer and placement_bid.placementbid_created > a.created : #Superior
                                print("superior")
                                placement_bid = PlacementBid(user=a.user, 
                                        placement=placement,
                                        offer=offer,
                                        is_autobid = True,
                                        is_superior = True,
                                        )
                                bulk_create_list.append(placement_bid)                                
                                offer+=placement.unit_price
                                print("append", placement_bid, "1회 응찰 대항", bulk_create_list)                                                                        
                            elif a.limit > placement_bid.offer:
                                placement_bid = PlacementBid(user=a.user, 
                                        placement=placement,
                                        offer=offer,
                                        is_autobid = True,
                                        )
                                bulk_create_list.append(placement_bid)
                                offer+=placement.unit_price
                                print("append", placement_bid, "1회 응찰 대항, 더 클때", bulk_create_list)
            tmp=offer #offer변화감지
            if len(autobids) != 1:
                for a in autobids:

                    #AUTOBID 우선순위 선별과정
                    # print(a.limit, placement_bid.offer, a.user, placement_bid.user)
                    # print("선별과정", a, placement_bid)
                    # print("한번보자", a.limit, placement_bid.offer, a.user, placement_bid.user)
                    if a.user != placement_bid.user:
                        try: 
                            #자동응찰 vs 자동응찰
                            if placement_bid.is_autobid == True:
                                # print(AutoBid.objects.get(user=placement_bid.user).created, a.created, (AutoBid.objects.get(user=placement_bid.user).created > a.created))
                                atb=AutoBid.objects.get(placement=placement, user=placement_bid.user)
                                # print("here!", atb, a.limit, atb.limit)
                                if atb.created > a.created and a.limit >= atb.limit and atb.limit == placement_bid.offer:
                                    placement_bid = PlacementBid(user=a.user, 
                                                                placement=placement,
                                                                offer=placement_bid.offer,
                                                                is_autobid = True,
                                                                is_superior = True,
                                                                )
                                    bulk_create_list.append(placement_bid)
                                    again=True

                                    print("자동응찰 vs 자동응찰 우선선별", placement_bid)
                                # elif placement_bid.created > a.created:
                                #     placement_bid.user=a.user
                                #     placement_bid.save()
                                #     print("자동응찰 vs 1회응찰 우선선별", placement_bid)
                            else: #1회응찰 vs 자동응찰
                                if a.limit >= placement_bid.offer and placement_bid.created > a.created:
                                    placement_bid = PlacementBid(user=a.user, 
                                                                 placement=placement,
                                                                offer=placement_bid.offer,
                                                                is_autobid = True,
                                                                is_superior = True,
                                                                )
                                    bulk_create_list.append(placement_bid)
                                    again=True
                                    print("1회 응찰 vs 자동응찰 우선선별", placement_bid)
                        except:
                            pass
                for a in autobids:
                  if a.user != placement_bid.user and a.limit >= offer:
                    print("다시! 1")
                    again=True

        #bulk_create & phone_send
        if bulk_create_list:
            print(bulk_create_list)
            if len(bulk_create_list) > 1:
                placement_bids_queryset=PlacementBid.objects.bulk_create(bulk_create_list)
                bulk_create_list.sort(key=lambda x: x.offer, reverse=True)
                instance = bulk_create_list[0]
                post_save.send(PlacementBid, instance=instance, created=True)
            elif len(bulk_create_list) == 1:
                u_pbd=bulk_create_list[0]
                u_pbd.save()

            #유저별로
            user_list=[]
            for p in bulk_create_list:
                if p.user not in user_list:
                    user_list.append(p.user)
            for u in user_list:
                u_pbd = [pbds for pbds in bulk_create_list if pbds.user == u]
                u_pbd.sort(key=lambda x: x.offer, reverse=True)
                #문자보내기
                p = format(u_pbd[0].offer, ',')
                c = len(u_pbd)
                content=f'\n[원앤온리] {u.username}님\n[자동응찰] {c}회\n[{p_name}]님 경매품\n최종 자동응찰가 {p}원'                
                phone=u.verification.standardize_phone
                # Phone_SMS_Send.apply_async( args=[phone, content], ignore_result=False)
                print('문자보내기', phone, content, '\n')
                    # messages.info(request,'알림메시지 발송에 실패하였습니다')            
        return

    else:
      #POST 이외요청
        return


class AuctionBiddingTest(TestCase):
    @classmethod
    def setUpTestData(cls):
      Placement.objects.create(
        title = '테스트',
        description = '설명',
        placement_price=100000,
        unit_price=50000,
        placement_buynow_price = 1000000,
        )

      user1 = Users.objects.create_user('test1', 'eaa0305@naver.com', 'rkskekfk1')
      Verification.objects.create(user=user1, phone='01025806413', phone_verified=True)
      user2 = Users.objects.create_user('test2', 'eaa0103@gmail.com', 'rkskekfk1')
      Verification.objects.create(user=user2, phone='01025806413', phone_verified=True)
      user3 = Users.objects.create_user('test3', 'annalee98@naver.com', 'rkskekfk1')
      Verification.objects.create(user=user3, phone='01025806413', phone_verified=True)

    def setUp(self):
      p=Placement.objects.get(id=1)
      p.placement_price=100000
      p.unit_price=50000
      p.save()

    #1회응찰만
    def test_only_one_bid(self):
      for user in Users.objects.all():
        p=Placement.objects.get(id=1)
        #'one-bid', 'auto-bid', 'buynow-bid'
        placement_detail('POST', 1, user.id, 'one-bid', p.placement_price+(random.choice([1,2,3,4,5]))*p.unit_price)
      print('1회 응찰객체결과')
      for pbd in PlacementBid.objects.all().order_by('-placementbid_created'):
        print(pbd, pbd.placementbid_created, pbd.is_superior)

    #자동응찰만
    def test_only_auto_bid(self):
      li=[[1,2,3,4,5],[6,7,8,9,10],[11,12,13,14,15]]
      for i in range(3):
        for user in Users.objects.all():
          p=Placement.objects.get(id=1)
          #'one-bid', 'auto-bid', 'buynow-bid'
          placement_detail('POST', 1, user.id, 'auto-bid', p.placement_price+(random.choice(li[i]))*p.unit_price)
        print('\n자동응찰기')
        for a in AutoBid.objects.all():
          print(a, a.limit)

        print('\n자동 응찰객체결과')
        for pbd in PlacementBid.objects.all().order_by('-placementbid_created'):
          print(pbd, pbd.placementbid_created, pbd.is_superior)

    #1회응찰, 자동응찰
    def test_mix_one_auto_bid(self):
      for _ in range(3):
        self.test_only_auto_bid()
        self.test_only_one_bid()

    #1회응찰, 자동응찰, 바로구매 무작위
    def test_random(self):
      pass
