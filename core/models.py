from distutils.command.upload import upload
from django.db.models.deletion import CASCADE
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.dispatch.dispatcher import receiver
from django.db.models.signals import post_save, post_delete, pre_save
from core.managers import TimeStampedModel
from django.db import models
from django.core.serializers.json import DjangoJSONEncoder
from core.utils import Phone_Number_Standardize
import json

        
#'value(단계)', 'display(보여지는 display)'
DELIVER_CHOICES = (
    (1, '1단계'), #펀딩 중 (계좌이체 전)      #펀딩성공(펀딩 당첨)
    (2, '2단계'),                         #예약금 완납(1차 예약금 완납)
    (3, '3단계'), #펀딩성공 (계좌이체 완료)     #잔금 완납(2차 잔금 완납)
    (4, '4단계'), #진행 확정 (펀딩상품이 100% 도달 및 장소안내)
)

PG = (
    ('D', '다날'),
    ('T', '토스페이'),
    ('KG', 'KG이니시스'),    
    ('N', '네이버페이'),
    ('KA', '카카오페이'),
    ('ETC', '기타')
)

CATEGORY = (
    ('1', '공지사항'),
    ('2', '이벤트'),
    ('3', '보도자료'),
    ('4', '참고자료'),
    ('5', '특별기획')
)

SERVICE_CATEGORY = (
    ('1', '작사/작곡/편곡'),
    ('2', '회화/공예'),
    ('3', '애니메이션/웹툰'),
    ('4', '경제/학술'),
    ('5', '기타'),
)

def custom_info_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/ElasticInfo/<filename>
    return 'ElasticInfo/{0}'.format(filename)
def custom_orderitem_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/OrderItem/<username>/<filename>
    return 'OrderItem/{0}/{1}'.format(instance.user.username, filename)
def custom_article_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/OrderItem/<username>/<filename>
    return 'Article/{0}/{1}'.format(instance.user.username, filename)

class ElasticInfo(models.Model):
    tag = models.CharField(max_length=20, help_text="식별가능한 문자열", primary_key=True)
    image = models.ImageField(upload_to=custom_info_path, null=True, blank=True)
    video = models.FileField(upload_to=custom_info_path, null=True, blank=True)
    info = models.CharField(max_length=400, null=True, blank=True)

#굿즈ITEM(구 orderitem + item)
class OrderItemModel(TimeStampedModel):
    # order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)

    #주문정보
    ref_code = models.CharField(max_length=50, null=True, blank=True)    
    imp_uid = models.CharField(max_length=50, null=True, blank=True)

    #Vbank
    vbank_num=models.CharField(max_length=50, null=True, blank=True)
    vbank_date=models.DateTimeField(null=True, blank=True)
    vbank_name=models.CharField(max_length=50, null=True, blank=True)

    #COUPON
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)

    #PAYMENT
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)    

    #user주문자, Placement 상품
    user = models.ForeignKey('user.Users', on_delete=models.SET_NULL, null=True, blank=True)
    placement = models.ForeignKey('auction.Placement', on_delete=models.SET_NULL ,null=True, blank=True)

    #interactive with form
    deliver_detail = models.IntegerField(choices=DELIVER_CHOICES, blank=True, default=1)
    price = models.IntegerField(default=100000, blank=True)
    discount_price = models.IntegerField(blank=True, null=True)    
    quantity = models.IntegerField(default=1)

    #REFUND
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)
    refund_account = models.CharField(max_length=100, blank=True, null=True)
    refund_file = models.FileField(upload_to=custom_orderitem_path, null=True, blank=True)

    #EXPIRE
    expired = models.BooleanField(default=False)
    due_date = models.DateTimeField(null=True, blank=True)

    #티켓입장
    ticket_checked=models.BooleanField(default=False)

    class Meta:
        abstract = True
        ordering = ["-updated"]
        
    def __str__(self):
        return f"{self.quantity} * {self.placement} / by:{self.user.username}"

    def qr_src(self):
        BASE_URL="https://chart.googleapis.com/chart?chs=300x300&cht=qr&chl=#(NEXT)"
        next=f"https://onenonly.io/ticket/{self.placement.placement_type}/{self.id}/"
        return BASE_URL.replace('#(NEXT)', next)
    def to_json(self):
        try:
            return json.dumps({
                'id':self.id,
                'price':self.price,
                'amountToBePaid':self.amountToBePaid(),
                'quantity':self.quantity,            
                'placement':{
                    'artist':self.placement.placement_artist.name,
                    'title':self.placement.title,
                    'id':self.placement.id,
                    'type':self.placement.placement_type,
                    'category':self.placement.category,
                    'thumbnail':self.placement.thumbnail.url,
                    'path':self.placement.get_absolute_url(),
                    'd_day':self.placement.d_day.strftime("%Y년 %m월 %d일 %H시 %M분"),
                    'd_place':self.placement.d_place,
                },
                'qr_src':self.qr_src(),
                'user':{
                    'id':self.user.id,
                    'username':self.user.username,
                    'phone':self.user.verification.standardize_phone(),
                    'email':self.user.email,
                    'name':self.user.verification.name,
                },
                'due_date':self.due_date,
            }, cls=DjangoJSONEncoder, ensure_ascii=False)            
        except:        
            return json.dumps({
                'id':self.id,
                'price':self.price,
                'amountToBePaid':self.amountToBePaid(),
                'quantity':self.quantity,            
                'placement':{
                    'artist':self.placement.placement_artist.name,
                    'title':self.placement.title,
                    'id':self.placement.id,
                    'type':self.placement.placement_type,
                    'category':self.placement.category,
                    'thumbnail':self.placement.thumbnail.url,
                    'path':self.placement.get_absolute_url,
                    'd_day':self.placement.d_day.strftime("%Y년 %m월 %d일 %H시 %M분"),
                    'd_place':self.placement.d_place,
                },
                'qr_src':self.qr_src(),
                'user':{
                    'id':self.user.id,
                    'username':self.user.username,
                    'phone':'',
                    'email':self.user.email,
                    'name':'',
                },
                'due_date':self.due_date,
            }, cls=DjangoJSONEncoder, ensure_ascii=False)
    def get_total_item_price(self):
        return self.quantity * self.price

    def get_total_discount_item_price(self):
        return self.quantity * self.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        # if self.refund_granted:
        #     return 0
        coupon=0
        if self.coupon:
            coupon=self.coupon.amount
        elif self.discount_price:
            return self.get_total_discount_item_price()-coupon
        return self.get_total_item_price()-coupon
