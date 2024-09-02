from typing import Any
from django.db.models.query import QuerySet
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from auction.decorators import authorization_required
from auction.forms import Admin_PlacementForm, Admin_PlacementForm_Crowd
from core.decorators import Admin_Authorization_Required_Mixin
from core.models import Articles
from .models import AuctionAuthorization, AuctionNftToken, Donation, Placement, PlacementBid, AuctionArtist, AutoBid, TimeStoreItem
from user.models import Users
from core.models import CrowdFundingOrderItem
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from user.decorators import Phone_Exist_Required, Phone_Verified_Required, Phone_Verified_Required_Mixin, Phone_Exist_Required_Mixin
from core.tasks import AdminPhone_SMS_Send, Biz_KAKAO_Send, Phone_SMS_Send
from django.db.models.signals import post_save
from django.views.generic import ListView, DetailView, View, TemplateView
from django.views.generic.edit import FormMixin, FormView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
import datetime, json
from django.db.models import F,Q

'''
TIMESTORE
'''
class TimeStoreListView(ListView):
    model = TimeStoreItem
    paginate_by = 12
    template_name = 'auction/timestore/list.html'
    context_object_name = 'items'
    # queryset = Placement.objects.filter(placement_order__gt=1)
    paginate_orphans = 3

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cols'] = self.get_queryset().exclude(is_col = True)
        context['non_cols'] = self.get_queryset().exclude(is_col = False)        
        return context

class TimeStoreDetailView(DetailView):
    model = TimeStoreItem
    template_name = 'auction/timestore/detail.html'    
    context_object_name = "item"

    def get_context_data(self, **kwargs):
        object = self.get_object()
        pk=self.kwargs['pk']
        context = super().get_context_data(**kwargs)
        context['placement'] = object.placement
        return context
    
'''
Display(파트너스)
'''
class DisplayListView(ListView):
    model = Articles
    paginate_by = 8
    template_name = 'auction/display/list.html'
    context_object_name = 'items'
    # queryset = Placement.objects.filter(id__in=[22,29])
    paginate_orphans = 2
    def get_queryset(self):
        dtype = self.request.GET.get('type')
        if dtype is not None:
            if dtype=='a':
                return Articles.objects.filter(category=5).order_by('-display_day')
            else:
                return Articles.objects.none()
        else:
            self.context_object_name = 'onenonly_items'
            return Placement.objects.filter(id__in=[22,29])            

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['cols'] = self.get_queryset().exclude(is_col = True)
    #     context['non_cols'] = self.get_queryset().exclude(is_col = False)        
    #     return context

# class DisplayDetailView(DetailView):
#     model = TimeStoreItem
#     template_name = 'auction/display/detail.html'
#     context_object_name = "item"

#     def get_context_data(self, **kwargs):
#         object = self.get_object()
#         pk=self.kwargs['pk']
#         context = super().get_context_data(**kwargs)
#         context['placement'] = object.placement
#         return context    

"""
Auction Home & Artist, Placement List
"""
class AuctionArtistListView(ListView):
    model = AuctionArtist
    paginate_by = 12
    template_name = 'auction/home.html'
    context_object_name = "auctionartists"
    paginate_orphans = 3
    #form_class = LForm

    def get_context_data(self, **kwargs):
        context = super(AuctionArtistListView, self).get_context_data(**kwargs)
        placements=Placement.objects.all().exclude(placement_order=0)
        context['placements']=placements
        context['slugs']=[s['placement_artist__slug'] for s in placements.values('placement_artist__slug')]
        return context

class AuctionArtistDetailView(DetailView):
    model = AuctionArtist
    context_object_name = "auctionartists"
    def get_template_names(self):
        templates_list=super().get_template_names()
        templates_list.insert(0,f"article/auction/portfolio/index_{self.kwargs['slug']}.html")
        return templates_list

    # #Pagination
    # def get_context_data(self, **kwargs):
    #     article = super().get_object()
    #     article_comment = Article_Comments.objects.filter(article=article)
    #     context = super(ArticleDetailView, self).get_context_data(**kwargs)
    #     context['article_commentlist'] = article_comment
    #     return context
    #     # try:
    #     #     post_list = artist.user.post.all()
    #     #     review_list = artist.review.all()
    #     #     post_paginator = Paginator(post_list, 6)
    #     #     post_paginator.orphans=3
    #     #     review_paginator = Paginator(review_list, 6)
    #     #     review_paginator.orphans=3
    #     #     post_page = self.request.GET.get('post_page' ,'1') 
    #     #     review_page =  self.request.GET.get('review_page', '1')
    #     #     posts = post_paginator.get_page(post_page)
    #     #     reviews = review_paginator.get_page(review_page)
    #     #     context['posts'] = posts
    #     #     context['reviews'] = reviews
    #     #     context['review_list'] = review_list
    #     #     return context

    #     # except:
    #     #     messages.info(self.request, "Pagination error occurred")
    #     #     return context
    # def post(self, request, *args, **kwargs):
    #     article = super().get_object()
    #     form = Article_comment_Form(request.POST or None)
    #     #채워넣는 logic    
    #     if form.is_valid():
    #         form = form.save(commit=False)
    #         form.user = request.user
    #         form.article = article
    #         form.save()
    #     else:
    #         messages.info(request, "Article_comment_Form Error occurred")

    #     self.object = self.get_object()
    #     context = self.get_context_data(**kwargs)
    #     return self.render_to_response(context=context)

