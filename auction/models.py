from django.urls import reverse
from django.db import models
from django.dispatch.dispatcher import receiver
from django.db.models.signals import post_save, post_delete
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
from core.utils import remove_tags
import json
from django.core.validators import FileExtensionValidator
from core.managers import TimeStampedModel

#'value(단계)', 'display(보여지는 display)'
AUCTION_TYPE = (
    ('crowdfunding', '일반티켓'), #펀딩
    ('secretfunding', '경쟁티켓'), #비밀경매
    ('openfunding', '경매'), #Depreciated
)

class AuctionArtist(TimeStampedModel):
    """
    옥션아티스트 모델(artists.Artist와 연동가능)
    """
    user = models.OneToOneField("user.Users", on_delete=models.CASCADE, null=True, blank=True)
    avatar = models.ImageField(upload_to='Auction/avatar/', help_text = "Auction 아티스트 이미지", default='default.png', blank=True,)
    name = models.TextField(max_length=255, default="AUCTION 아티스트 한국이름")
    E_name = models.TextField(max_length=255, default="AUCTION 아티스트 영어이름")
    description = models.TextField(default="AUCTION 아티스트 소개")
    description_oneoff = models.TextField(default="AUCTION 아티스트 한줄")
    description_info = models.TextField(default="AUCTION 아티스트 약력")
    slug = models.SlugField(max_length=40, help_text="포트폴리오 index_slug.html")
    class Meta: 
        ordering = ['-created'] 
        verbose_name = '옥션 아티스트'
        verbose_name_plural = '옥션 아티스트들'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("auction:auctionartistdetailview", kwargs={
            'slug': self.slug
        })

def custom_video_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    c=instance.placement_artist.name
    t=instance.title
    # fileName, fileExtension = os.path.splitext(filename)
    return 'Auction/{0}/{1}/video-{2}'.format(c,t,filename)

def custom_remember_image_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    c=instance.placement.placement_artist.name
    t=instance.placement.title
    return 'Auction/{0}/{1}/remember/{2}'.format(c,t,filename)

def custom_etc_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    c=instance.placement_artist.name
    t=instance.title
    return 'Auction/{0}/{1}/{2}'.format(c,t,filename)