class Payment(TimeStampedModel):
    user = models.ForeignKey('user.Users',
                             on_delete=models.SET_NULL, null=True)
    PG = models.CharField(choices=PG, max_length=3, default="T")
    imp_uid = models.CharField(max_length=50)
    status=models.CharField(max_length=50)
    pay_method = models.CharField(max_length=50)
    amount = models.IntegerField()

    #V_Bank
    vbank_name = models.CharField(max_length=100, null=True, blank=True)
    vbank_num = models.CharField(max_length=100, null=True, blank=True)
    vbank_date = models.CharField(max_length=100, null=True, blank=True)
    #Card
    card_name = models.CharField(max_length=100, null=True, blank=True)
    card_number = models.CharField(max_length=100, null=True, blank=True)
    receipt_url = models.CharField(max_length=300, null=True, blank=True)

    paid_at = models.DateTimeField(null=True, blank=True, auto_now=False, auto_now_add=False)
    
    class Meta:
        ordering = ["user"]
        verbose_name = '결제정보'
        verbose_name_plural = '결제정보들'

    def __str__(self):
        return f"{self.pay_method}/{self.user.username}"
class Coupon(TimeStampedModel):
    placement = models.ManyToManyField('auction.Placement')
    user = models.ForeignKey('user.Users',on_delete=models.CASCADE)
    title=models.CharField(max_length=100)
    amount = models.IntegerField()
    expired=models.BooleanField(default=False)
    class Meta:
        ordering = ["-updated"]
        verbose_name = '쿠폰'
        verbose_name_plural = '쿠폰들'

    def __str__(self):
        return f"{self.user.username}-{self.amount}원 쿠폰"

class CrowdFundingOrderItem(OrderItemModel):
    donation = models.OneToOneField('auction.Donation', on_delete=models.CASCADE, null=True, blank=True)
    class Meta:
        verbose_name = '일반티켓 주문'
        verbose_name_plural = '일반티켓 주문들'
    def amountToBePaid(self):
        amountToBePaid=0
        if self.deliver_detail==1:
            amountToBePaid=self.get_final_price()
        return amountToBePaid