class PlacementListView(ListView):
    model = Placement
    paginate_by = 12
    template_name = 'auction/unboxing/ub_list.html'
    context_object_name = 'placements'
    queryset = Placement.objects.filter(placement_order__gt=1).order_by('placement_start')
    paginate_orphans = 3

    def get_queryset(self):
        _type=self.request.GET.get('type')
        _search=self.request.GET.get('search')
        if _type is not None:
            if _type == 'c':
                return Placement.objects.filter(placement_order__gt=1, placement_type='crowdfunding').exclude(placement_price=F('unit_price')).order_by('placement_start')
            elif _type == 'c1':
                return Placement.objects.filter(placement_order__gt=1, placement_type='crowdfunding', placement_price=F('unit_price')).order_by('placement_start')
            elif _type == 's':
                return Placement.objects.filter(placement_order__gt=1, placement_type='secretfunding').order_by('placement_start')
        if _search is not None:
            filter_args = Q()
            filter_args |= Q(title__icontains = _search)
            filter_args |= Q(description__icontains = _search)
            return Placement.objects.filter(*(filter_args,))
        return Placement.objects.filter(placement_order__gt=1).order_by('placement_start')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['slugs']=[s['placement_artist__slug'] for s in self.queryset.values('placement_artist__slug')]
        _type=self.request.GET.get('type')
        if _type == 'c':
            context['cs_placements'] = Placement.objects.filter(placement_order=1, placement_type='crowdfunding').exclude(placement_price=F('unit_price')).order_by('placement_start')
            context['finish_placements'] = Placement.objects.filter(placement_order__lt=0, placement_type='crowdfunding').exclude(placement_price=F('unit_price')).order_by('placement_start')
        elif _type == 'c1':
            context['cs_placements'] = Placement.objects.filter(placement_order=1, placement_type='crowdfunding',placement_price=F('unit_price')).order_by('placement_start')
            context['finish_placements'] = Placement.objects.filter(placement_order__lt=0, placement_type='crowdfunding',placement_price=F('unit_price')).order_by('placement_start')
        elif _type == 's':
            context['cs_placements'] = Placement.objects.filter(placement_order=1, placement_type='secretfunding').order_by('placement_start')
            context['finish_placements'] = Placement.objects.filter(placement_order__lt=0, placement_type='secretfunding').order_by('placement_start')
        else:
            context['cs_placements'] = Placement.objects.filter(placement_order=1).order_by('placement_start')
            context['finish_placements'] = Placement.objects.filter(placement_order__lt=0).order_by('placement_start')
        # 내가 참여한 Placement 목록
        # if self.request.user.is_authenticated:
        #     try:
        #         p_list=[]
        #         pbds=PlacementBid.objects.filter(user_id=self.request.user.id).select_related('placement')
        #         for pbd in pbds:
        #             if pbd.placement.id not in p_list:
        #                 p_list.append(pbd.placement.id)
        #         my_placement=Placement.objects.filter(id__in=p_list)
        #         context['my_placement']=my_placement
        #     except:
        #         pass
        return context

class PlacementDetailView(DetailView):
    model = Placement
    context_object_name = "placement"
    def dispatch(self, request, *args, **kwargs):
        object=self.get_object()
        #예정 & 숨김
        if object.placement_order == 0 or object.placement_order ==1:
            if request.user.is_authenticated:
                if self.request.user.is_staff or self.request.user == object.placement_artist.user:
                    pass
                else:
                    messages.error(self.request, '진행중인 상품이 아닙니다. 접속을 위해서 스태프 권한이 필요합니다.')
                    return redirect('auction:plv')
            else:
                messages.error(self.request, '진행중인 상품이 아닙니다. 접속을 위해서 스태프 권한이 필요합니다.')
                return redirect('auction:plv')
        #진행중 & 종료
        else:
            pass
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        object = self.get_object()
        pk=self.kwargs['pk']
        context = super().get_context_data(**kwargs)

        #예정 + 진행중
        context['others'] = Placement.objects.filter(placement_order__gt=1).exclude(id=pk).order_by('placement_start')

        #크라우드펀딩
        if object.placement_type == 'crowdfunding': 
            # context['donations'] = Donation.objects.filter(orderitem__order__ordered=True)
            pass

        #시크릿, 오픈 펀딩
        else:
            #시크릿 펀딩
            if object.placement_type == 'secretfunding':
                pass

            #오픈 펀딩
            else:
                pass
        return context

    def get_template_names(self):
        templates_list=super().get_template_names()
        object = self.get_object()
        templates_list.insert(0,f"auction/unboxing/ub_{object.placement_type}.html")
        return templates_list