class Placement(TimeStampedModel):
    """
    공통
    """    
    #정보
    title=models.TextField(max_length=50, help_text="제목")
    description=models.TextField(max_length=400, help_text='설명')
    category=models.CharField(max_length=15, help_text="Music, Dance, Making, etc ...")
    rep=models.CharField(max_length=15, help_text="회차 정보", blank=True, null=True)
    duration=models.CharField(max_length=50, help_text="만남 시간", blank=True, null=True)
    d_day=models.DateTimeField(help_text="만남 날짜", blank=True, null=True)
    d_place=models.CharField(max_length=100, help_text="만남 장소", blank=True, null=True)
    thumbnail = models.ImageField(upload_to=custom_etc_path, help_text = "Thumbnail Image", default='default.png', blank=True, null=False)
    secret_video = models.FileField(upload_to=custom_video_path, help_text = "Unboxing list video", default='default.mp4', blank=True, null=False)
    unboxing_video_mp4 = models.FileField(upload_to=custom_video_path, help_text = "Unboxing list video", validators=[FileExtensionValidator(allowed_extensions=['mp4'])], default='default.mp4', blank=True, null=False)
    m_banner_video_mp4 = models.FileField(upload_to=custom_video_path, help_text = "Mobile mp4 VIDEO", validators=[FileExtensionValidator(allowed_extensions=['mp4'])], default='default.mp4', blank=True, null=False)
    pc_banner_video_mp4 = models.FileField(upload_to=custom_video_path, help_text = "PC mp4 VIDEO", validators=[FileExtensionValidator(allowed_extensions=['mp4'])], default='default.mp4', blank=True, null=False)
    youtube_id = models.CharField(max_length=50, null=True, blank=True)
    image_1 = models.ImageField(upload_to=custom_etc_path, help_text = "상품 설명 이미지 1", default='default.png', blank=True, null=False)
    image_2 = models.ImageField(upload_to=custom_etc_path, help_text = "상품 설명 이미지 2", default='default.png', blank=True, null=False)
    image_3 = models.ImageField(upload_to=custom_etc_path, help_text = "상품 설명 이미지 3", default='default.png', blank=True, null=False)
    image_4 = models.ImageField(upload_to=custom_etc_path, help_text = "상품 설명 이미지 4", default='default.png', blank=True, null=False)    
    image_5 = models.ImageField(upload_to=custom_etc_path, help_text = "상품 설명 이미지 4", default='default.png', blank=True, null=False)
    detail_1_title = models.TextField(help_text='에디터 제목', null=True, blank=True, default="에디터 노트")
    detail_1 = models.TextField(help_text='에디터 설명', null=True, blank=True)
    detail_2_title = models.TextField(help_text='상품상세 2 타이틀', null=True, blank=True)
    detail_2 = models.TextField(help_text='상품상세 2', null=True, blank=True)
    detail_3_title = models.TextField(help_text='상품상세 3 타이틀', null=True, blank=True)
    detail_3 = models.TextField(help_text='상품상세 3', null=True, blank=True)
    detail_4_title = models.TextField(help_text='상품상세 4 타이틀', null=True, blank=True)
    detail_4 = models.TextField(help_text='상품상세 4', null=True, blank=True)
    detail_5_title = models.TextField(help_text='상품상세 5 타이틀', null=True, blank=True)
    detail_5 = models.TextField(help_text='상품상세 5', null=True, blank=True)
    detail_6_title = models.TextField(help_text='상품상세 6 타이틀', null=True, blank=True)
    detail_6 = models.TextField(help_text='상품상세 6', null=True, blank=True)    
    etc_1 = models.TextField(help_text='기타정보1', null=True, blank=True)
    etc_1_on = models.BooleanField(help_text='기타정보1 활성화', default=False)
    etc_2 = models.TextField(help_text='기타정보2', null=True, blank=True)
    etc_2_on = models.BooleanField(help_text='기타정보2 활성화', default=False)

    #성분
    placement_artist = models.ForeignKey(AuctionArtist, on_delete=models.CASCADE, null=True)    
    placement_type = models.CharField(choices=AUCTION_TYPE, max_length=20, default='crowdfunding', help_text="경매 종류")
    placement_price = models.IntegerField(default=100000)
    placement_start=models.DateTimeField(default=timezone.now)
    placement_end=models.DateTimeField(default=timezone.now)
    placement_order = models.IntegerField(default=1, help_text = "음수: 종료, 1 < : 진행중, 1:예정, 0:가리기")
    is_encore = models.BooleanField(default=False, help_text="앵콜요청")
    unit_price = models.IntegerField(default=50000, help_text="일반티켓 가격 or 경쟁티켓 가격")
    deposit = models.IntegerField(default=300000, help_text="예약금")
    buy_limit = models.IntegerField(default=5, help_text="구매 제한 개수")

    #설문지
    questionnaire = models.ForeignKey("core.Questionnaire", on_delete=models.SET_NULL, null=True, blank=True)

    """
    옥션 상품
    """
    placement_start_price = models.IntegerField(default=100000)
    placement_estimated_price = models.TextField(default="AUCTION 추정가")
    placement_buynow_price = models.IntegerField(default=500000)
    placement_win = models.ForeignKey("auction.PlacementBid", on_delete=models.CASCADE, null=True, blank=True, related_name='placement_win')

    '''
    CrowdFunding 상품
    '''
    placement_win_crowdfunding = models.ManyToManyField("auction.Donation", blank=True, related_name='placement_win_crowdfunding')
    #target_amount=placement_price
    #target_unit = unit_price

    class Meta: 
        ordering = ['-placement_order'] 
        verbose_name = '옥션상품'
        verbose_name_plural = '옥션상품들'

    def __str__(self):
        return self.title
    def save(self, *args, **kwargs):
        self.title=self.title.replace('<p>','').replace('</p>','')
        super().save(*args, **kwargs)
    # def save(self, *args, **kwargs):
    #     #최초등록
    #     if self._state.adding:
    #         pass
    #     super().save(*args, **kwargs)

    # def get_placement_type_display(self):
    #     if self.placement_type == 'crowdfunding':
    #         if self.get_ready_cnt == '1':
    #             return '일반구매(단독)'
    #         else:
    #             return '일반구매'
    #     elif self.placement_type == 'secretfunding':
    #         return '경쟁구매'
    #     else:
    #         return '오픈펀딩(depreciated)'
    def to_json(self):
        return json.dumps({
            'pk':self.pk,
            'title':self.title,
            'description':remove_tags(self.description),
            'artist':self.placement_artist.name,
            'thumbnail':self.thumbnail.url,
            'category':self.category,
            'placement_start':self.placement_start,
            'placement_end':self.placement_end,
        }, cls=DjangoJSONEncoder, ensure_ascii=False)
       
    def get_absolute_url(self):
        return reverse("auction:pdv", kwargs={
            'pk': self.pk
        })

    #ADMIN PREVIEW용
    def get_admin_absolute_url(self):
        return reverse("auction:admin-pdv", kwargs={
            'pk': self.pk
        })

    #옥션
    def get_final_price(self):
        pbs=self.placementbid_set.all()
        if pbs:
            return pbs.order_by('-offer')[0].offer
        else:
            return self.placement_price

    #판매 티켓 수
    def get_ready_cnt(self):
        if self.placement_type == 'crowdfunding':
            return int(self.placement_price/self.unit_price)
        else:
            return 1

    def get_crowdfunding_total(self):
        if self.placement_type == 'crowdfunding':
            cnt=0
            donation_qs=self.donation_set.all()
            if donation_qs.exists():
                for donation in donation_qs:
                    try:
                        if not donation.crowdfundingorderitem.expired:
                            cnt+=donation.get_total_price()
                    except:
                        pass
            return cnt
    #실제 결제완료
    def get_crowdfunding_total_really(self):
        cnt=0        
        if self.placement_type == 'crowdfunding':
            for oi in self.crowdfundingorderitem_set.all():
                if (not oi.expired) and oi.deliver_detail >=3:
                    cnt+=oi.donation.get_total_price()
        return cnt

    def get_crowdfunding_total_cnt(self):
        if self.placement_type == 'crowdfunding':
            cnt=0
            donation_qs=self.donation_set.all()
            if donation_qs.exists():
                for donation in donation_qs:
                    if not donation.crowdfundingorderitem.expired:
                        cnt+=donation.quantity
            return cnt

    def get_crowdfunding_available_cnt(self):
        if self.placement_type == 'crowdfunding':
            try:
                return int((self.placement_price - self.get_crowdfunding_total())/self.unit_price)
            except:
                pass
            return 0

    #클라이언트 입장 FINISH
    def is_crowdfunding_finish(self):
        if self.placement_type == 'crowdfunding':        
            cnt = 0
            for oi in self.crowdfundingorderitem_set.all():
                if not oi.expired:
                    cnt += oi.donation.get_total_price()
            return self.placement_price <= cnt
    
    #결제완료 관점에서 FINISH
    def is_crowdfunding_really_finish(self):
        if self.placement_type == 'crowdfunding':
            cnt=0
            for oi in self.crowdfundingorderitem_set.all():
                if (not oi.expired) and oi.deliver_detail >=3:
                    cnt+=oi.donation.get_total_price()
            if cnt >= self.placement_price:
                return True
            return False

