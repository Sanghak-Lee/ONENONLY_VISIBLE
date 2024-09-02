from django.db import models
from django.dispatch.dispatcher import receiver
from django.shortcuts import reverse
from django.db.models.signals import post_save, pre_delete, pre_save
from django.core.validators import MinValueValidator, MaxValueValidator
#'value(단계)', 'key(보여지는 key)'
ACCOUNTS = (
    ('KB', 'KB국민은행'),
    ('WOORI', '우리은행'),
    ('NH', 'NH농협은행'),
    ('SHINHAN', '신한은행'),
    ('HANA', '하나은행'),
    ('IBK', 'IBK기업은행'),
    ('SC', 'SC제일은행'),
    ('CITY', '씨티은행'),
    ('KDB', 'KDB산업은행'),
    ('KAKAO', '카카오뱅크'),
    ('SU', '수협은행'),
    ('ETC', '기타')
)

INSTRUMENTS = (
    ('H', '현악기'),
    ('G', '관악기'),
    ('T', '타악기'),
    ('ETC', '기타')
)

LEVELS = (
    ('B', 'Bronze'),
    ('S', 'Silver'),
    ('G', 'Gold'),
)

SCORE = (
    (1, '1 플플'),
    (2, '2 플플'),
    (3, '3 플플'),
    (4, '4 플플'),
    (5, '5 플플'),
)

class Artists(models.Model):
    #user본체
    user = models.OneToOneField("user.Users", on_delete=models.CASCADE, related_name="artist")
    #활성상태
    activate = models.BooleanField(default=False)    
    #아티스트 등급, 적립금
    level = models.CharField(choices=LEVELS, default='B', max_length=10)
    credit = models.IntegerField(help_text = "원앤온리 적립금", default=0)


    #form
    K_name = models.CharField(max_length=15)
    E_name = models.CharField(max_length=15)
    avatar = models.ImageField(upload_to='artist/images/', help_text = "50x50 사이즈 작은 프로필이미지", default='default.png', blank=True)
    bio_image = models.ImageField(upload_to='artist/images/', help_text = "큰 프로필이미지", blank=True, null=True)
    bio_video = models.FileField(upload_to = 'artist/videos/', blank=True)
    bio_text = models.CharField(max_length = 300)
    instrument = models.CharField(choices=INSTRUMENTS, max_length=3)
    price = models.IntegerField(default=100000)
    discount_price = models.IntegerField(default=None, null=True, blank=True)
    lesson_price = models.IntegerField(default=200000)
    lesson_discount_price = models.IntegerField(default=None, null=True, blank=True)
    # account_verify1 = models.ImageField(upload_to='artist/images/', help_text = "통장 사본")
    # account_verify2 = models.ImageField(upload_to='artist/images/', help_text = "신분증 사본")
    # account_bank = models.CharField(chocies=ACCOUNTS, max_length=10, null=True) 
    # account_host = models.CharField(max_length=10, null=True)
    # account_num = models.IntegerField(null=True)

    #auto
    start_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-pk"]
        verbose_name = 'Artist'
        verbose_name_plural = 'Artists'

    def __str__(self):
        return self.E_name.upper()

    # def get_name(self):
    #     name = self.first_name + self.last_name
    #     return name.upper()

    def get_artist_url(self):
        return reverse("core:detail_artist", kwargs={'pk':self.pk})
        
    def get_artist_score(self):
        if self.review.all():
            score = 0
            reviews = self.review.all()
            for i in reviews:
                score += i.score
            return round(float(score/reviews.count()), 1)
        else:
            pass
    def get_artist_like(self):
        return self.artist_like.all().count()

    def average_score(self):
        if Reviews.objects.all():
            total_score = 0
            for i in Reviews.objects.all():
                total_score += i.score
            return round(float(total_score/Reviews.objects.all().count()),1)
        else :
            pass

#Artist Profile---
class ArtistProfiles(models.Model):
    artist = models.OneToOneField(Artists, on_delete=models.CASCADE)
    # 부가정보
    class Meta:
        verbose_name = 'ArtistProfile'
        verbose_name_plural = 'ArtistProfiles' 
        
    def __str__(self):
        value = self.artist + "아티스트 프로필"
        return value
   


class Reviews(models.Model):
    user = models.ForeignKey("user.Users", on_delete=models.CASCADE, blank=True)
    artist = models.ForeignKey(Artists, on_delete=models.CASCADE, related_name="review", blank=True)
    score = models.IntegerField(choices=SCORE, default=1)
    text = models.CharField(max_length=100)
    start_date = models.DateTimeField(auto_now_add=True)
        
    class Meta:
        ordering = ["-pk"]
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'         

def ArtistProfile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        artistprofile = ArtistProfiles.objects.create(artist=instance, pk=instance.pk)        

post_save.connect(ArtistProfile_receiver, sender=Artists)

@receiver(pre_delete, sender = "user.Users")
def Artist_delete(sender, instance, **kwargs):
    artist = Artists.objects.filter(user=instance).first()
    if artist:
        artist.delete()
# @receiver(post_save, sender = Artists)
# def Artist_update(sender, instance, created, *args, **kwargs):
#     if created:
#         instance.pk=instance.user.pk
#         instance.save()