class BiddingDetailView(Phone_Verified_Required_Mixin, DetailView):
    http_method_names = ['get', 'post']
    model = Placement
    context_object_name = "placement"

    def dispatch(self, request, *args, **kwargs):
        try:
            object=self.get_object()
            #(예정 or 가림) and (STAFF X and ARTIST X 일때)
            if (object.placement_order == 1 or object.placement_order==0) and not(self.request.user.is_staff or self.request.user == object.placement_artist.user):
                messages.error(self.request, '공개중인 상품이 아닙니다. 접속을 위해서 스태프 권한이 필요합니다.')
                return redirect('auction:plv')
            else:
                return super().dispatch(request, *args, **kwargs)
        except:
            messages.error(self.request, '[에러코드:1] 에러가 발생하였습니다.')
            return redirect('auction:plv')

    def get_template_names(self):
        templates_list=super().get_template_names()
        object = self.get_object()
        templates_list.insert(0,f"auction/unboxing/ub_bidding_{object.placement_type}.html")
        return templates_list

    def get_context_data(self, **kwargs):
        try:
            object = self.get_object()
            pk=self.kwargs['pk']
            context = super().get_context_data(**kwargs)

            #크라우드펀딩
            if object.placement_type == 'crowdfunding': 
                # context['donations'] = Donation.objects.filter(orderitem__order__ordered=True)
                pass

            #오픈 펀딩
            elif object.placement_type == 'openfunding':
                my_autobid = AutoBid.objects.filter(user=self.request.user, placement__id=pk).first()
                pbd=PlacementBid.objects.filter(user=self.request.user, placement=pk)
                all_pbd=PlacementBid.objects.filter(placement=pk).order_by('-offer','-id')
                max_autobid = AutoBid.objects.filter(placement=pk)
                context['my_autobid']=my_autobid
                context['pbd'] = pbd
                context['all_pbd'] = all_pbd
                context['max_autobid'] = max_autobid
            #시크릿 펀딩
            elif object.placement_type == 'secretfunding':
                context['pbd'] = PlacementBid.objects.filter(user=self.request.user, placement=object).first()

            return context
        except:
            messages.error(self.request, '[에러코드:2] 에러가 발생하였습니다.')
            return redirect('auction:plv')


    # #Pagination
    # def get_context_data(self, **kwargs):
    #     article = super().get_object()
    #     article_comment = Article_Comments.objects.filter(article=article)
    #     context = super(ArticleDetailView, self).get_context_data(**kwargs)
    #     context['article_commentlist'] = article_comment
    #     return context
    #     # try:
    #     #     post_list = artist.user.post.all()
    #     #     review_list = artist.review.all()
    #     #     post_paginator = Paginator(post_list, 6)
    #     #     post_paginator.orphans=3
    #     #     review_paginator = Paginator(review_list, 6)
    #     #     review_paginator.orphans=3
    #     #     post_page = self.request.GET.get('post_page' ,'1') 
    #     #     review_page =  self.request.GET.get('review_page', '1')
    #     #     posts = post_paginator.get_page(post_page)
    #     #     reviews = review_paginator.get_page(review_page)
    #     #     context['posts'] = posts
    #     #     context['reviews'] = reviews
    #     #     context['review_list'] = review_list
    #     #     return context

    #     # except:
    #     #     messages.info(self.request, "Pagination error occurred")
    #     #     return context
    # def post(self, request, *args, **kwargs):
    #     article = super().get_object()
    #     form = Article_comment_Form(request.POST or None)
    #     #채워넣는 logic    
    #     if form.is_valid():
    #         form = form.save(commit=False)
    #         form.user = request.user
    #         form.article = article
    #         form.save()
    #     else:
    #         messages.info(request, "Article_comment_Form Error occurred")

    #     self.object = self.get_object()
    #     context = self.get_context_data(**kwargs)
    #     return self.render_to_response(context=context)
    #         
    # def get_template_names(self):
    #     templates_list=super().get_template_names()
    #     templates_list.insert(0,f"article/auction/portfolio/index_{self.kwargs['slug']}.html")
    #     return templates_list