#옥션 모델(autobid, placementbid)
class TimeStoreItem(TimeStampedModel):
    placement = models.ForeignKey(Placement, on_delete=models.CASCADE, null=True, blank=True)
    background = models.ImageField(help_text = "TimeStore Background Image")
    image = models.ImageField(help_text = "TimeStore Thumbnail Image")
    title=models.TextField(max_length=50)
    description=models.TextField(max_length=400)
    url=models.URLField(max_length=200, null=True, blank=True)
    is_soldout=models.BooleanField(default=False)
    is_col=models.BooleanField(default=False)
    class Meta: 
        ordering = ['-id'] 
        verbose_name = '굿즈'
        verbose_name_plural = '굿즈들'

    def __str__(self):
        if self.placement:
            return f"{self.placement.title[:13]}...굿즈"
        else:
            return f"{self.title} 굿즈"

    def get_absolute_url(self):
        return reverse("auction:tdv", kwargs={
            'pk': self.pk
        })
class PlacementMemory(TimeStampedModel):
    placement = models.OneToOneField(Placement, on_delete=models.CASCADE)
    history_background = models.ImageField(upload_to=custom_remember_image_path, help_text="Remember Background", null=True)
    history_sign = models.ImageField(upload_to=custom_remember_image_path, help_text="Remember Sign", null=True)
    history_thumbnail = models.ImageField(upload_to=custom_remember_image_path, help_text = "Remember Thumbnail", null=True)
    celeb_name = models.CharField(max_length=50, help_text="셀럽의 성함을 입력해주세요")
    celeb_comment = models.CharField(max_length=500, help_text="셀럽의 코멘트를 입력해주세요")

    class Meta: 
        ordering = ['-created'] 
        verbose_name = '옥션기록'
        verbose_name_plural = '옥션기록들'

    def __str__(self):
        count = self.oneys.all().count()
        if count > 1:
            return '{}이/가 {}명 에게'.format(self.celeb_name, count)
        elif count == 1:
            return '{}이/가 {}에게'.format(self.celeb_name, self.oneys.all()[0])
        else:
            return f"{self.celeb_name}의 기록"
