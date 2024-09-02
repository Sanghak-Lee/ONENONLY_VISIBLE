# from celery import shared_task
# from .models import Placement, PlacementBid
# from core.tasks import Phone_SMS_Send

# @shared_task
# def Auction_Finish_SMS(**kwargs):
#   pre_content=kwargs['content']
#   pk=kwargs['pk']
#   p=Placement.objects.get(pk=pk)
#   pbd=PlacementBid.objects.filter(placement__id=p.id)
#   pbd_first=pbd.first()
  
#   users=[]
#   for pb in p.placementbid_set.all():
#     if not pb.user in users:
#       users.append(pb.user)
  
#   for u in users:
#     phone=u.verification.standardize_phone()
#     content=pre_content.format(placement=p.placement_artist, user=u.username, winner=pbd_first.user, winner_price=format(pbd_first.offer, ','))
#     Phone_SMS_Send.apply_async( args=[phone, content], ignore_result=True)
  

# @shared_task
# def auction_Alarm_Kakao(**kwargs):
#   #Periodic Task 만들기
#   pass