class OpenFundingOrderItem(OrderItemModel):
    placementbid = models.OneToOneField('auction.PlacementBid', on_delete=models.CASCADE,  null=True, blank=True)
    class Meta:
        verbose_name = '오픈 펀딩 주문'
        verbose_name_plural = '오픈 펀딩 주문들'
    def amountToBePaid(self):
        amountToBePaid=0
        if self.deliver_detail==1:
            amountToBePaid=self.placement.deposit
        elif self.deliver_detail==2:
            amountToBePaid=self.get_final_price()-self.placement.deposit
        return amountToBePaid
class SecretFundingOrderItem(OrderItemModel):
    placementbid = models.OneToOneField('auction.PlacementBid', on_delete=models.CASCADE,  null=True, blank=True)
    class Meta:
        verbose_name = '경쟁티켓 주문'
        verbose_name_plural = '경쟁티켓 주문들'
    def amountToBePaid(self):
        amountToBePaid=0
        if self.deliver_detail==1:
            amountToBePaid=self.placement.deposit
        elif self.deliver_detail==2:
            amountToBePaid=self.get_final_price()-self.placement.deposit
class Questionnaire(TimeStampedModel):
    title = models.CharField(max_length=30)
    q1 = models.TextField(null=True, blank=True, help_text='1번 질문')
    q2 = models.TextField(null=True, blank=True, help_text='2번 질문')
    q3 = models.TextField(null=True, blank=True, help_text='3번 질문')
    q4 = models.TextField(null=True, blank=True, help_text='4번 질문')
    q5 = models.TextField(null=True, blank=True, help_text='5번 질문')
    q6 = models.TextField(null=True, blank=True, help_text='6번 질문')
    q7 = models.TextField(null=True, blank=True, help_text='7번 질문')
    q8 = models.TextField(null=True, blank=True, help_text='8번 질문')
    q9 = models.TextField(null=True, blank=True, help_text='9번 질문')
    q10 = models.TextField(null=True, blank=True, help_text='10번 질문')
    class Meta:
        ordering = ["-updated"]
        verbose_name = '설문지'
        verbose_name_plural = '설문지들'

    def __str__(self):
        return self.title