class Oney(TimeStampedModel):
    placementmemory = models.ForeignKey(PlacementMemory, on_delete=models.CASCADE, related_name='oneys')
    name = models.CharField(max_length=50, help_text="워니의 성함을 입력해주세요")
    comment = models.CharField(max_length=500, help_text="워니의 코멘트를 입력해주세요")
    class Meta: 
        ordering = ['-created'] 
        verbose_name = '기록 워니'
        verbose_name_plural = '기록 워니들'
    def __str__(self):
        return self.name

class AutoBid(TimeStampedModel):
    """
    Autobidding 객체
    """
    user = models.ForeignKey("user.Users", on_delete=models.CASCADE)
    limit = models.IntegerField()
    placement = models.ForeignKey(Placement, on_delete=models.CASCADE)    
    class Meta: 
        ordering = ['-created'] 
        verbose_name = '자동응찰'
        verbose_name_plural = '자동응찰들'

    def __str__(self):
        return '{}-{}'.format(self.user.username, self.created)

class PlacementBid(TimeStampedModel):
    """
    옥션 응찰객체
    """

    user = models.ForeignKey("user.Users", on_delete=models.CASCADE)
    placement = models.ForeignKey(Placement, on_delete=models.CASCADE)
    offer = models.IntegerField()
    confirmed = models.BooleanField(default=False)
    is_autobid = models.BooleanField(default=False)
    is_superior = models.BooleanField(default=False)    
    class Meta: 
        ordering = ['placement', '-offer'] 
        verbose_name = '응찰객체'
        verbose_name_plural = '응찰객체들'
    def __str__(self):
        return '{}/{}-{}'.format(self.placement, self.offer, self.user)

    def save(self, *args, **kwargs):
        #오픈펀딩
        if self.placement.placement_type=='openfunding':
            max=PlacementBid.objects.filter(placement=self.placement).order_by('-offer','-id').first()
            if max:
                if self.offer >= max.offer:
                    super().save(*args, **kwargs)
                else:
                    return
            else:
                super().save(*args, **kwargs)

        #크라우드, 시크릿펀딩
        else:
            super().save(*args, **kwargs)            


#크라우드 펀딩 모델(Donation)
class Donation(TimeStampedModel):
    """
    크라우드펀딩 모금객체
    """
    user = models.ForeignKey("user.Users", on_delete=models.CASCADE)
    placement = models.ForeignKey(Placement, on_delete=models.CASCADE)
    offer = models.IntegerField()
    quantity = models.IntegerField(default=1)

    class Meta:
        ordering = ['placement', '-updated'] 
        verbose_name = '일반티켓 펀딩객체'
        verbose_name_plural = '일반티켓 펀딩객체들'        

    def __str__(self):
        return '{} * {}/{}-{}'.format(self.quantity, self.placement, self.offer, self.user)

    def get_total_price(self):
        return self.quantity*self.offer

    # def save(self, *args, **kwargs):
    #     max=PlacementBid.objects.filter(placement=self.placement).order_by('-offer','-id').first()
    #     if max:
    #         if self.offer >= max.offer:
    #             super().save(*args, **kwargs)
    #         else:
    #             return
    #     else:
    #         super().save(*args, **kwargs)