#Key concept:offer=다음 비교할값, autobid는 created 오름차순배열이라 비교이후 offer을 올리면 코드 효율 높아짐
#@authorization_required
class AdminPlacementDetailView(Admin_Authorization_Required_Mixin, UpdateView):
    model = Placement
    context_object_name = "placement"
    success_message = "상품이 수정되었습니다."
    def get_form_class(self):
        object = self.get_object()
        if object.placement_type =='crowdfunding':
            return Admin_PlacementForm_Crowd
        else:
            return Admin_PlacementForm

    # def form_valid(self, form):
    #     print(form.cleaned_data.get('is_encore'), '-1')
    #     print(form.cleaned_data.get('placement_start'), '0')
    #     print(self.request.POST.get('is_encore'), '1')
    #     print(self.request.POST.get('placement_start'), '2')
    #     if form.is_valid():
    #         instance = form.save(commit=False)
    #         print(instance.is_encore, instance.placement_start)
    #         # cleaned_data=form.cleaned_data
    #         # instance.placement_start=cleaned_data.get('placement_start')
    #         # instance.placement_end=cleaned_data.get('placement_end')
    #         # instance.save()
    #     return super().form_valid(form)

    # def post(self, request, **kwargs):
    #     # request.POST = request.POST.copy()
    #     print("post override")
    #     print(request.FILES.items())
    #     for filename, file in request.FILES.items():
    #         print(filename, file, file.name, file.content_type, file.size)
    #     return super().post(request, **kwargs)
    # def dispatch(self, request, *args, **kwargs):
    #     placement = self.get_object()
    #     if placement.placement_type == 'crowdfunding':
    #         self.fields = [
    #             # "title",
    #             # "description",
    #             # "category",
    #             # "duration",
    #             # "d_day",
    #             # "d_place",
    #             # "thumbnail",
    #             # "m_banner_video_mp4",
    #             # "pc_banner_video_mp4",

    #             "youtube_id",
    #             "image_1",
    #             "image_2",
    #             "image_3",
    #             "image_4",
    #             # "detail_1_title",
    #             # "detail_1",
    #             # "detail_2_title",
    #             # "detail_2",
    #             # "detail_3_title",
    #             # "detail_3",
    #             # "detail_4_title",
    #             # "detail_4",
    #             # "detail_5_title",
    #             # "detail_5",
    #             # "detail_6_title",
    #             # "detail_6",                
    #             "etc_1",
    #             "placement_type",
    #             "placement_price",

    #             # "placement_start",
    #             # "placement_end",
    #             # "is_encore",

    #             # "unit_price"
    #         ]

    #     else:
    #         self.fields = [
    #             "title",
    #             "description",
    #             "category",
    #             "duration",
    #             "d_day",
    #             "d_place",
    #             "thumbnail",
    #             "m_banner_video_mp4",
    #             "pc_banner_video_mp4",
    #             "youtube_id",
    #             "image_1",
    #             "image_2",
    #             "image_3",
    #             "image_4",
    #             "detail_1_title",
    #             "detail_1",
    #             "detail_2_title",
    #             "detail_2",
    #             "detail_3_title",
    #             "detail_3",
    #             "detail_4_title",
    #             "detail_4",
    #             "detail_5_title",
    #             "detail_5",
    #             "detail_6_title",
    #             "detail_6",                
    #             "etc_1",
    #             "placement_type",
    #             "placement_price",
    #             "placement_start",
    #             "placement_end",
    #             "is_encore",
    #             "unit_price",
    #             "placement_start_price",
    #             "placement_estimated_price",
    #             "placement_buynow_price",
    #         ]

    #     return super().dispatch(request, *args, **kwargs)
    def get_object(self, queryset = None):
        pk=self.kwargs['pk']
        return Placement.objects.get(pk=pk)

    # def get_form(self, form_class=None):
    #     form = super().get_form(form_class=form_class)
    #     # form.fields["username"].widget.attrs = {"placeholder" : self.request.user.username}
    #     # form.fields["username"].required = True
    #     # form.fields["email"].widget.attrs = {"placeholder" : self.request.user.email }
    #     # form.fields["email"].required = True
    #     return form

    def get_context_data(self, **kwargs):
        object = self.get_object()
        pk=self.kwargs['pk']
        context = super().get_context_data(**kwargs)

        #크라우드펀딩
        if object.placement_type == 'crowdfunding': 
            pass

        #시크릿, 오픈 펀딩
        else:
            #시크릿 펀딩
            if object.placement_type == 'secretfunding':
                pass

            #오픈 펀딩
            else:
                pass
        return context

    def get_template_names(self):
        templates_list=super().get_template_names()
        object = self.get_object()
        templates_list.insert(0,f"auction/unboxing/admin/ub_{object.placement_type}.html")
        return templates_list

@Phone_Exist_Required
def Toggle_Alarm(request):
    try:
        pk = request.POST.get('pk', None)
        placement = Placement.objects.get(pk=pk)        
        if placement in request.user.alarm.all():
            request.user.alarm.remove(placement)
            return JsonResponse({'alarm':'deactivate'})
        else:
            request.user.alarm.add(placement)
            return JsonResponse({'alarm':'activate'})
    except:
            return JsonResponse({'alarm':'error'}, status=404)

@Phone_Exist_Required
def Toggle_Encore(request):
    try:
        pk = request.POST.get('pk', None)
        placement = Placement.objects.get(pk=pk)
        if placement in request.user.encore.all():
            request.user.encore.remove(placement)
            return JsonResponse({'encore':'deactivate'})        
        else:
            request.user.encore.add(placement)
            return JsonResponse({'encore':'activate'})
    except:
        return JsonResponse({'encore':'error'}, status=404)

@login_required
def Toggle_Plike(request):
    try:
        pk = request.POST.get('pk', None)
        placement = Placement.objects.get(pk=pk)
        if placement in request.user.plike.all():
            request.user.plike.remove(placement)
            return JsonResponse({'plike':'deactivate'})
        else:
            request.user.plike.add(placement)
            return JsonResponse({'plike':'activate'})
    except:
        return JsonResponse({'plike':'error'}, status=404)        