class Questionanswer(TimeStampedModel):
    user = models.ForeignKey('user.Users', on_delete=models.SET_NULL, null=True, blank=True)    
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.SET_NULL, null=True, blank=True)
    of_oi = models.OneToOneField(OpenFundingOrderItem, on_delete=models.CASCADE, null=True, blank=True)
    sf_oi = models.OneToOneField(SecretFundingOrderItem, on_delete=models.CASCADE, null=True, blank=True)    
    cf_oi = models.OneToOneField(CrowdFundingOrderItem, on_delete=models.CASCADE, null=True, blank=True)    
    #참여자 정보
    name = models.CharField(max_length = 50, null=True, blank=True)
    sex = models.CharField(max_length = 10, null=True, blank=True)    
    phone = models.CharField(max_length = 16, null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    job = models.CharField(max_length = 16, null=True, blank=True)    
    a1 = models.TextField(null=True, blank=True, help_text='1번 답변')
    a2 = models.TextField(null=True, blank=True, help_text='2번 답변')
    a3 = models.TextField(null=True, blank=True, help_text='3번 답변')
    a4 = models.TextField(null=True, blank=True, help_text='4번 답변')
    a5 = models.TextField(null=True, blank=True, help_text='5번 답변')
    a6 = models.TextField(null=True, blank=True, help_text='6번 답변')
    a7 = models.TextField(null=True, blank=True, help_text='7번 답변')
    a8 = models.TextField(null=True, blank=True, help_text='8번 답변')
    a9 = models.TextField(null=True, blank=True, help_text='9번 답변')
    a10 = models.TextField(null=True, blank=True, help_text='10번 답변')
    class Meta:
        ordering = ["-updated"]
        verbose_name = '응답지'
        verbose_name_plural = '응답지들'

    def __str__(self):
        if self.name:
            return f"{self.name}/{self.questionnaire.title}/응답지"
        else:
            return f"{self.questionnaire.title}/응답지"

    def save(self, *args, **kwargs):
        if self.phone:
            self.phone = Phone_Number_Standardize(self.phone)
        super().save(*args, **kwargs)

class Partnership(TimeStampedModel):
    name = models.CharField(max_length = 50)
    company = models.CharField(max_length = 50, blank=True, null=True)              
    email = models.EmailField()
    phone = models.CharField(max_length = 16)
    text = models.TextField()
    class Meta:
        ordering = ["created"]
        verbose_name = '파트너십 제안서'
        verbose_name_plural = '파트너십 제안서들'
    def __str__(self):
        if self.company:
            return f"{self.name}/{self.company} 파트너십 제안서"
        else:
            return f"{self.name} 파트너십 제안서"
class Kakao_Result(TimeStampedModel):
    text=models.TextField()
    status=models.IntegerField()
    class Meta:
        ordering=["-created"]
        verbose_name='비즈톡 전송결과'
        verbose_name_plural='비즈톡 전송결과들'

'''
Article
'''

#게시글
class Articles(TimeStampedModel):
    user = models.ForeignKey('user.Users', on_delete=models.SET_NULL, null=True, blank=True)
    category = models.CharField(choices=CATEGORY, max_length=5)
    title = models.CharField(max_length=50, default='untitled')
    text = models.TextField()
    n_hit = models.PositiveIntegerField(default=0)
    thumbnail = models.ImageField(upload_to=custom_article_path)
    badge = models.ImageField(upload_to=custom_article_path,  default='default.png', help_text="섬네일 옆 배지 이미지")

    #파트너스 겸용
    is_soldout=models.BooleanField(default=False)
    display_text = models.TextField(null=True, blank=True)
    display_place=models.TextField(null=True, blank=True)    
    display_day=models.DateTimeField(null=True, blank=True)
    display_url=models.TextField(null=True,blank=True, default='https://m.trevari.co.kr/categories/5')

    class Meta:
        verbose_name = '게시글'
        verbose_name_plural = '게시글들'
        ordering =['-created']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('core:article_detail', kwargs={'pk': self.pk})

    def update_counter(self):
        self.n_hit = self.n_hit+1
        self.save()
        return self.n_hit
    
    def save(self, *args, **kwargs):
        self.text=self.text.replace('&nbsp;',' ')
        super().save(*args, **kwargs)

#게시판 댓글
class Article_Comments(TimeStampedModel):
    article = models.ForeignKey(Articles, on_delete=models.CASCADE, related_name= "article_comment", blank=True)
    user = models.ForeignKey('user.Users', on_delete=models.CASCADE, blank=True)
    text = models.TextField()

    #대댓글 기능
    parent_article_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ["-pk"]
        db_table = 'article_comments'
        verbose_name = '게시판 댓글'
        verbose_name_plural = '게시판 댓글들'

#아티스트_문의
class Posts(TimeStampedModel):
    user = models.ForeignKey('user.Users', on_delete=models.CASCADE, related_name="post", blank=True)
    text = models.TextField()

    class Meta:
        ordering = ["-pk"]
        db_table = 'posts'
        verbose_name = '문의글'
        verbose_name_plural = '문의글들'

#아티스트_문의답변
class Comments(TimeStampedModel):
    post = models.ForeignKey(Posts, on_delete=models.CASCADE, related_name= "comment", blank=True)
    user = models.ForeignKey('user.Users', on_delete=models.CASCADE, blank=True)
    text = models.TextField()

    #대댓글 기능
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ["-pk"]
        db_table = 'comments'
        verbose_name = '문의 답변'
        verbose_name_plural = '문의 답변들'


#Crowdfunding order check
# @receiver(post_save, sender = Order)
# def Order_Check(sender, instance, *args, **kwargs):
#     try:
#         for orderitem in instance.orderitem_set.all().select_related('placement'):
#             #prefetch, selet하기
#             if orderitem.placement.placement_type == 'crowdfunding':
#                 crowdfunding_placement=orderitem.placement
#                 cnt=0
#                 users=[]
#                 for donation in crowdfunding_placement.donation_set.all():
#                     if donation.orderitem.order.ordered:
#                         cnt+=donation.get_total_price()
#                         users.append(donation.user)
#                 if cnt >= crowdfunding_placement.placement_price:
#                     d_list=Donation.objects.filter(user_id__in = [u.id for u in users])

#                     #Placement Winner에 winner group 넣기, 시간끝내기
#                     crowdfunding_placement.placement_win_crowdfunding.add(*d_list)
#                     crowdfunding_placement.placement_end=datetime.datetime.now()


#                     #메시지보내기
#                     for u in users:
#                         #문자보내기
#                         p = format(crowdfunding_placement.placement_price, ',')
#                         content=f'\n[원앤온리] {u.username}님\n[크라우드 펀딩 종료안내]\n[{crowdfunding_placement}] 펀딩이 완료되었습니다.'
#                         phone=u.verification.phone
#                         try:
#                             Phone_SMS_Send.apply_async( args=[phone, content], ignore_result=False)
#                         except:
#                             pass

#                     #placement 객체 수정
#                     # crowdfunding_placement.is_crowdfunding_finish = True
#                     # crowdfunding_placement.save()

#             elif orderitem.placement.placement_type == 'openfunding':
#                 pass
#             elif orderitem.placement.placement_type == 'secretfunding':
#                 pass
#     except:
#         pass


# class Order(TimeStampedModel):

#     #user주문자
#     user = models.ForeignKey('user.Users' ,on_delete=models.SET_NULL, null=True, blank=True)

#     #interactive with form
#     ref_code = models.CharField(max_length=30)
#     ordered_date = models.DateTimeField(null=True)
#     ordered = models.BooleanField(default=False)

#     #form
#     PG = models.CharField(choices=PG, max_length=3, default="BT")

#     #COUPON
#     coupon = models.ForeignKey(
#         'Coupon', on_delete=models.SET_NULL, blank=True, null=True)

#     class Meta:
#         verbose_name = '주문'
#         verbose_name_plural = '주문들'

#     def __str__(self):
#         name=''
#         name+=self.user.username + "님의 " + '{0}'.format(self.get_total_count()) + "개 주문"
#         return name

#     def get_total(self):
#         total = 0
#         for i in self.orderitem_set.all():
#             total += i.get_total_item_price()
#         return total

#     def get_final_price(self):
#         total = 0
#         for i in self.orderitem_set.all():
#             total += i.get_final_price()            
#         if self.coupon:
#             total -= self.coupon.amount
#         return total

#     def get_total_count(self):
#         total = 0
#         for i in self.orderitem_set.all():
#             total += i.quantity            
#         return total

#     def get_item_name(self):
#         name = ''
#         for i in self.orderitem_set.all():
#             name += str(i) + ', '
#         return name

#     class Meta:
#         ordering = ["ordered_date"]

# #굿즈ITEM(구 orderitem + item)
# class OrderItem(TimeStampedModel):

#     #user주문자, Placement 상품
#     user = models.ForeignKey('user.Users', on_delete=models.SET_NULL, null=True, blank=True)
#     placement = models.ForeignKey('auction.Placement', on_delete=models.SET_NULL, related_name= "orderitem", null=True, blank=True)
#     order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    
#     #interactive with form
#     deliver_detail = models.IntegerField(choices=DELIVER_CHOICES, blank=True, default=0)
#     price = models.IntegerField(default=100000, blank=True)
#     discount_price = models.IntegerField(blank=True, null=True)    
#     quantity = models.IntegerField(default=1)

#     #REFUND
#     refund_requested = models.BooleanField(default=False)
#     refund_granted = models.BooleanField(default=False)

#     #EXPIRE
#     expired = models.BooleanField(default=False)


#     class Meta:
#         ordering = ["updated"]
#         verbose_name = '주문 상품'
#         verbose_name_plural = '주문 상품들'

#     def __str__(self):
#         return f"{self.quantity} * {self.placement} / by:{self.user.username}"

#     def get_total_item_price(self):
#         return self.quantity * self.price

#     def get_total_discount_item_price(self):
#         return self.quantity * self.discount_price

#     def get_amount_saved(self):
#         return self.get_total_item_price() - self.get_total_discount_item_price()

#     def get_final_price(self):
#         if self.refund_granted:
#             return 0
#         elif self.discount_price:
#             return self.get_total_discount_item_price()
#         return self.get_total_item_price()


# #-----------------------------------------------------
#주문서(구 orderitem+item)
# class OrderArtists(models.Model):

#     #user주문자, artist만든사람
#     user = models.ForeignKey('user.Users', on_delete=models.SET_NULL, null=True, blank=True)
#     artist = models.ForeignKey('artist.Artists', on_delete=models.SET_NULL, related_name= "orderartist", null=True, blank=True)                         
#     order = models.ForeignKey(Orders, on_delete=models.SET_NULL, null=True, blank=True)    

#     #interactive with form
#     delivered = models.BooleanField(default=False, blank=True)
#     deliver_detail = models.IntegerField(choices=DELIVER_CHOICES, blank=True, default=0)
#     discount_price = models.IntegerField(default=100000, blank=True, null=True)
#     price = models.IntegerField(default=100000, blank=True)

#     #form
#     music_purpose = models.IntegerField(choices=MUSIC_PURPOSE)
#     music_name = models.CharField(max_length=20)
#     music_vibe = models.CharField(max_length=100, blank=True)
#     music_ref = models.CharField(max_length=20, blank=True)
# #    music_event =models.CharField(max_length=20 )

#     music_receiver = models.CharField(max_length=20, blank=True)
# #    video_text= models.CharField(max_length=100 )
# #    artist_text= models.CharField(max_length=100 )



#     #자동
#     updated = models.DateTimeField(auto_now=True)
#     quantity = models.IntegerField(default=1)
#     class Meta:
#         ordering = ["updated"]
#         verbose_name = 'OrderArtist'
#         verbose_name_plural = 'OrderArtists'

#     def __str__(self):
#         return f"{self.quantity} * {self.artist} orderby:{self.user.username}"

#     def get_total_item_price(self):
#         return self.quantity * self.price

#     def get_total_discount_item_price(self):
#         return self.quantity * self.discount_price

#     def get_amount_saved(self):
#         return self.get_total_item_price() - self.get_total_discount_item_price()

#     def get_final_price(self):
#         if self.discount_price:
#             return self.get_total_discount_item_price()
#         return self.get_total_item_price()


#주문한 영상 업로드 및 저장 모델
# def custom_video_path(instance, filename):
#     # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
#     c=instance.user.username
#     f=instance.artist.K_name +"의 영상작품" + str(datetime.datetime.now())
#     return 'ClientVideo/{0}/{1}'.format(c, f)
# class OrderVideos(models.Model):
#     #set
#     artist = models.ForeignKey('artist.Artists', on_delete=models.SET_NULL, null=True, blank=True)
#     user = models.ForeignKey('user.Users', on_delete=models.SET_NULL, null=True, blank=True)
#     orderartist = models.OneToOneField(OrderArtists, on_delete=models.SET_NULL, null=True, blank=True)

#     #manual type
#     title = models.CharField(max_length=100)
#     description = models.TextField(blank = True)
#     video = models.FileField(upload_to=custom_video_path)
#     password = models.CharField(max_length=10, default="PLAYPLZ", null=True, blank=True)

#     #auto add
#     start_date = models.DateTimeField(auto_now_add=True)
#     class Meta:
#         verbose_name = 'OrderVideo'
#         verbose_name_plural = 'OrderVideos'
#     def __str__(self):
#         return self.title

# INSTRUMENT_CHOICES = (
#     ('H', '현악기'),
#     ('G', '관악기'),
#     ('T', '타악기'),
#     ('ETC', '기타')
# )


# CATEGORY_CHOICES = (
#     ('H', '현악기'),
#     ('G', '관악기'),
#     ('T', '타악기'),
#     ('ETC', '기타')
# )

# LABEL_CHOICES = (
#     ('P', 'primary'),
#     ('S', 'secondary'),
#     ('D', 'danger')
# )

# ADDRESS_CHOICES = (
#     ('B', 'Billing'), #speical request
#     ('S', 'Shipping'),
# )


# class Item(models.Model):
#     title = models.CharField(max_length=100)
#     price = models.IntegerField()
#     discount_price = models.IntegerField(blank=True, null=True)
#     category = models.CharField(choices=CATEGORY_CHOICES, max_length=3, default="ETC")
#     label = models.CharField(choices=LABEL_CHOICES, max_length=1)
#     description = models.TextField()
#     image = models.ImageField(upload_to='item/image')
#     video = models.FileField(upload_to='item/video')
#     slug = models.SlugField()
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
#     like_user = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='like_item',  blank=True, null= True)
#     onlyforartist = models.BooleanField(default = False)
#     onlyforspecial = models.BooleanField(default=False)
#     special_price = models.IntegerField(null=True) #special album 살때 가격
#     discount_special_price = models.IntegerField(null=True, blank=True)  # special album 살때 가격
#     recommend = models.CharField(max_length=10, null=True, blank=True)

#     def __str__(self):
#         return self.title

#     def get_absolute_url(self):
#         return reverse("core:product", kwargs={
#             'slug': self.slug
#         })

#     def get_add_to_cart_url(self):
#         return reverse("core:add-to-cart", kwargs={
#             'slug': self.slug
#         })

#     def get_direct_add_to_cart_url(self):
#         return reverse("core:direct_add-to-cart", kwargs={
#             'slug': self.slug
#         })

#     def get_remove_from_cart_url(self):
#         return reverse("core:remove-from-cart", kwargs={
#             'slug': self.slug
#         })

# class OrderItem(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL,
#                              on_delete=models.CASCADE)
#     ordered = models.BooleanField(default=False)
#     ordered_detail = models.IntegerField(choices=ORDERDETAIL_CHOICES, null= True, blank = True)
#     updated = models.DateTimeField(auto_now=True)
#     item = models.ForeignKey(Item, on_delete=models.CASCADE, null= True)
#     quantity = models.IntegerField(default=1)
#     author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null = True, related_name="orderitem_author")

#     def __str__(self):
#         return f"{self.quantity} * {self.item.title} orderby:{self.user.username}"

#     def get_total_item_price(self):
#         return self.quantity * self.item.price

#     def get_total_discount_item_price(self):
#         return self.quantity * self.item.discount_price

#     def get_amount_saved(self):
#         return self.get_total_item_price() - self.get_total_discount_item_price()

#     def get_final_price(self):
#         if self.item.discount_price:
#             return self.get_total_discount_item_price()
#         return self.get_total_item_price()

#     def article_upload_time(self):

#             for a in self.article_orderitem.all():
#                 return a.start_date

# class Order(models.Model):
#     id = models.AutoField(primary_key=True)
#     user = models.ForeignKey(settings.AUTH_USER_MODEL,
#                              on_delete=models.CASCADE)
#     ref_code = models.CharField(max_length=20)
#     items = models.ManyToManyField(OrderItem)
#     start_date = models.DateTimeField(auto_now_add=True)
#     ordered_date = models.DateTimeField()
#     ordered = models.BooleanField(default=False)
#     address = models.ForeignKey(
#         'Address', related_name='address', on_delete=models.SET_NULL, null=True)
#     special_address = models.ForeignKey(
#         'Address', related_name='special_address', on_delete=models.SET_NULL, blank=True, null=True)
#     payment = models.ForeignKey(
#         'Payment', on_delete=models.SET_NULL, null=True)
#     coupon = models.ForeignKey(
#         'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
#     being_delivered = models.BooleanField(default=False)
#     received = models.BooleanField(default=False)
#     refund_requested = models.BooleanField(default=False)
#     refund_granted = models.BooleanField(default=False)
#     PG = models.CharField(max_length = 10)
#     pre_request = models.CharField(max_length=100, blank=True, null=True)
#     '''
#     1. Item added to cart
#     2. Adding a billing address
#     (Failed checkout)
#     3. Payment
#     (Preprocessing, processing, packaging etc.)
#     4. Being delivered
#     5. Received
#     6. Refunds
#     '''

#     def __str__(self):
#          return self.user.username

#     def get_total(self):
#         total = 0
#         for order_item in self.items.all():
#             total += order_item.get_final_price()
#         if self.coupon:
#             total -= self.coupon.amount
#         return total

#     def get_total_count(self):
#         total = 0
#         for order_item in self.items.all():
#             total += order_item.quantity
#         return total

#     def get_item_name(self):
#         name = ''
#         for order_item in self.items.all():
#             name += str(order_item) + ', '
#         return name

# class Item(models.Model):
#     title = models.CharField(max_length=100)
#     price = models.IntegerField()
#     discount_price = models.IntegerField(blank=True, null=True)
#     category = models.CharField(choices=CATEGORY_CHOICES, max_length=3, default="ETC")
#     label = models.CharField(choices=LABEL_CHOICES, max_length=1)
#     description = models.TextField()
#     image = models.ImageField(upload_to='item/image')
#     video = models.FileField(upload_to='item/video')
#     slug = models.SlugField()
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
#     like_user = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='like_item',  blank=True)
#     onlyforartist = models.BooleanField(default = False)
#     onlyforspecial = models.BooleanField(default=False)
#     special_price = models.IntegerField(null=True) #special album 살때 가격
#     discount_special_price = models.IntegerField(null=True, blank=True)  # special album 살때 가격
#     recommend = models.CharField(max_length=10, null=True, blank=True)

#     def __str__(self):
#         return self.title

#     def get_absolute_url(self):
#         return reverse("core:product", kwargs={
#             'slug': self.slug
#         })

#     def get_add_to_cart_url(self):
#         return reverse("core:add-to-cart", kwargs={
#             'slug': self.slug
#         })

#     def get_direct_add_to_cart_url(self):
#         return reverse("core:direct_add-to-cart", kwargs={
#             'slug': self.slug
#         })

#     def get_remove_from_cart_url(self):
#         return reverse("core:remove-from-cart", kwargs={
#             'slug': self.slug
#         })


# class Article(models.Model):
#     title = models.CharField(max_length=100)
#     category = models.CharField(choices=CATEGORY_CHOICES, max_length=2, blank= True, null = True)
#     description = models.TextField(blank = True, null = True)
#     image = models.ImageField(upload_to='article/image', blank= True, null = True)
#     video = models.FileField(upload_to='article/video', blank= True, null = True)
#     slug = models.SlugField(null = True, blank = True)
#     article_password = models.CharField(max_length=20, null=True, blank = True)
#     embedurl = models.CharField(max_length=200)
#     client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name='client')
#     author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name='author')
#     orderitem = models.ForeignKey(OrderItem, on_delete=models.CASCADE, null=True, related_name='article_orderitem')
#     start_date = models.DateTimeField(auto_now_add=True, null = True)

#     def __str__(self):
#         return self.title

#     def get_absolute_url(self):
#         return reverse("core:customer_product", kwargs={
#             'slug': self.slug
#         })

#     def password(self):
#         return reverse("core:customer_product", kwargs={
#             'slug': self.slug
#         })



# class Video(models.Model):
#     title = models.CharField(max_length=200)
#     video = models.FileField(upload_to='videos/')

#     class Meta:
#         verbose_name = 'video'
#         verbose_name_plural = 'videos'

#         def __str__(self):
#             return self.title

# class UserProfile(models.Model):
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
#     one_click_purchasing = models.BooleanField(default=False)
#     image = models.ImageField(upload_to='profile/image', blank=True)
#     video = models.FileField(upload_to='profile/video')
#     instrument = models.CharField(choices=INSTRUMENT_CHOICES, max_length=3)
#     description = models.CharField(max_length = 100, blank=True, null=True)
#     followers = models.ManyToManyField("self", blank=True, related_name="followers")
#     followings = models.ManyToManyField("self", blank=True, related_name="followings")
#     start_date = models.DateTimeField(auto_now_add=True, null = True)

#     def __str__(self):
#         return self.user.username

#     def get_absolute_url(self):
#         return reverse("core:artist_profile_detail", kwargs={
#             'pk': self.pk
#         })

# #MD 추천상품
# class BG_MDPICK(models.Model):
#     title = models.CharField(max_length=100)
#     def __str__(self):
#         return self.title

# class SM_MDPICK(models.Model):
#     title = models.CharField(max_length=100)
#     items = models.ManyToManyField(Item, blank=True, related_name="md_items")
#     artists = models.ManyToManyField(UserProfile,  blank=True, related_name="md_artists")
#     bg_mdpick=models.ForeignKey(BG_MDPICK, on_delete=models.CASCADE, null=True)
#     def __str__(self):
#         return self.title


# class Comment(models.Model):
#     content = models.TextField(max_length=50)
#     item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True)
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     start_date = models.DateTimeField(auto_now_add=True, null=True)


# class Address(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL,
#                              on_delete=models.CASCADE)
#     email = models.CharField(max_length=100, null=True)
#     request = models.CharField(max_length=100, null=True)
#     phone = models.CharField(max_length=15, null=True)
#     zip = models.CharField(max_length=10, null=True)
#     address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
#     default = models.BooleanField(default=False)

#     def __str__(self):
#         return str(self.phone)

#     class Meta:
#         verbose_name_plural = 'Addresses'


# class Payment(models.Model):
#     stripe_charge_id = models.CharField(max_length=50)
#     user = models.ForeignKey(settings.AUTH_USER_MODEL,
#                              on_delete=models.SET_NULL, blank=True, null=True)
#     amount = models.IntegerField()
#     timestamp = models.DateTimeField(auto_now_add=True)
#     def __str__(self):
#         return str(self.amount)


# class Coupon(models.Model):
#     code = models.CharField(max_length=15)
#     amount = models.IntegerField()

#     def __str__(self):
#         return self.code


# class Refund(models.Model):
#     order = models.ForeignKey(Order, on_delete=models.CASCADE)
#     reason = models.TextField()
#     accepted = models.BooleanField(default=False)
#     email = models.EmailField()

#     def __str__(self):
#         return f"{self.pk}"


# def userprofile_receiver(sender, instance, created, *args, **kwargs):
#     if created:
#         userprofile = UserProfile.objects.create(user=instance, pk=instance.pk)

# post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL)