@receiver(post_save, sender = PlacementBid)
def PlacementBid_Unit_Placement_Price_Update_Post_Save(sender, instance, *args, **kwargs): 
    """
    PlacementBid생성 -> unit_price 검증 + placement_price 검증
    """
    pk=instance.placement.pk
    p = Placement.objects.get(pk=pk)
    pbd= PlacementBid.objects.filter(placement=p)
    offer = pbd.first().offer
    unit_price = p.unit_price
    if offer < 1000000 and unit_price != 50000:
        p.unit_price = 50000
    elif 1000000 <= offer and offer < 3000000 and unit_price != 100000:
        p.unit_price = 100000
    elif 3000000 <= offer and offer < 5000000 and unit_price != 200000:
        p.unit_price = 200000
    elif 5000000 <= offer and offer < 10000000 and unit_price != 300000:
        p.unit_price = 300000
    elif 10000000 <= offer and offer < 30000000 and unit_price != 500000:
        p.unit_price = 500000
    elif 30000000 <= offer and offer < 50000000 and unit_price != 1000000:
        p.unit_price = 1000000
    elif 50000000 <= offer and offer < 100000000 and unit_price != 2000000:
        p.unit_price = 2000000
    elif 100000000 <= offer and offer < 200000000 and unit_price != 3000000:
        p.unit_price = 3000000
    elif 200000000 <= offer and unit_price != 5000000:
        p.unit_price = 5000000
    p.placement_price=offer
    p.save()

@receiver(post_delete, sender = PlacementBid)
def PlacementBid_Unit_Placement_Price_Update_Post_Delete(sender, instance, *args, **kwargs):
    """
    PlacementBid삭제 -> unit_price 검증 + placement_price 검증
    """
    pk=instance.placement.pk
    p = Placement.objects.get(pk=pk)
    pbd= PlacementBid.objects.filter(placement=p)
    offer= p.placement_start_price
    if pbd.first() is not None:
        offer = pbd.first().offer
    unit_price = p.unit_price
    if offer < 1000000 and unit_price != 50000:
        p.unit_price = 50000
    elif 1000000 <= offer and offer < 3000000 and unit_price != 100000:
        p.unit_price = 100000
    elif 3000000 <= offer and offer < 5000000 and unit_price != 200000:
        p.unit_price = 100000
    elif 5000000 <= offer and offer < 10000000 and unit_price != 300000:
        p.unit_price = 100000
    elif 10000000 <= offer and offer < 30000000 and unit_price != 500000:
        p.unit_price = 100000
    elif 30000000 <= offer and offer < 50000000 and unit_price != 1000000:
        p.unit_price = 100000
    elif 50000000 <= offer and offer < 100000000 and unit_price != 2000000:
        p.unit_price = 100000
    elif 100000000 <= offer and offer < 200000000 and unit_price != 3000000:
        p.unit_price = 100000
    elif 200000000 <= offer and unit_price != 5000000:
        p.unit_price = 100000
    p.placement_price=offer
    p.save()
# @receiver(post_save, sender = Placement)
# def Placement_Finish_MSG(sender, instance, **kwargs):
#     if instance.placement_win:
#         winner=instance.placement_win
#         for u in Users.objects.all():
#             for p in Placement.objects.filter(id=instance.id):
class AuctionAuthorization(models.Model):
    user = models.ForeignKey("user.Users", on_delete=models.CASCADE, null=True, blank=True)
    placement = models.ForeignKey(Placement, related_name="auctionauthorization", on_delete=models.CASCADE, null=True, blank=True)
    code = models.CharField(max_length=20, unique=True, null=True, blank=True)
    is_authorized = models.BooleanField(default=False)
    class Meta:
        ordering = ['-user']
        verbose_name = '옥션 권한객체'
        verbose_name_plural = '옥션 권한객체들'
    def __str__(self):
        return '{0}-{1}-{2}'.format(self.user, self.placement, self.is_authorized)

class AuctionNftToken(models.Model):
    token_id = models.TextField()
    class Meta:
        ordering = ['-id']
        verbose_name = 'NFT 토큰'
        verbose_name_plural = 'NFT 토큰들'    
    def __str__(self):
        return "NFT_TOKEN"