"""
FUDNING UTILS
"""
def OpenAuctionModule(request, pk):
    placement = get_object_or_404(Placement, pk=pk)
    all_pbd=PlacementBid.objects.filter(placement=pk).order_by('-offer','-id')
    max_autobid = AutoBid.objects.filter(placement=pk)
    p_name=placement.placement_artist.name
    #현최고자동응찰금액 산정
    if len(max_autobid) != 0:
        max_autobid = max_autobid.order_by('-limit')[0]

    #자동응찰, 1회응찰
    if request.method == 'POST':

        # 바로구매
        if 'buynow-bid' in request.POST and placement.placement_buynow_price != 0:
            try:
                buynow_pbd, created = PlacementBid.objects.get_or_create(
                    user=request.user,
                    placement=placement,
                    offer=placement.placement_buynow_price,
                )
                # placement.placement_end=datetime.datetime.now()
                placement.placement_win=buynow_pbd
                placement.placement_price=placement.placement_buynow_price
                placement.save()
                messages.info(request,"바로구매가 완료되어 옥션이 종료되었습니다. 낙찰정보는 '낙찰 확인하기' 페이지에서 확인 가능합니다. 감사합니다")
                return redirect('auction:pdv', placement.pk)

            except:
                if created:
                    messages.info(request,'바로구매는 등록되었으나 오류가 발생했습니다')
                    return redirect('auction:pdv', placement.pk)
                else:
                    messages.info(request,'바로구매중 오류가 발생했습니다.')
                    return redirect('auction:pdv', placement.pk)

            
        # 자동응찰
        elif 'auto-bid' in request.POST:
            submitted_limit = int(request.POST.get("limit", None).replace(',',''))
            # if submitted_limit % placement.unit_price != 0: #호가단위 검사
            #     tmp = format(placement.unit_price, ',')
            #     messages.info(request,f'호가 단위에 맞는 금액을 넣어주십시오. 호가 단위는 {tmp}원 입니다')
            #     return redirect('auction:placement-detail', placement.pk)
            if submitted_limit >= placement.placement_price+placement.unit_price:
                #update or create autobid                                                        
                try:
                    autobidObject, created = AutoBid.objects.update_or_create(
                    user=request.user,
                    placement=placement,
                    defaults={"limit": submitted_limit}
                    )
                    #당장 비교할값은 다음 step 가격이기 때문에
                    offer=placement.placement_price + placement.unit_price

                    #문자보내기
                    n = format(submitted_limit, ',')
                    if created:
                        content=f'[원앤온리] {request.user.username}님\n[자동응찰 등록]\n[{p_name}]님 경매품\n자동응찰가 {n}원'
                        #응찰시각 {datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")}
                    else:
                        content=f'[원앤온리] {request.user.username}님\n[자동응찰가 변경]\n[{p_name}]님 경매품\n자동응찰가 {n}원'
                    try:
                        phone=request.user.verification.standardize_phone()
                        Phone_SMS_Send.apply_async( args=[phone, content], ignore_result=False)
                    except:
                        pass
                        # messages.info(request,'알림메시지 발송에 실패하였습니다')
                except:
                    messages.info(request,'자동응찰 에러')
                    return redirect('auction:placement-detail', placement.pk)
            else:
                messages.info(request,'상대방 응찰로 현재가가 변경되었습니다. 더 높은 금액으로 시도해주십시오')
                return redirect('auction:placement-detail', placement.pk)
        # 1회응찰
        elif 'one-bid' in request.POST:
            submitted_amount = int(request.POST.get("amount", None).replace(',',''))
            # if submitted_amount % placement.unit_price != 0: #호가단위 검사
            #     tmp = format(placement.unit_price, ',')
            #     messages.info(request,f'호가 단위에 맞는 금액을 넣어주십시오. 호가 단위는 {tmp}원 입니다')
            #     return redirect('auction:placement-detail', placement.pk)            
            if submitted_amount >= placement.placement_price+placement.unit_price:                        
                placement_bid, created = PlacementBid.objects.get_or_create(user=request.user, 
                                                                    placement=placement, 
                                                                    offer=submitted_amount)
                offer = submitted_amount
                if created:
                    #문자보내기
                    n = format(submitted_amount, ',')
                    content=f'[원앤온리] {request.user.username}님\n[1회 응찰]\n[{p_name}]님 경매품\n1회 응찰가 {n}원'
                    try:
                        phone=request.user.verification.standardize_phone()
                        Phone_SMS_Send.apply_async( args=[phone, content], ignore_result=False)
                    except:
                        # messages.info(request,'알림메시지 발송에 실패하였습니다')
                        pass
            else:
                messages.info(request,'더 높은 금액으로 시도해주십시오')
                return redirect('auction:placement-detail', placement.pk)
        else:
                messages.error(request,'잘못된 요청입니다')
                return redirect('auction:placement-detail', placement.pk)
        # 자동응찰기 동작 offer=당장 비교할값, placement_bid=첫째 응찰객체
        autobids = AutoBid.objects.filter(placement=placement, limit__gte=offer)
        placement_bid = all_pbd.first()
        bulk_create_list=[]
        again=True
        while again == True:
            again=False
            for a in autobids:
                print(f'a.limit:{a.limit}, offer:{offer}')
                if a.limit >= offer:
                    if placement_bid is None: #init(자동응찰)
                        placement_bid=PlacementBid(user=a.user, 
                                    placement=placement,
                                    offer=placement.placement_price,
                                    is_autobid = True,
                                    )
                        bulk_create_list.append(placement_bid)
                        offer=offer+placement.unit_price
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
                                offer=offer+placement.unit_price
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
                                offer=offer+placement.unit_price
                                print("append", placement_bid, "1회 응찰 대항", bulk_create_list)                                                                        
                            elif a.limit > placement_bid.offer:
                                placement_bid = PlacementBid(user=a.user, 
                                        placement=placement,
                                        offer=offer,
                                        is_autobid = True,
                                        )
                                bulk_create_list.append(placement_bid)
                                offer=offer+placement.unit_price
                                print("append", placement_bid, "1회 응찰 대항, 더 클때", bulk_create_list)
            tmp=offer #offer변화감지
            if len(autobids) != 1:
                for a in autobids:
                    #한번 더 돌지 결정
                    if a.limit >= offer and a.limit >= placement_bid.offer:
                        again=True

                    #AUTOBID 우선순위 선별과정
                    # print(a.limit, placement_bid.offer, a.user, placement_bid.user)
                    # print("선별과정", a, placement_bid)
                    # print("한번보자", a.limit, placement_bid.offer, a.user, placement_bid.user)
                    if a.limit >= placement_bid.offer and a.user != placement_bid.user:
                        try: 
                            #자동응찰 vs 자동응찰
                            if placement_bid.is_autobid == True:
                                # print(AutoBid.objects.get(user=placement_bid.user).created, a.created, (AutoBid.objects.get(user=placement_bid.user).created > a.created))
                                atb=AutoBid.objects.get(placement=placement, user=placement_bid.user)
                                # print("here!", atb, a.limit, atb.limit)
                                if atb.created > a.created and a.limit >= atb.limit:
                                    placement_bid = PlacementBid(user=a.user, 
                                                                placement=placement,
                                                                offer=placement_bid.offer,
                                                                is_autobid = True,
                                                                is_superior = True,
                                                                )
                                    offer=offer+placement.unit_price
                                    # print("자동응찰 vs 자동응찰 우선선별", placement_bid)
                                # elif placement_bid.created > a.created:
                                #     placement_bid.user=a.user
                                #     placement_bid.save()
                                #     print("자동응찰 vs 1회응찰 우선선별", placement_bid)
                            else: #1회응찰 vs 자동응찰
                                if placement_bid.created > a.created:
                                    placement_bid = PlacementBid(user=a.user, 
                                                                 placement=placement,
                                                                offer=placement_bid.offer,
                                                                is_autobid = True,
                                                                is_superior = True,
                                                                )
                                    offer=offer+placement.unit_price
                                    # print("1회 응찰 vs 자동응찰 우선선별", placement_bid)
                        except:
                            pass
                if offer > tmp:
                    bulk_create_list.append(placement_bid)
        
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
                phone=u.verification.standardize_phone()
                Phone_SMS_Send.apply_async( args=[phone, content], ignore_result=False)

                    # messages.info(request,'알림메시지 발송에 실패하였습니다')            
        return redirect('auction:placement-detail', placement.pk)            

    elif request.method == 'GET':
        pass

    #INVALID REQUEST
    else:
        messages.error(request,'잘못된 요청입니다')
        return redirect('auction:pdv', pk)

def SecretAuctionModule(request, pk):
    placement = get_object_or_404(Placement, pk=pk)
    if request.method == 'POST':
        #시크릿 바로구매
        if 'buynow-bid' in request.POST and placement.placement_buynow_price != 0 and placement.placement_win==None:
            #응찰객체 만들기
            buynow_pbd, created = PlacementBid.objects.get_or_create(
                user=request.user,
                placement=placement,
                offer=placement.placement_buynow_price,
            )

            #Placement 값 변경
            placement.placement_win=buynow_pbd
            placement.placement_price=placement.placement_buynow_price
            placement.save()

            return redirect('core:AddAuctionToOrderItem', buynow_pbd.id, placement.id)
        #시크릿 응찰
        elif 'secret-bid' in request.POST:
            submitted_amount = int(request.POST.get("secret-bid", None).replace(',',''))
            # if submitted_amount % placement.unit_price != 0: #호가단위 검사
            #     tmp = format(placement.unit_price, ',')
            #     messages.info(request,f'호가 단위에 맞는 금액을 넣어주십시오. 호가 단위는 {tmp}원 입니다')
            #     return redirect('auction:placement-detail', placement.pk)
            if submitted_amount >= 2**31-1:
                messages.error(request,'적정한 금액을 입력해주십시오')
                return redirect('auction:bidding', placement.pk)
            elif submitted_amount >= placement.placement_start_price:
                placement_bid, created = PlacementBid.objects.update_or_create(
                                                                        user=request.user, 
                                                                        placement=placement,
                                                                        defaults={'offer':submitted_amount}
                                                                    )
                offer = submitted_amount
                if created:
                    messages.success(request, "시크릿 옥션 응찰이 완료되었습니다")
                else:
                    messages.success(request, "시크릿 옥션 응찰 변경이 완료되었습니다.")
                #카카오 메시지 v2_secret_bid_0
                #관리자 메시지
                phones_params=[]
                phone=request.user.verification.standardize_phone()
                params={
                    'USERNAME':request.user.username,
                    'TITLE':placement.title,
                    'PRICE':submitted_amount,
                }
                phones_params.append({phone:params})
                tmpltCode='v2_secret_bid_0'
                Biz_KAKAO_Send.apply_async(kwargs={'phones_params':phones_params, 'tmpltCode':tmpltCode}, ignore_result=False)
                AdminPhone_SMS_Send.apply_async(args=[f"경쟁구매 입찰\n유저:{request.user.username}\n상품:{placement.title[:5]+'...'}\n가격:{format(int(submitted_amount),',')}"], ignore_result=False)
                return
            else:
                messages.info(request,'더 높은 금액으로 시도해주십시오')
                return redirect('auction:bidding', placement.pk)
        else:
                messages.error(request,'잘못된 요청입니다')
                return redirect('auction:bidding', placement.pk)          

    elif request.method == 'GET':
        pass

    #INVALID REQUEST
    else:
        messages.error(request,'잘못된 요청입니다')
        return redirect('auction:pdv', pk)



@Phone_Verified_Required
def BiddingView(request, pk):
    placement = get_object_or_404(Placement, pk=pk)
    try:
        if request.method == 'GET':
            messages.error(request, "허용되지 않는 요청입니다.")
            return redirect('auction:pdv', pk)

        elif request.method == 'POST':
            if placement.placement_type == 'openfunding':
                OpenAuctionModule(request, pk)
            elif placement.placement_type == 'secretfunding':
                SecretAuctionModule(request, pk)
            else:
                messages.error(request, f"{placement.get_type_display()}입니다. 오픈,경쟁구매 요청만 가능합니다.")
                return redirect('auction:pdv', pk)
            return redirect('auction:pdv', pk)                
    except:
        messages.error(request, "구매 진행중 에러가 발생했습니다.")
        return redirect('auction:pdv', pk)

@Phone_Verified_Required
def CrowdFundingStart(request, pk):
    placement=Placement.objects.get(id=pk)    
    if request.method == 'POST':    
        try:
            if not placement.is_crowdfunding_finish():
                cwd_n=int(request.POST.get('cwd_n', None))            

                #인당 최대 누적구매 개수
                c_ois=CrowdFundingOrderItem.objects.filter(
                    user=request.user,
                    placement=placement,
                    expired=False,
                ).values_list('quantity', flat=True)
                num=0
                for quantity in c_ois:
                    num+=quantity
                if num+cwd_n>placement.buy_limit:
                    messages.info(request,f"1인당 최대 구매가능 티켓은 {placement.buy_limit}장 입니다. {request.user.username}님 구매이력 {num}장이 확인되었습니다.")
                    return redirect('auction:pdv', placement.pk)

                if cwd_n is None:
                    messages.info(request,'최대 티켓개수가 입력되지 않았습니다')
                    return redirect('auction:pdv', placement.pk)
                elif cwd_n < 1:
                    messages.info(request,'최소 티켓개수는 1개입니다.')
                    return redirect('auction:pdv', placement.pk)
                elif cwd_n > 30:
                    messages.info(request,'최대 티켓개수는 30개입니다.')
                    return redirect('auction:pdv', placement.pk)
                elif cwd_n > placement.get_crowdfunding_available_cnt():
                    messages.info(request,'남은 티켓보다 많은 수의 티켓을 구매할 수 없습니다')
                    return redirect('auction:pdv', placement.pk)
                elif cwd_n <= placement.get_crowdfunding_available_cnt():
                    donation=Donation.objects.create(
                                    user=request.user,
                                    placement=placement,
                                    offer=placement.unit_price,
                                    quantity=cwd_n
                                    )
                    return redirect('core:AddAuctionToOrderItem', donation.pk, pk)
                else:
                    messages.info(request,'올바른 티켓 개수를 입력해주십시오.')
                    return redirect('auction:pdv', placement.pk)
            else:
                messages.info(request,'남은 티켓이 없습니다.')
                return redirect('auction:pdv', placement.pk)
        except:
            messages.info(request,'티켓구매 과정에서 에러가 발생하였습니다. 다시 시도해주세요')
            return redirect('auction:pdv', placement.pk)
    else:
        return redirect('auction:pdv', placement.pk)


def BiddingRefresh(request, pk):
    #is_ajax()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.accepts("application/json"):
        try:
            placement = Placement.objects.get(pk=pk)
            data = json.loads(request.body)
            id = data.get('first_id', None)
            pbds=PlacementBid.objects.filter(placement__id=pk, id__gt=id).order_by('offer','id')
            if pbds.exists():
                context=[]
                for p in pbds:
                    c={}
                    c['user_id']=p.user.id
                    c['username']=str(p.user.username)[0]+'...'
                    c['id']=p.id
                    c['is_superior'] = p.is_superior
                    c['offer']=format(p.offer, ',')

                    D= p.placementbid_created
                    result=D.strftime('%Y년 %m월 %d일 %I:%M %p').replace('AM','오전').replace('PM','오후')
                    c['created']=result

                    c['is_autobid']=p.is_autobid
                    context.append(c)
                    res={
                        'context':context,
                        'res':"success",
                    }
                return JsonResponse(res)
            else:
                return JsonResponse({'res':'fail'})

        except:
            return JsonResponse({'res':'fail'})
    else:
        messages.error(request,'AJAX 요청만 가능합니다')
        return redirect('auction:pdv', pk)





def InvitationToAuctionAuthorization(request, pk):
    if request.method == "POST":
        try:
            body=request.body
            data = json.loads(request.body)
            print(data)
            is_superpass = data.get('is_superpass', None)
        except:
            is_superpass = None
            
        if is_superpass == "True":
            # messages.info(request, f'[VIP멤버쉽]{request.user}님 인증되었습니다.아래 버튼을 눌러 입장하여주십시오')
            request.session['NFT-verify'] = request.user.id
            return HttpResponse('success')
        else:
            try:
                placement=Placement.objects.get(pk=pk)
                code = request.POST.get("code", None)
                if code is not None:
                    try:
                        auth = AuctionAuthorization.objects.get(code=code, placement__id=pk)
                        if auth.user == None:
                            auth.user = request.user
                            auth.is_authorized = True
                            auth.save()
                            request.session['E-verify'] = request.user.id
                            messages.success(request, f'[일반초대]{request.user}님 입장하셨습니다. 옥션에 참가하신걸 환영합니다.')
                            return redirect('auction:placement-detail', pk)
                        elif auth.user != request.user:
                            messages.info(request, "다른 유저의 초대코드입니다. 다른 초대코드으로 시도해주십시오")
                            return redirect('auction:invi-auth', pk)
                        elif auth.user == request.user:
                            messages.info(request, "초대코드 본인 인증완료-디버깅용")
                            request.session['E-verify'] = request.user.id                            
                            return redirect('auction:placement-detail', pk)
                        
                    except ObjectDoesNotExist:
                        messages.info(request, "잘못된 코드입니다. 초대장을 다시 확인해주세요")
                        return redirect('auction:invi-auth', pk)
                    
                else:
                    messages.info(request, "전송 오류가 발생했습니다. 다시 시도해주십시오")
                    return redirect('auction:invi-auth', pk)

            except:
                messages.info(request, "브라우저에 오류가 발생했습니다. 다시 시도해주십시오")
                return redirect('auction:invi-auth', pk)

    else:
        context={'pk':pk}
        try:
            # token_ids=AuctionNftToken.objects.get(placement__id=pk)
            token_ids=AuctionNftToken.objects.all()[0]
            token_list=token_ids.token_id.split(',')
            context['token_list']=token_list

        except:
            pass

        return render(request, "auction/authorization.html", context)

def InvitationToAuctionAuthorization2(request):
    if request.method == "POST":
        try:
            body=request.body
            data = json.loads(request.body)
            is_superpass = data.get('is_superpass', None)
        except:
            is_superpass = None
            
        if is_superpass == "True":
            # messages.info(request, f'[VIP멤버쉽]{request.user}님 인증되었습니다.아래 버튼을 눌러 입장하여주십시오')
            request.session['NFT-verify'] = request.user.id
            return HttpResponse('success')
        else:
            messages.info(request, "브라우저에 오류가 발생했습니다. 다시 시도해주십시오")
            return redirect('auction:invi-auth-2')

    else:
        context={}
        try:
            # token_ids=AuctionNftToken.objects.get(placement__id=pk)
            token_ids=AuctionNftToken.objects.all()[0]
            token_list=token_ids.token_id.split(',')
            context['token_list']=token_list

        except:
            pass

        return render(request, "auction/authorization_NFT.html", context)

"""
응찰요약 dashboard기능 & 응찰확정 기능
"""
# @login_required(redirect_field_name='next')
# def placements(request):
#     all_placements = Placement.objects.all()
#     paginator = Paginator(all_placements, 18)
#     page = request.GET.get('page')
#     placements = paginator.get_page(page)
#     context = {'placements': placements}
#     return render(request, 'auction/placements.html', context)

# @login_required
# def bid_summary(request):

#     bids = PlacementBid.objects.filter(user=request.user)

#     context = {'bids': bids}

#     return render(request, 'auction/bid-summary.html', context)



# @login_required
# def confirm_bids(request):

#     bids_queryset = PlacementBid.objects.filter(user=request.user, confirmed=False)
    
#     if bids_queryset.exists():

#         # First get the order ID
#         bid_id = bids_queryset[0].bid.id

#         # Update PlacementBid Objects confirmed flag
#         for bid in bids_queryset:
#             bid.confirmed = True
#             bid.save()
        
#         # Update the Bid object status
#         bid = Bid.objects.filter(id=bid_id)[0]
#         bid.bid_status = True
#         bid.save()

#     return redirect('auction:bid-summary')


# @login_required
# def dashboard(request):
    
#     # Get tile data
#     total_companies = AuctionArtist.objects.count()
#     total_users = Users.objects.count()
#     total_placements = Placement.objects.count()
#     total_offers = PlacementBid.objects.aggregate(Sum('offer'))['offer__sum']
#     total_offers_k = total_offers // 1000
    
#     # Get aggregate data
#     top_5 = PlacementBid.objects\
#                     .values('placement__placement_artist__name', 'offer')\
#                     .annotate(Sum('offer'))\
#                     .order_by('-offer')[:5]

#     top_5_offer_names = [item['placement__placement_artist__name'] for item in top_5]
#     top_5_offer_names = [name[:8] + '...' for name in top_5_offer_names]
#     top_5_offer_values = [item['offer'] for item in top_5]

#     # Store context
#     context = {'total_companies':total_companies,
#                 'total_users':total_users,
#                 'total_placements':total_placements,
#                 'total_offers':total_offers_k,
#                 'top_5_offer_names':top_5_offer_names,
#                 'top_5_offer_values':top_5_offer_values}

#     return render(request, 'auction/dashboard.html', context)
