import json, os, requests
from typing import Any
from django.db.models.query import QuerySet
from django.forms.forms import Form
from django.views.decorators.csrf import requires_csrf_token
from django.urls.base import reverse_lazy
from parse import *
from urllib import parse as _parse
from django.conf import settings
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.utils import timezone
from django.views.generic import ListView, DetailView, View, TemplateView
from django.views.generic.edit import FormMixin, FormView, CreateView, UpdateView, DeleteView
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from datetime import datetime, timedelta, date
from django.db.models import Q
from auction.decorators import authorization_required_2_mixin
from auction.models import Donation, Placement, PlacementBid, PlacementMemory
from core.decorators import Fake_Admin_Authorization_Required_Mixin
from core.models import ElasticInfo, CrowdFundingOrderItem,OpenFundingOrderItem, Partnership, Questionanswer, Questionnaire,SecretFundingOrderItem, Article_Comments, Articles, Payment, Coupon
from core.tasks import AdminPhone_SMS_Send, Before_Make_OrderItem_Expired, Biz_KAKAO_Send, Make_OrderItem_Expired
from core.utils import SeoulToUTC
from user.decorators import Password_Check_Required_Mixin
from user.models import Users, Verification
from .forms import Article_comment_Form, Article_Form, PartnershipForm
from allauth.socialaccount.models import SocialAccount
from decouple import config
from allauth.account.forms import EmailAwarePasswordResetTokenGenerator
from allauth.account.utils import user_pk_to_url_str
from allauth.account.models import EmailAddress
from django_celery_beat.models import PeriodicTask, ClockedSchedule
from django.views.decorators.http import require_http_methods
from .utils import ToUTC, is_mobile
from core.admin import f_crowd_make3_checkmake4, f_secret_open_make2, f_secret_open_make3, f_refund_complete, f_ticket_send
from auction.admin import f_secret_open_make1
from django.views.decorators.csrf import csrf_exempt
class HomeView(ListView):
    model = Articles
    paginate_by = 30
    template_name = 'home.html'
    context_object_name = 'items'
    queryset = Articles.objects.filter(category=5).order_by('-display_day')[:10]
    paginate_orphans = 6

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #종료, 숨김 처리 안보이게        
        placements=Placement.objects.all().exclude(placement_order__lte=0).order_by('placement_start')
        pmemorys = PlacementMemory.objects.all().order_by('placement__placement_start')
        if len(pmemorys) > 10:
            pmemorys=pmemorys[:10]
        homebanner = ElasticInfo.objects.get(tag="HomeBanner")
        context['placements']=placements
        context['pmemorys']=pmemorys
        context['homebanner']=homebanner

        #onenonly_items[원앤온리 다이닝]
        context['onenonly_items']=Placement.objects.filter(id__in=[22,29])
        return context

    # def get(self,request, *args, **kwargs):
    #     #종료, 숨김 처리 안보이게
    #     placements=Placement.objects.all().exclude(placement_order__lte=0).order_by('placement_start')
    #     pmemorys = PlacementMemory.objects.all().order_by('placement__placement_start')
    #     if len(pmemorys) > 10:
    #         pmemorys=pmemorys[:10]
    #     homebanner = ElasticInfo.objects.get(tag="HomeBanner")
    #     context = {
    #         'placements':placements,
    #         'pmemorys':pmemorys,
    #         'homebanner':homebanner,
    #     }
    #     return render(request, "home.html", context)

class FakeHomeView(View):
    def get(self,request, *args, **kwargs):
        return render(request, "article/auction/info/fake_home.html", None)


class AboutTemplateView(TemplateView):
    template_name = "about.html"
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     return context

class GuideTemplateView(TemplateView):
    template_name="article/auction/info/guide.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['p_info']=ElasticInfo.objects.get(tag='guide_pc_info')
        context['m_info']=ElasticInfo.objects.get(tag='guide_m_info')        
        return context
#중복으로 보내기전에 filter 하는 기능 추가
#signup완료됐을때 inviter을 검색해서 reward 넣기기능
#publish했을때 packages 수정본도 같이 보내지는지 확인

class ArticleListView(ListView):
    model = Articles
    paginate_by = 6
    template_name = "article/auction/article_list.html"
    context_object_name = "articles"
    queryset=Articles.objects.exclude(category='5')
    paginate_orphans = 2
    #form_class = LForm

    def get_queryset(self):
        try:
            category = self.request.GET.get('category' ,'0')
            tcu = self.request.GET.get('tcu', None)
            if category != '0':
                if tcu is not None:
                    articles = Articles.objects.filter(Q(user__username__contains=tcu) | Q(title__contains=tcu) | Q(text__contains=tcu) & Q(category=category))
                else :
                    articles = Articles.objects.filter(category=category)
            else :
                articles = Articles.objects.filter(Q(user__username__contains=tcu) | Q(title__contains=tcu) | Q(text__contains=tcu))
        except:
            articles=super().get_queryset()

        return articles.exclude(category='5')

    def get_context_data(self, **kwargs):
        context = super(ArticleListView, self).get_context_data(**kwargs)
        category = self.request.GET.get('category' ,'0')
        context['category']=category
        return context
class ArticleWriteView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Articles
    form_class = Article_Form
    success_url = reverse_lazy("core:article_list")
    template_name= "article/auction/article_write.html"
    success_message = "게시글을 성공적으로 등록되었습니다."

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(ArticleWriteView, self).form_valid(form)

class ArticleUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Articles
    form_class = Article_Form
    success_url = reverse_lazy("core:article_list")
    template_name= "article/auction/article_update.html"    
    context_object_name = 'article'
    success_message = "게시글을 성공적으로 수정되었습니다."


class ArticleDeleteView(LoginRequiredMixin, View):
    http_method_names = ['post']    
    model = Articles
    form_class = Article_Form
    success_url = reverse_lazy("core:article_list")
    def post(self, request, *args, **kwargs):
        pk=kwargs.get('pk')
        object=Articles.objects.get(pk=pk)
        if object.user == request.user.id or request.user.is_staff:
            messages.success(request, '게시글을 성공적으로 삭제하였습니다.')
            object.delete()
        else:
            messages.error(request, '작성자 본인만 삭제할 수 있습니다.')
        return redirect("core:article_list")        


# authorization_required_2_mixin
class ArticleDetailView(DetailView):
    model = Articles
    context_object_name = "article"
    template_name = "article/auction/article_detail.html"
 
    #Pagination
    def get_context_data(self, **kwargs):
        article = super().get_object()
        article_comment = Article_Comments.objects.filter(article=article)
        context = super(ArticleDetailView, self).get_context_data(**kwargs)
        try:
            comment_paginator = Paginator(article_comment, 8)
            comment_paginator.orphans=2
            comment_page =  self.request.GET.get('comment_page', '1')
            comments = comment_paginator.get_page(comment_page)
            context['comments'] = comments
            return context
        except:
            messages.error(self.request, "Pagination error occurred")

        return context
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            article = super().get_object()
            form = Article_comment_Form(request.POST or None)
            #채워넣는 logic
            if form.is_valid():
                form = form.save(commit=False)
                form.user = request.user
                form.article = article
                form.save()
            else:
                messages.info(request, "Article_comment_Form Error occurred")

        else:
            messages.info(request, "로그인이 필요합니다. 로그인 이후 다시 시도해주십시오.")
        self.object = self.get_object()
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context=context)

class PartnershipCreateView(CreateView):
    model = Partnership
    form_class = PartnershipForm
    success_url = reverse_lazy("core:partnership")
    template_name= "partnership.html"

    def form_valid(self, form):
        print(form.instance.name, form.is_valid())
        AdminPhone_SMS_Send.apply_async(args=[f"파트너제안\n이름:{form.instance.name}\n내용:{form.instance.text[:8]}..."], ignore_result=False)        
        return super().form_valid(form)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        yid = ElasticInfo.objects.get(tag="partnerYT")
        context['partnership'] = yid
        return context

    # def form_valid(self, form):
    #     form.instance.user = self.request.user
    #     return super(ArticleWriteView, self).form_valid(form)
class GcommonQuestionnarieView(LoginRequiredMixin,TemplateView):
    template_name = "Gcommon_question.html"    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk=kwargs['pk']
        ei = ElasticInfo.objects.get(tag=f"Gcommon-{pk}")
        context['Gsource']=ei.info
        return context

class QuestionnaireCreateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        slug=self.kwargs['slug']
        pk=self.kwargs['pk']
        if slug=='openfunding':
            oi=OpenFundingOrderItem.objects.get_or_none(pk=pk, user=request.user)
        elif slug=='secretfunding':
            oi=SecretFundingOrderItem.objects.get_or_none(pk=pk, user=request.user)
        elif slug=='crowdfunding':
            oi=CrowdFundingOrderItem.objects.get_or_none(pk=pk, user=request.user)
        else:
            messages.info(request, '잘못된 SLUG 입력값입니다')
            return redirect('core:user')

        if not oi:
            messages.info(request, "주문한 상품에 대해서만 응답할 수 있습니다")
            return redirect('core:user')
        try:
            answer=oi.questionanswer
        except:
            answer=None
        context={
            'orderitem': oi,
            'question':oi.placement.questionnaire,
            'answer':answer,
        }
        return render(request, 'questionnaire.html', context)
    def post(self, request, *args, **kwargs):
        q_pk = int(request.POST.get('q_pk', None))
        q = Questionnaire.objects.get(pk=q_pk)
        name=request.POST.get('name', None)
        job=request.POST.get('job', None)
        sex=request.POST.get('sex', None)
        ph1=request.POST.get('ph1', None)
        ph2=request.POST.get('ph2', None)
        ph3=request.POST.get('ph3', None)
        phone = ph1+ph2+ph3
        birthday_year=request.POST.get('birthday-year', None)
        birthday_month=request.POST.get('birthday-month', None)
        birthday_day=request.POST.get('birthday-day', None)
        birthday = date(int(birthday_year), int(birthday_month), int(birthday_day))

        a1=request.POST.get('a1', None)
        a2=request.POST.get('a2', None)
        a3=request.POST.get('a3', None)
        a4=request.POST.get('a4', None)
        a5=request.POST.get('a5', None)
        a6=request.POST.get('a6', None)
        a7=request.POST.get('a7', None)
        a8=request.POST.get('a8', None)
        a9=request.POST.get('a9', None)
        a10=request.POST.get('a10', None)
        qa, created = Questionanswer.objects.update_or_create(
            questionnaire = q,
            user=request.user,
            defaults={
                'name':name,
                'job':job,
                'sex':sex,
                'phone':phone,
                'birthday':birthday,
                'a1':a1,
                'a2':a2,
                'a3':a3,
                'a4':a4,
                'a5':a5,
                'a6':a6,
                'a7':a7,
                'a8':a8,
                'a9':a9,
                'a10':a10,
            }
        )

        slug=self.kwargs['slug']
        pk=self.kwargs['pk']
        if slug=='openfunding':
            oi=OpenFundingOrderItem.objects.get_or_none(pk=pk)
            qa.of_oi = oi
        elif slug=='secretfunding':
            oi=SecretFundingOrderItem.objects.get_or_none(pk=pk)
            qa.sf_oi = oi
        elif slug=='crowdfunding':
            oi=CrowdFundingOrderItem.objects.get_or_none(pk=pk)
            qa.cf_oi = oi
        else:
            messages.info(request, '답변에 주문상품이 연결되지 않았습니다. 관리자에게 문의 부탁드립니다.')
            return redirect('core:user')

        qa.save()
        if created:
            messages.success(request, '응답이 성공적으로 제출되었습니다.')
        else:
            messages.success(request, '응답이 성공적으로 수정되었습니다.')
        return redirect('core:user')


class QuestionnaireAdminView(View):
    def get(self, request, *args, **kwargs):
        pk=self.kwargs['pk']
        placement = Placement.objects.get(pk=pk)

        #스태프 or 아티스트 본인 검증
        if not(request.user.is_staff or request.user == placement.placement_artist.user):
            messages.info(request,'스태프 혹은 아티스트 본인만 접근 가능합니다')
            return redirect('core:home')

        if placement.placement_type == 'crowdfunding':
            oi_qs = placement.crowdfundingorderitem_set.exclude(questionanswer=None)
        elif placement.placement_type == 'openfunding':
            oi_qs = placement.openfundingorderitem_set.exclude(questionanswer=None)
        elif placement.placement_type == 'secretfunding':
            oi_qs = placement.secretfundingorderitem_set.exclude(questionanswer=None)

        context={
            'oi_qs':oi_qs,
            'question':placement.questionnaire,
        }
        return render(request, 'custom_admin/questionnaire.html', context)

class CommonQuestionnaireCreateView(LoginRequiredMixin,View):
    def get(self, request, *args, **kwargs):
        pk=self.kwargs['pk']
        qna = Questionnaire.objects.get_or_none(pk=pk)
        if qna is not None:
            try:
                answer = Questionanswer.objects.get(user=request.user, questionnaire=qna)
            except:
                answer=None
        context={
            'question':qna,
            'answer':answer,
        }
        return render(request, 'common_questionnaire.html', context)
    def post(self, request, *args, **kwargs):
        pk=self.kwargs['pk']        
        q = Questionnaire.objects.get(pk=pk)
        name=request.POST.get('name', None)
        job = request.POST.get('job', None)
        sex=request.POST.get('sex', None)
        ph1=request.POST.get('ph1', None)
        ph2=request.POST.get('ph2', None)
        ph3=request.POST.get('ph3', None)
        phone = ph1+ph2+ph3
        birthday_year=request.POST.get('birthday-year', None)
        birthday_month=request.POST.get('birthday-month', None)
        birthday_day=request.POST.get('birthday-day', None)
        birthday = date(int(birthday_year), int(birthday_month), int(birthday_day))

        a1=request.POST.get('a1', None)
        a2=request.POST.get('a2', None)
        a3=request.POST.get('a3', None)
        a4=request.POST.get('a4', None)
        a5=request.POST.get('a5', None)
        a6=request.POST.get('a6', None)
        a7=request.POST.get('a7', None)
        a8=request.POST.get('a8', None)
        a9=request.POST.get('a9', None)
        a10=request.POST.get('a10', None)
        qa, created = Questionanswer.objects.update_or_create(
            questionnaire = q,
            user=request.user,
            defaults={
                'name':name,
                'job':job,
                'sex':sex,
                'phone':phone,
                'birthday':birthday,
                'a1':a1,
                'a2':a2,
                'a3':a3,
                'a4':a4,
                'a5':a5,
                'a6':a6,
                'a7':a7,
                'a8':a8,
                'a9':a9,
                'a10':a10,
            }
        )
        if created:
            messages.success(request, '응답이 성공적으로 제출되었습니다.')
        else:
            messages.success(request, '응답이 성공적으로 수정되었습니다.')
        return redirect('core:user')

class CommonQuestionnaireAdminView(View):
    def get(self, request, *args, **kwargs):
        pk=self.kwargs['pk']
        qna = Questionnaire.objects.get_or_none(pk=pk)
        if qna is not None:
            try:
                answers = Questionanswer.objects.filter(questionnaire=qna)
            except:
                answers=None
        #관리자 or 아티스트 본인 검증
        if not (request.user.is_staff):
            messages.info(request,'스태프만 접근 가능합니다')
            return redirect('core:home')

        context={
            'answers':answers,
            'question':qna,
        }
        return render(request, 'custom_admin/common_questionnaire.html', context)

'''
MYPAGE
'''

class MypageUserView(LoginRequiredMixin, TemplateView):
    template_name = "account/mypage/Mypage.html"
    def get_context_data(self, **kwargs):
        context = super(MypageUserView, self).get_context_data(**kwargs)

        #TAB1
        filter_kwargs={}
        filter_kwargs['user']=self.request.user
        deliver_detail = self.request.GET.get("deliver_detail", None)
        if deliver_detail is not None:
            if deliver_detail == 'all':
                context['s_placementbids'] = PlacementBid.objects.filter(user=self.request.user, placement__placement_type='secretfunding').order_by('-created')
                context['o_placementbids'] = PlacementBid.objects.filter(user=self.request.user, placement__placement_type='openfunding').order_by('-created')
            elif deliver_detail == 'expired':
                filter_kwargs["expired"] = True
            else:
                filter_kwargs["deliver_detail"] = int(deliver_detail)
                filter_kwargs["expired"] = False
        else:
            context['s_placementbids'] = PlacementBid.objects.filter(user=self.request.user, placement__placement_type='secretfunding').order_by('-created')
            context['o_placementbids'] = PlacementBid.objects.filter(user=self.request.user, placement__placement_type='openfunding').order_by('-created')
            

        context['s_orderitems'] = SecretFundingOrderItem.objects.filter(**filter_kwargs).order_by('-created')
        context['o_orderitems'] = OpenFundingOrderItem.objects.filter(**filter_kwargs).order_by('-created')
        context['c_orderitems'] = CrowdFundingOrderItem.objects.filter(**filter_kwargs).order_by('-created')

        #TAB2
        context['plikes'] = self.request.user.plike.all()
        context['encores'] = self.request.user.encore.all()
        context['alarms'] = self.request.user.alarm.all()
        return context

class MypageUserInfoUpdateView(LoginRequiredMixin, Password_Check_Required_Mixin, SuccessMessageMixin, TemplateView):
    template_name = "account/mypage/MypageInfo.html"
    http_method_names = ['get', 'post']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['socialaccounts'] = SocialAccount.objects.filter(user=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['socialaccounts'] = SocialAccount.objects.filter(user=self.request.user)
        return render(request,"account/mypage/MypageInfo.html",context)


'''
AUTH
'''
class PhoneVerifyView(View):
    def get(self, request, *args, **kwargs):
        context={
        }
        return render(request, 'account/verify_phone.html', context)
class AuthSignUpView(View):
    def post(self, request, *args, **kwargs):
        data=json.loads(request.body)
        imp_uid=data.get('imp_uid')
        success = data.get('success')

        ###공통###
        if success:
            URL = "https://api.iamport.kr/users/getToken"
            headers={
                "Content-Type": "application/json"
            }
            data={
                'imp_key': config('IMP_KEY'),
                'imp_secret':config('IMP_SECRET'),
            }
            res = requests.post(URL, headers=headers, data=json.dumps(data))
            token = json.loads(res.text)['response']['access_token']

            _URL = f"https://api.iamport.kr/certifications/{imp_uid}"
            _headers={
                "Authorization": token,
            }
            res = requests.get(_URL, headers=_headers)
            info = json.loads(res.text)
            res = info.get('response', None)
        #########

            if res:
                #birthday
                try:
                    birthday_ymd=res.get('birthday').split('-')
                    birthday = date(int(birthday_ymd[0]), int(birthday_ymd[1]), int(birthday_ymd[2]))
                except:
                    birthday = None

                #unique_key
                tmp=res.get('unique_key', None)
                if tmp == '' or tmp == None:
                    return JsonResponse({'msg':'인증고유번호를 받아오지 못했습니다. 다른 인증방법을 이용해 주시거나 하단 챗봇을 통해 문의 부탁드립니다.'}, status=500)

                try:
                    u_vf, created = Verification.objects.update_or_create(
                            unique_key=res.get('unique_key'),
                            defaults={
                                'name':res.get('name'),
                                'phone':res.get('phone'),
                                'birthday':birthday,
                            }
                    )
                #2개 이상
                except:
                    return JsonResponse({'msg':'이미 해당 명의로 계정이 가입되어 있습니다. 해당 계정으로 로그인해주세요.'}, status=500)                    

                #1개
                if not created:
                    if u_vf.user:
                        if EmailAddress.objects.filter(user=u_vf.user, verified=True).exists():
                            #인증 O 계정 O
                            return JsonResponse({'msg':'이미 해당 명의로 계정이 가입되어 있습니다. 해당 계정으로 로그인해주세요.'}, status=500)
                        else:
                            #인증 X 계정 O
                            return JsonResponse({'msg':f"회원가입 진행하셨던 계정({u_vf.user.email})이 존재합니다. 해당 계정으로 로그인해주세요."}, status=500)
                    #인증 O 계정 X
                    else:
                        #Anonymous User Identifier
                        request.session['onenonly_user_unique_key']=res.get('unique_key')
                        return JsonResponse(res, status=200)                        
 
                #인증 X 계정 X
                else:
                    #Anonymous User Identifier
                    request.session['onenonly_user_unique_key']=res.get('unique_key')
                    return JsonResponse(res, status=200)
            else:
                return JsonResponse({'msg':'인증에 실패하였습니다.'}, status=500)
        else:
            return JsonResponse({'msg':'아임포트 서버 오류. 인증에 실패하였습니다.'}, status=500)
class AjaxAuthView(View):
    def post(self, request, *args, **kwargs):
        data=json.loads(request.body)
        imp_uid=data.get('imp_uid')
        success = data.get('success')

        ###공통###
        if success:
            URL = "https://api.iamport.kr/users/getToken"
            headers={
                "Content-Type": "application/json"
            }
            data={
                'imp_key': config('IMP_KEY'),
                'imp_secret':config('IMP_SECRET'),
            }
            res = requests.post(URL, headers=headers, data=json.dumps(data))
            token = json.loads(res.text)['response']['access_token']

            _URL = f"https://api.iamport.kr/certifications/{imp_uid}"
            _headers={
                "Authorization": token,
            }
            res = requests.get(_URL, headers=_headers)
            info = json.loads(res.text)
            res = info.get('response', None)
        #########
            if res:
                #birthday
                try:
                    birthday_ymd=res.get('birthday').split('-')
                    birthday = date(int(birthday_ymd[0]), int(birthday_ymd[1]), int(birthday_ymd[2]))
                except:
                    birthday = None

                #unique_key
                tmp=res.get('unique_key', None)
                if tmp == '' or tmp == None:
                    return JsonResponse({'msg':'인증고유번호를 받아오지 못했습니다. 다른 인증방법을 이용해 주시거나 하단 챗봇을 통해 문의 부탁드립니다.'}, status=500)
                try:
                    u_vf, created = Verification.objects.update_or_create(
                        unique_key = res.get('unique_key'),
                        defaults={
                            'user': request.user,
                            'name': res.get('name'),
                            'phone': res.get('phone'),
                            'birthday': birthday,
                            }
                    )

                    if res.get('phone'):
                        u_vf.last_verified = datetime.now()
                        u_vf.save()
                        request.session['phone_verified_user'] = request.user.id
                        return JsonResponse(res, status=200)

                    else:
                        return JsonResponse({'msg':'핸드폰 번호를 받아오지 못했습니다. 다시 인증을 진행해주시거나 하단 챗봇을 통해 문의 부탁드립니다.'}, status=500)
                #2개 이상
                except Exception as e:
                    return JsonResponse({'msg':'이미 다른 아이디에 인증이 되어있습니다. 동일한 사람이 여러개의 아이디를 인증할 수 없습니다.'}, status=500)                    
            else:
                return JsonResponse({'msg':'서버오류'}, status=500)

        else:
            return JsonResponse({'msg':'아임포트 오류'}, status=500)
class MobileAuthView(View):
    def get(self, request, *args, **kwargs):
        imp_uid=request.GET.get('imp_uid')
        success = request.GET.get('success')
        process = request.GET.get('process')
        next = request.GET.get('next', '')

        ###공통###
        if success:
            URL = "https://api.iamport.kr/users/getToken"
            headers={
                "Content-Type": "application/json"
            }
            data={
                'imp_key': config('IMP_KEY'),
                'imp_secret':config('IMP_SECRET'),
            }
            res = requests.post(URL, headers=headers, data=json.dumps(data))
            token = json.loads(res.text)['response']['access_token']

            _URL = f"https://api.iamport.kr/certifications/{imp_uid}"
            _headers={
                "Authorization": token,
            }
            res = requests.get(_URL, headers=_headers)
            info = json.loads(res.text)
            res = info.get('response', None)
        #########

            if res:
                #birthday
                try:
                    birthday_ymd=res.get('birthday').split('-')
                    birthday = date(int(birthday_ymd[0]), int(birthday_ymd[1]), int(birthday_ymd[2]))
                except:
                    birthday = None
                
                if process=='signup':
                    #unique_key
                    tmp=res.get('unique_key', None)
                    if tmp == '' or tmp == None:
                        messages.error(request, '다른 인증 방법을 선택해주십시오.')
                        return redirect(reverse('core:verify')+f"?next={next}")

                    try:
                        u_vf, created = Verification.objects.update_or_create(
                                unique_key=res.get('unique_key'),
                                defaults={
                                    'name':res.get('name'),
                                    'phone':res.get('phone'),
                                    'birthday':birthday,
                                }
                        )
                    #2개 이상
                    except:
                        messages.error(request,'이미 해당 명의로 계정이 가입되어 있습니다. 해당 계정으로 로그인해주세요.')
                        return redirect('account_signup')

                    #1개
                    if not created:
                        #시도 계정존재
                        if u_vf.user:
                            if EmailAddress.objects.filter(user=u_vf.user, verified=True).exists():
                                #인증 O 계정 O
                                messages.error(request,'이미 해당 명의로 계정이 가입되어 있습니다. 해당 계정으로 로그인해주세요.')
                                return redirect('account_signup')
                            else:
                                #인증 X 계정 O
                                messages.error(request,f"회원가입 진행하셨던 계정({u_vf.user.email})이 존재합니다. 해당 계정으로 로그인해주세요.")
                                return redirect('account_signup')
                        #인증 O 계정 X
                        else:
                            #Anonymous User Identifier
                            request.session['onenonly_user_unique_key']=res.get('unique_key')
                            messages.success(request, "회원가입 시도이력이 존재합니다. 인증이 완료되었습니다.")
                            if next != '' and next != 'null':
                                return redirect(next)
                            else:
                                return redirect(reverse('account_signup')+f"?cef=true")

                    else:
                        #인증 X 계정 X
                        #Anonymous User Identifier
                        request.session['onenonly_user_unique_key']=res.get('unique_key')
                        messages.success(request, "인증이 완료되었습니다.")

                        if next != '' and next != 'null':
                            return redirect(next)
                        else:
                            return redirect(reverse('account_signup')+f"?cef=true")

                elif process =='auth':
                    #unique_key
                    tmp=res.get('unique_key', None)
                    if tmp == '' or tmp == None:
                        messages.error(request, '다른 인증 방법을 선택해주십시오.')
                        return redirect(reverse('core:verify')+f"?next={next}")
                    try:
                        u_vf, created = Verification.objects.update_or_create(
                            unique_key = res.get('unique_key'),
                            defaults={
                                'user': request.user,
                                'name': res.get('name'),
                                'phone': res.get('phone'),
                                'birthday': birthday,
                                }
                        )

                        if res.get('phone'):
                            u_vf.last_verified = datetime.now()
                            u_vf.save()
                            request.session['phone_verified_user'] = request.user.id
                            messages.success(request,'인증 토큰이 저장되었습니다.')

                        if next != '' and next != 'null':
                            return redirect(next)
                        else:
                            return redirect('core:user')
                    except Exception as e:
                        messages.error(request, "이미 다른 아이디에 인증이 되어있습니다. 동일한 사람이 여러개의 아이디를 인증할 수 없습니다.")
            else:
                messages.error(request, '아임포트 서버로부터 인증토큰을 받아오지 못했습니다.')
                return redirect('core:home')
            
            return redirect('core:home')
        else:
            messages.error(request, '인증에 실패하였습니다.')
            return redirect('core:home')



class UserPasswordChangeView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        token_generator = EmailAwarePasswordResetTokenGenerator()
        temp_key = token_generator.make_token(request.user)
        path = reverse("account_reset_password_from_key", 
                kwargs=dict(uidb36=user_pk_to_url_str(request.user), key=temp_key))
        return redirect(path)

class UserPrivacyToggleView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            up = request.user.userprivacy
            up.agreement_4 = not up.agreement_4
            up.save()
            if up.agreement_4:
                return JsonResponse({'ad':'activate'}, status=200)
            else:
                return JsonResponse({'ad':'deactivate'}, status=200)
            # messages.info(request, "{}... 옥션앵콜 요청이 완료되었습니다. 옥션이 추후 열린다면 알람이 전송됩니다.".format(placement.placement_title[:15]))
        except:
            return JsonResponse({'ad':'UserPrivacy 모델이 없습니다.'}, status=500)

@login_required
def DeActivateUser(request):
    if request.user.is_authenticated:
        request.user.is_active = False
        request.user.save()

        clocked, _ = ClockedSchedule.objects.get_or_create(
            clocked_time=ToUTC(datetime.now())+timedelta(days=30)
        )
        PeriodicTask.objects.create(
            clocked=clocked,
            expires=ToUTC(datetime.now())+timedelta(days=50),
            name=f"{request.user.username}-UserDelete",
            task="core.tasks.DeleteUser",
            one_off=True,
            kwargs=json.dumps({
                'id':request.user.id,
            }),
        )    
        messages.info(request, f"{request.user.username}님 계정이 비활성화 되었습니다. 30일 경과후 계정 및 개인정보는 자동 삭제됩니다")
        return redirect('core:home')
    else:
        messages.error(request, "로그인이 되어있지 않습니다.")
        return redirect('account_login')

class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Users
    fields = (
        "username",
        "email",
    )
    context_object_name = "user"
    success_message = "프로필이 업데이트 되었습니다"
    success_url = reverse_lazy('core:user')
    template_name = "account/mypage/MypageInfo.html"

    def get_object(self, queryset = None):
        return self.request.user

    # def get_form(self, form_class=None):
    #     form = super().get_form(form_class=form_class)
    #     form.fields["username"].widget.attrs = {"placeholder" : self.request.user.username}
    #     form.fields["username"].required = True
    #     form.fields["email"].widget.attrs = {"placeholder" : self.request.user.email }
    #     form.fields["email"].required = True
    #     return form



'''
ORDER & PAY
'''

@login_required
def AddAuctionToOrderItem(request, pk, placement_id):
    placement=Placement.objects.get(id=placement_id)
    I_orderitem=None
    #크라우드펀딩
    if placement.placement_type == 'crowdfunding':
        try:
            donation=Donation.objects.get(user=request.user, pk=pk)
            I_orderitem, created = CrowdFundingOrderItem.objects.update_or_create(
                user=request.user,
                placement = placement,
                donation = donation,
                price=donation.offer,
                expired=False,
                deliver_detail = 1,
                defaults={
                    'quantity':donation.quantity,
                }
            )
            #카카오톡 알림(v2_crowd_bid_1)
            #관리자문자
            phones_params=[]
            phone=request.user.verification.standardize_phone()
            params={
                'USERNAME':request.user.username,
                'TITLE': placement.title,
                'PRICE':I_orderitem.get_final_price(),
            }
            phones_params.append({phone:params})
            tmpltCode='v2_crowd_bid_1'

            # Biz_KAKAO_Send.run(phones_params=phones_params, tmpltCode=tmpltCode)
            # AdminPhone_SMS_Send.run(f"상품주문\n유저:{request.user.username}\n상품:{placement.title[:5]}\n주문번호:{I_orderitem.id}")
            Biz_KAKAO_Send.apply_async(kwargs={'phones_params':phones_params, 'tmpltCode':tmpltCode}, ignore_result=False)
            AdminPhone_SMS_Send.apply_async(args=[f"상품주문\n유저:{request.user.username}\n상품:{placement.title[:5]+'...'}\n주문번호:{I_orderitem.id}\n개수:{I_orderitem.quantity}"], ignore_result=False)

            if created:
                I_orderitem.due_date=datetime.now()+timedelta(minutes=20)
                I_orderitem.save()
                #Expire 2개
                Before_Make_OrderItem_Expired.apply_async(kwargs={'pk':I_orderitem.id, 'slug':I_orderitem.placement.placement_type}, eta=SeoulToUTC(datetime.now())+timedelta(minutes=15), expires=SeoulToUTC(datetime.now())+timedelta(days=1))
                Make_OrderItem_Expired.apply_async(kwargs={'pk':I_orderitem.id, 'slug':I_orderitem.placement.placement_type}, eta=SeoulToUTC(datetime.now())+timedelta(minutes=20), expires=SeoulToUTC(datetime.now())+timedelta(days=1))
                # Make_OrderItem_Expired.run(pk=I_orderitem.id, slug=I_orderitem.placement.placement_type)
            messages.success(request, "주문에 성공하였습니다. 기한내에 결제를 완료해주세요.")
            return redirect('core:checkout', type=placement.placement_type, pk=I_orderitem.id)
        except:
            messages.error(request, "[일반티켓 구매] 주문생성 중 에러가 발생하였습니다.")

    #오픈, 시크릿펀딩 바로구매
    elif placement.placement_type == 'secretfunding' or placement.placement_type=='openfunding':
        placementbid=PlacementBid.objects.get(user=request.user, pk=pk)
        try:
            f_secret_open_make1(request, placementbid)
        except:
            pass
    else:
        messages.error(request,"옥션 기능(OpenFunding)은 지원하지 않습니다.")
    return redirect('core:user')

class CheckoutView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        type=kwargs.get('type')
        pk=kwargs.get('pk')
        amountToBePaid=0
        if type == 'openfunding':
            orderitem = OpenFundingOrderItem.objects.get(pk=pk, user=request.user)
            if orderitem.deliver_detail==1:
                amountToBePaid=orderitem.placement.deposit
            elif orderitem.deliver_detail==2:
                amountToBePaid=orderitem.get_final_price()-orderitem.placement.deposit            
        elif type == 'secretfunding':
            orderitem = SecretFundingOrderItem.objects.get(pk=pk, user=request.user)
            if orderitem.deliver_detail==1:
                amountToBePaid=orderitem.placement.deposit
            elif orderitem.deliver_detail==2:
                amountToBePaid=orderitem.get_final_price()-orderitem.placement.deposit                    
        elif type == 'crowdfunding':
            orderitem = CrowdFundingOrderItem.objects.get(pk=pk, user=request.user)
            if orderitem.deliver_detail==1:
                amountToBePaid=orderitem.get_final_price()

        if orderitem.deliver_detail >= 3:
            messages.info(request, '이미 결제가 완료된 주문서입니다.')
            return redirect('core:user')

        if orderitem.expired:
            messages.info(request, '결제가 불가능한 만료된 주문서입니다. 구매를 다시 시도해주십시오.')
            return redirect('core:user')

        #미성년자
        u_vf=Verification.objects.get_or_none(user=request.user)        
        child='False'
        age19=365*19
        if u_vf is not None:
            if datetime.now().date() - request.user.verification.birthday < timedelta(days=age19):
                if amountToBePaid >= 200000:
                    child='True'
        #COUPON
        coupons = Coupon.objects.filter(user=request.user, placement__in=[orderitem.placement], expired=False)
        context={
            'orderitem':orderitem,
            'child':child,
            'coupons':coupons,
        }
        return render(request, 'checkout.html', context)
    # def post(self, request, *args, **kwargs):

@require_http_methods(["POST"])
@login_required
def AddCouponView(request, *args, **kwargs):
    type=kwargs.get('type')
    pk=kwargs.get('pk')
    if type == 'openfunding':
        orderitem = OpenFundingOrderItem.objects.get(pk=pk, user=request.user)
    elif type == 'secretfunding':
        orderitem = SecretFundingOrderItem.objects.get(pk=pk, user=request.user)
    elif type == 'crowdfunding':
        orderitem = CrowdFundingOrderItem.objects.get(pk=pk, user=request.user)
    couponID = request.POST.get('couponID', None)
    _coupon=Coupon.objects.get_or_none(id=couponID)
    if _coupon is not None:
        if _coupon.expired == False:
            orderitem.coupon=_coupon
    else:
        orderitem.coupon = _coupon
    orderitem.save()

    return redirect('core:checkout', type=type, pk=pk)


def GetPaymentData(imp_uid):
    ### Get Access Token ###
    URL = "https://api.iamport.kr/users/getToken"
    headers={
        "Content-Type": "application/json"
    }
    data={
        'imp_key': config('IMP_KEY'),
        'imp_secret':config('IMP_SECRET'),
    }
    res = requests.post(URL, headers=headers, data=json.dumps(data))
    token = json.loads(res.text)['response']['access_token']
    ### Get PaymentData ###
    _URL = f"https://api.iamport.kr/payments/{imp_uid}"
    _headers={
        "Authorization": token,
    }
    res = requests.get(_URL, headers=_headers)
    info = json.loads(res.text)
    res = info.get('response', None)
    ######
    return res


@require_http_methods(["GET", "POST"])
def CheckoutProcessView(request, type, pk):
    amountToBePaid=0
    if type == 'openfunding': #depreciated
        orderitem = OpenFundingOrderItem.objects.get(pk=pk, user=request.user)
        if orderitem.deliver_detail==1:
            amountToBePaid=orderitem.placement.deposit
        elif orderitem.deliver_detail==2:
            amountToBePaid=orderitem.get_final_price()-orderitem.placement.deposit
    elif type == 'secretfunding':
        orderitem = SecretFundingOrderItem.objects.get(pk=pk, user=request.user)
        if orderitem.deliver_detail==1:
            amountToBePaid=orderitem.placement.deposit
        elif orderitem.deliver_detail==2:
            amountToBePaid=orderitem.get_final_price()-orderitem.placement.deposit        
    elif type == 'crowdfunding':
        orderitem = CrowdFundingOrderItem.objects.get(pk=pk, user=request.user)
        if orderitem.deliver_detail==1:
            amountToBePaid=orderitem.get_final_price()

    #미성년자
    age19=365*19
    if datetime.now().date()-request.user.verification.birthday < timedelta(days=age19):
        if amountToBePaid >= 200000:
            messages.error(request, "미성년자(법정나이 만 19세 미만)는 20만원 이상 구매가 불가능합니다.")
            return redirect('core:checkout', type=type, pk=pk)

    if is_mobile(request):
        #MOBILE
        imp_uid=request.GET.get('imp_uid')
        merchant_uid=request.GET.get('merchant_uid')
        imp_success = request.GET.get('imp_success')
        success=request.GET.get('success')
        error_msg=request.GET.get('error_msg')
        error_code=request.GET.get('error_code')
        if error_msg:
            messages.error(request, f"결제를 처리하던 도중 에러가 발생하였습니다.\n에러코드 : {error_code}\n에러메시지 : {error_msg}")
            return redirect('core:checkout', type=type, pk=pk)        
    else:
        #PC
        data=json.loads(request.body)
        imp_uid=data.get('imp_uid')
        merchant_uid=data.get('merchant_uid')
        imp_success = data.get('imp_success')
        success=data.get('success')        
    
    #진행
    paymentData=GetPaymentData(imp_uid)
    status=paymentData.get('status')
    amount=paymentData.get('amount')
    receipt_url=paymentData.get('receipt_url')
    url = _parse.urlparse(receipt_url)
    query = _parse.parse_qs(url.query)
    result = _parse.urlencode(query, doseq=True)
    # receipt_url = "https://www.danalpay.com/receipt/creditcard/view.aspx" + f"?{result}"
    if amountToBePaid == int(amount):
        if status=='ready': #가상계좌 발급
            orderitem.vbank_num=paymentData.get('vbank_num')
            orderitem.vbank_name=paymentData.get('vbank_name')
            orderitem.vbank_date=datetime.fromtimestamp(int(paymentData.get('vbank_date')))
            orderitem.save()
            if not is_mobile(request):
                return JsonResponse({'msg':'가상계좌 발급에 성공하였습니다. 기한내 입금하여 주문을 완료해주세요.','paymentData':paymentData}, status=200)
            else:
                messages.success(request, '가상계좌 발급에 성공하였습니다. 기한내 입금하여 주문을 완료해주세요.')
                return redirect(reverse('core:checkout_complete', kwargs={'type':type, 'pk':pk})+f"?vbank=true")
        elif status=='paid': #결제완료
            if not is_mobile(request):
                return JsonResponse({'msg':'결제에 성공하였습니다. 결제내역은 마이페이지에서 확인할 수 있습니다.','paymentData':paymentData}, status=200)
            else:
                messages.success(request, '결제 성공하였습니다. 결제내역은 마이페이지에서 확인할 수 있습니다.')
                return redirect(reverse('core:checkout_complete', kwargs={'type':type, 'pk':pk})+f"?amountToBePaid={amountToBePaid}&card_name={paymentData.get('card_name')}&receipt_url={receipt_url}")
        elif status=='failed': #결제실패
            if not is_mobile(request):
                return JsonResponse({'msg':'[에러코드:A]결제에 실패하였습니다. 다시 시도해주십시오.', 'paymentData':paymentData}, status=500)
            else:
                messages.error(request, '[에러코드:A]결제에 실패하였습니다. 다시 시도해주십시오')
                return redirect('core:checkout', type=type, pk=pk)

        else:
            if not is_mobile(request):
                return JsonResponse({'msg':'[에러코드:B]결제에 실패하였습니다. 다시 시도해주십시오.'}, status=500)
            else:
                messages.error(request, '[에러코드:B]결제에 실패하였습니다. 다시 시도해주십시오')
                return redirect('core:checkout', type=type, pk=pk)
    else:
        if amount:
            amountToBePaid=amount
        else:
            if amountToBePaid==0:
                amountToBePaid='* 원(마이페이지에서 결제내역 확인)'
        if paymentData.get('card_name'):
            card_name=paymentData.get('card_name')
        else:
            card_name='* 카드(마이페이지에서 결제내역 확인)'
        return redirect(reverse('core:checkout_complete', kwargs={'type':type, 'pk':pk})+f"?amountToBePaid={amountToBePaid}&card_name={card_name}")
    # #is_ajax()
    # if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.accepts("application/json"):
    #     #PC
    #     return JsonResponse({'msg':'결제에 성공하였습니다. 결제내역은 마이페이지에서 확인할 수 있습니다.'}, status=200)
    # else:
    #     #Mobile
    #     messages.success(request, '결제에 성공하였습니다. 결제내역은 마이페이지에서 확인할 수 있습니다.')
    #     return redirect('core:checkout_complete', slug=type, pk=pk)

@csrf_exempt
@require_http_methods(["POST"])
def CheckoutWebhookView(request):
    data=json.loads(request.body)
    imp_uid=data.get('imp_uid')
    merchant_uid=data.get('merchant_uid')
    status = data.get('status')
    # merchant_uid==paymentData.get('merchant_uid')

    #조회값
    paymentData=GetPaymentData(imp_uid)
    amount=paymentData.get('amount')
    cancel_amount=paymentData.get('cancel_amount', 0)

    #서버값
    order=merchant_uid.split('_')
    type=order[0]
    pk=order[1]

    amountToBePaid=0
    errors=[]    
    f_type=''
    if type == 'openfunding':    #depreciated
        orderitem = OpenFundingOrderItem.objects.get(pk=pk)
        if orderitem.deliver_detail==1:
            amountToBePaid=orderitem.placement.deposit
            f_type='f_secret_open_make2'
        elif orderitem.deliver_detail==2:
            amountToBePaid=orderitem.get_final_price()-orderitem.placement.deposit
            f_type='f_secret_open_make3'            
    elif type == 'secretfunding':
        orderitem = SecretFundingOrderItem.objects.get(pk=pk)
        if orderitem.deliver_detail==1:
            amountToBePaid=orderitem.placement.deposit
            f_type='f_secret_open_make2'
        elif orderitem.deliver_detail==2:
            amountToBePaid=orderitem.get_final_price()-orderitem.placement.deposit
            f_type='f_secret_open_make3'
    elif type == 'crowdfunding':
        orderitem = CrowdFundingOrderItem.objects.get(pk=pk)
        if orderitem.deliver_detail==1:
            amountToBePaid=orderitem.get_final_price()
            f_type='f_crowd_make3_checkmake4'
    # order[0]==orderitem.placement.type
    # order[1]==orderitem.id


    #검증로직
    if amountToBePaid == int(amount):
        if status=='ready': #가상계좌 발급
            '''
            가상계좌 발급 LOGIC
            '''            
            payment, _=Payment.objects.update_or_create(
                user=orderitem.user,
                imp_uid=imp_uid,
                defaults={
                    'status':paymentData.get('status'),
                    'pay_method':paymentData.get('pay_method'),
                    'amount':int(paymentData.get('amount')),
                    'vbank_name':paymentData.get('vbank_name'),
                    'vbank_num':paymentData.get('vbank_num'),
                    'vbank_date':datetime.fromtimestamp(int(paymentData.get('vbank_date'))),
                }
            )
            orderitem.imp_uid=imp_uid
            orderitem.payment=payment
            orderitem.save()
            return HttpResponse(status=200)            
        elif status=='paid': #결제완료
            '''
            결제완료 LOGIC
            '''
            if f_type=='f_secret_open_make2':
                f_secret_open_make2(orderitem)
            elif f_type=='f_secret_open_make3':
                f_secret_open_make3(orderitem)
            elif f_type=='f_crowd_make3_checkmake4':
                f_crowd_make3_checkmake4(orderitem)
                errors=f_ticket_send(_oi=orderitem, _queryset=None)

            payment, _=Payment.objects.update_or_create(
                user=orderitem.user,
                imp_uid=imp_uid,
                defaults={
                    'status':paymentData.get('status'),
                    'pay_method':paymentData.get('pay_method'),
                    'amount':int(paymentData.get('amount')),
                    'card_name':paymentData.get('card_name'),
                    'card_number':paymentData.get('card_number'),
                    'receipt_url':paymentData.get('receipt_url'),
                    'paid_at':datetime.fromtimestamp(int(paymentData.get('paid_at'))),
                }
            )
            orderitem.imp_uid=imp_uid
            orderitem.payment=payment
            orderitem.save()
            if len(errors)>0:
                e=','.join(errors)
                raise Exception(f"{e}번 티켓 전송실패")
            else:
                return HttpResponse(status=200)

        elif status=='failed': #결제실패
            return HttpResponse(status=500)

    #환불
    elif 0 < cancel_amount:
        if status == 'cancelled':
            if f_refund_complete(orderitem):
                return HttpResponse(status=200)
            else:
                raise Exception('WEBHOOK: 환불과정 오류')
        else:
            pass
    #위조
    else:
        raise Exception('WEBHOOK: 금액 검증오류')
class CheckoutCompleteView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        type=kwargs.get('type')
        pk=kwargs.get('pk')
        if type == 'openfunding':
            orderitem = OpenFundingOrderItem.objects.get_or_none(pk=pk, user=request.user)
        elif type == 'secretfunding':
            orderitem = SecretFundingOrderItem.objects.get_or_none(pk=pk, user=request.user)
        elif type == 'crowdfunding':
            orderitem = CrowdFundingOrderItem.objects.get_or_none(pk=pk, user=request.user)

        # if orderitem.deliver_detail >= 3:
        #     messages.info(request, '이미 결제가 완료된 주문서입니다.')
        #     return redirect('core:user')

        if orderitem is None:
            messages.error(request, '결제를 실패하였습니다. 다시 시도해주십시오')
            return redirect('core:checkout', type=type, pk=pk)

        if orderitem.expired:
            messages.info(request, '결제가 불가능한 만료된 주문서입니다.')
            return redirect('core:user')


        context={
            'orderitem':orderitem,
        }
        return render(request, 'checkout_complete.html', context)

@login_required
def remove_from_cart_orderitem(request, type, pk):
    try :
        if type == 'openfunding':
            orderitem = OpenFundingOrderItem.objects.get(pk=pk, user=request.user)
        elif type == 'secretfunding':
            orderitem = SecretFundingOrderItem.objects.get(pk=pk, user=request.user)
        elif type == 'crowdfunding':
            orderitem = CrowdFundingOrderItem.objects.get(pk=pk, user=request.user)
        name=orderitem.placement.title
        if orderitem.quantity > 1:
            orderitem.donation.quantity -= 1
            orderitem.donation.save()
            orderitem.quantity -= 1
            orderitem.save()
        else:
            orderitem.delete()
        messages.success(request, "{0} 요청서를 삭제하였습니다.".format(name))
        return redirect("core:user")
    except:
        messages.info(request, "요청서가 존재하지 않습니다.")
        return redirect("core:user")



@login_required
def ToggleRefundView(request, slug, pk):
    try :
        if slug == 'openfunding':
            orderitem = OpenFundingOrderItem.objects.get(pk=pk, user=request.user)
        elif slug == 'secretfunding':
            orderitem = SecretFundingOrderItem.objects.get(pk=pk, user=request.user)
        elif slug == 'crowdfunding':
            orderitem = CrowdFundingOrderItem.objects.get(pk=pk, user=request.user)

        # if orderitem.expired:
        #     messages.info(request,"이미 만료된 요청서입니다.")
        #     return redirect('core:user')

        if 'cancel' in request.POST:
            if orderitem.refund_requested:
                messages.info(request, "환불 신청을 취소하였습니다.")
                AdminPhone_SMS_Send.apply_async(args=[f"환불취소\n유저:{request.user.username}[{request.user.id}]\n주문번호:{orderitem.id}"], ignore_result=False)
                orderitem.refund_requested = False
            else:
                pass
        elif 'process' in request.POST:
            if orderitem.deliver_detail == 1:
                messages.success(request, "환불 신청이 완료되었습니다.")
                AdminPhone_SMS_Send.apply_async(args=[f"환불신청\n유저:{request.user.username}[{request.user.id}]\n주문번호:{orderitem.id}"], ignore_result=False)
                orderitem.refund_requested = True
            elif orderitem.deliver_detail == 4:
                messages.error(request, "진행 확정상태에서는 환불신청이 어렵습니다. 자세한 사항은 홈페이지 하단 고객센터 또는 채팅봇에 문의 부탁드립니다.")
                return redirect('core:user')
            else:
                try:
                    rf_account = request.POST.get('refund_account', None)
                    rf_file = request.FILES['refund_file']
                    if rf_account and rf_file:
                        orderitem.refund_account = rf_account
                        orderitem.refund_file = rf_file
                        orderitem.refund_requested= True
                        messages.success(request, "환불 신청이 완료되었습니다.")
                        AdminPhone_SMS_Send.apply_async(args=[f"환불신청\n유저:{request.user.username}[{request.user.id}]\n주문번호:{orderitem.id}"], ignore_result=False)
                except:
                    messages.info(request, "환불 계좌 또는 환불사유서 파일 업로드가 되지않았습니다. 다시 확인후 시도 바랍니다.")
                    return redirect('core:user')
        else:
            pass
        orderitem.save()
    except:
        messages.info(request, "주문내역이 존재하지 않습니다.")

    return redirect("core:user")

class TicketView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        type=kwargs['type']
        oid=kwargs['pk']
        if type=='openfunding':
            oi=OpenFundingOrderItem.objects.get_or_none(pk=oid)
            orderitems=oi.placement.placement_win.openfundingorderitem
        elif type=='secretfunding':
            oi=SecretFundingOrderItem.objects.get_or_none(pk=oid)
            orderitems=oi.placement.placement_win.secretfundingorderitem
        elif type=='crowdfunding':
            oi=CrowdFundingOrderItem.objects.get_or_none(pk=oid)
            oid_qs=[str(d.crowdfundingorderitem.id) for d in oi.placement.placement_win_crowdfunding.all()]
            if len(oid_qs) != 0:
                orderitems=CrowdFundingOrderItem.objects.filter(id__in=oid_qs).order_by('-updated')
            else:
                orderitems=None
        context={
            'type':type,
            'orderitem':oi,
            'orderitems':orderitems,
        }
        #본인
        if request.user == oi.user:
            return render(request, 'ticket.html', context)

        #관리자
        elif request.user.is_staff:
            if not oi.ticket_checked:
                oi.ticket_checked=True
                oi.save()            
                messages.success(request, '티켓확인이 완료되었습니다')
                context['checked']=False
            else:
                messages.info(request, f"이미 확인처리가 된 티켓입니다. 최종 수정일 - {oi.updated}")
                context['checked']=True
            return render(request, 'ticket_admin.html', context)
                        
        #다른고객
        elif not(request.user.is_staff) and request.user != oi.user:
            messages.error(request, '주문상품에 대한 당사자만 티켓을 확인할 수 있습니다. 상품주문시 사용했던 아이디로 로그인해주십시오.')
            return redirect('core:home')            

# class ItemListView(ListView):
#     model = Items
#     template_name = "list.html"
#     context_object_name = "items"
#     paginate_by = 24
#     paginate_orphans = 3
#     #form_class = LForm

#     def get_context_data(self, **kwargs):
#         context = super(ItemListView, self).get_context_data(**kwargs)
#         return context

# class ArtistItemDetailView(DetailView):
#     model = Items
#     context_object_name = "item"
#     template_name = "detail_item.html"
#     def post(self, request, *args, **kwargs):
#         item = super().get_object()
 
#         #주문하기(Item 주문)
#         try:
#             form = OrderArtist_Form_item(request.POST or None)
#             #채워넣는 logic    
#             if form.is_valid():
#                 form = form.save(commit=False)
#                 form.user = request.user
#                 form.ordered_detail = 1

#                 form.artist = item.artist
#                 form.price = item.price
#                 form.discount_price = item.discount_price                
#                 form.music_name = item.title
#                 form.music_vibe = item.description
#                 form.music_purpose = item.category
#                 #ORDER 모델 만들기
#                 order, created = Order.objects.get_or_create(
#                 user=request.user,
#                 ordered=False,
#                 )                   

#                 #order link
#                 form.order=order
#                 form.save()         
                
#             else:
#                 messages.info(request, "OrderArtist_Form_present Error occurred")                
#             return redirect('core:checkout')
#         except:
#             #DUMMY POST GREP
#             messages.info(request, "저장에 실패하였습니다. 다시 시도해주세요!")


#         self.object = self.get_object()
#         context = self.get_context_data(**kwargs)
#         return self.render_to_response(context=context)    
    
# class ArtistDetailView(DetailView):
#     model = Artists
#     context_object_name = "artist"
#     template_name = "detail_artist.html"
 
#     #Pagination
#     def get_context_data(self, **kwargs):
#         context = super(ArtistDetailView, self).get_context_data(**kwargs)
#         pk=self.kwargs['pk']
#         artist = super().get_object()
#         try:
#             post_list = artist.user.post.all()
#             review_list = artist.review.all()
#             post_paginator = Paginator(post_list, 6)
#             post_paginator.orphans=3
#             review_paginator = Paginator(review_list, 6)
#             review_paginator.orphans=3
#             post_page = self.request.GET.get('post_page' ,'1') 
#             review_page =  self.request.GET.get('review_page', '1')
#             posts = post_paginator.get_page(post_page)
#             reviews = review_paginator.get_page(review_page)
#             context['posts'] = posts
#             context['reviews'] = reviews
#             context['review_list'] = review_list
#             return context

#         except:
#             messages.info(self.request, "Pagination error occurred")
#             return context

#     #post, comment 작성 & OrderArtist 분류
    
#     def post(self, request, *args, **kwargs):
#         artist = super().get_object()
#         #리뷰(review)
#         if request.GET.get('which', '') == "review":
#             form = Review_Form(request.POST or None)
#             #채워넣는 logic    
#             if form.is_valid():
#                 form = form.save(commit=False)
#                 form.user = request.user
#                 form.artist = artist 
#                 form.save()
#             else:
#                 messages.info(request, "Review_Form Error occurred")


#         #문의하기(Post)
#         elif request.GET.get('which', '') == "post":
#             form = Post_Form(request.POST or None) 
#             #채워넣는 logic    

#             if form.is_valid():
#                 form = form.save(commit=False)
#                 form.user = request.user
#                 form.save()                   
                          
#             else:
#                 messages.info(request, "Post_Form Error occurred")
                


#         #주문하기(선물하기)        
#         elif request.GET.get('which', '') == "orderartist_1":
#             form = OrderArtist_Form_present(request.POST) 
#             #채워넣는 logic    
#             if form.is_valid():
#                 form = form.save(commit=False)
#                 form.user = request.user
#                 form.artist=artist
#                 form.ordered_detail = 1
#                 form.price = artist.price
#                 form.discount_price = artist.discount_price
                
#                 #ORDER 모델 만들기
#                 order, created = Order.objects.get_or_create(
#                 user=request.user,
#                 ordered=False,
#                 )                   

#                 #order link
#                 form.order=order
#                 form.save()         
                
#             else:
#                 messages.info(request, "OrderArtist_Form_present Error occurred")
#             return redirect('core:checkout')
              

#         #주문(연습영상)          
#         elif request.GET.get('which', '') == "orderartist_2":
#             form = OrderArtist_Form_practice(request.POST) 
#             #채워넣는 logic    

#             if form.is_valid():
#                 form = form.save(commit=False)
#                 form.user = request.user
#                 form.artist=artist
#                 form.ordered_detail = 1
#                 form.lesson_price = artist.lesson_price
#                 form.lesson_discount_price = artist.lesson_discount_price

#                 #ORDER 모델 만들기
#                 order = Order.objects.get_or_create(
#                 user=request.user,
#                 ordered=False,                
#                 )

#                 #order link
#                 form.order=order
#                 form.save()   
                
#             else:
#                 messages.info(request, "Orderartist_Form_practice Error occurred")
#             return redirect('core:checkout')

#         else:
#             #DUMMY POST GREP
#             messages.info(request, "저장에 실패하였습니다. 다시 시도해주세요!")


#         self.object = self.get_object()
#         context = self.get_context_data(**kwargs)
#         return self.render_to_response(context=context)


# class artistpage(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
#     model = Artists
#     template_name = "account/mypageA/Mypage_artist.html"
#     form_class = Artist_Form
#     context_object_name = "artist"
#     success_message = "프로필이 업데이트 되었습니다"

#     def get(self, request, *args, **kwargs):
#         if self.request.user.is_artist:
#             return super().get(request, *args, **kwargs)
#         else:
#             messages.info(request, "아티스트 등록이 필요합니다")
#             return redirect('core:user')

#     # def __init__(self):
#     #     print(self.request)
#     #     if self.request.user.is_artist:
#     #         super().__init__()
#     #     else:
#     #         messages.info(self.request, "아티스트 등록이 필요합니다")
#     #         reverse('core:userpage')

#     def get_success_url(self):
#         return reverse('core:user')

#     def get_object(self, queryset = None):
#         return self.request.user.artist

#     def get_form(self, form_class=None):
#         form = super().get_form(form_class=form_class)
#         # form.fields["username"].widget.attrs = {"placeholder" : self.request.user.username}
#         # form.fields["username"].required = True
#         # form.fields["email"].widget.attrs = {"placeholder" : self.request.user.email }
#         # form.fields["email"].required = True
#         return form


# class UserRegArtist(CreateView):
#     form_class = Artist_Form
#     template_name = 'account/mypageU/Mypage_user_reg.html'
#     success_url = reverse_lazy('core:userregartist')
#     def get_initial(self):
#         initial = super(UserRegArtist, self).get_initial()
#         if self.request.user.is_authenticated:
#             initial.update({'K_name': '한글이름',
#                             'E_name': '영어이름' })
#         return initial

#     def form_valid(self, form):
#         self.object = form.save(commit=False)
#         self.object.user = self.request.user
#         self.object.save()
# #        form.cleaned_data.get('')
#         return super(UserRegArtist, self).form_valid(form)

# def ArtistCalc(request):
#     orderartist_list=OrderArtists.objects.filter(artist=request.user.artist, deliver_detail=1)

#     if request.method == 'GET':
#         context = {
#             'orderartist_list': orderartist_list,
#         }
#         return render(request, "account/mypageA/Mypage_artist_calc.html", context)

# def ArtistUpload(request):
#     orderartist_list=OrderArtists.objects.filter(artist=request.user.artist, deliver_detail=1)

#     if request.method == 'GET':
        
#         context = {
#             'orderartist_list': orderartist_list,
            
#         }
#         return render(request, "account/mypageA/Mypage_artist_upload.html", context)

#     elif request.method == 'POST':
#         # form=OrderVideo_Form(request.POST, request.FILES)
#         orderartist_pk=request.GET.get('pk','')
#         # if form.is_valid():
#         #     form.save(commit=False)

#         #     form.save()
#         try:
#             orderartist=OrderArtists.objects.get(pk=orderartist_pk)
#             ordervideo, created = OrderVideos.objects.get_or_create(
#             artist = request.user.artist,
#             user=orderartist.user,
#             orderartist=orderartist,
#             )
#             ordervideo.video = request.FILES['video']

# #html에 구현해야함
#             ordervideo.title = request.user.artist + "님의 연주선물"
#             ordervideo.description = "영상 설명, 해설 부분"            
#             ordervideo.password = "1234"

#             ordervideo.save()

#             orderartist.deliver_detail=2

#             messages.success(request, "비디오 업로드가 완료되었습니다. 팬분께 비디오를 전달해드릴게요!")


#         except:
#             messages.info(request, "업로드에 실패하였습니다.")
#         return redirect("core:artistupload")
#         #return render(request, 'account/Mypage_artist_upload.html', context)
#     messages.info(request, "POST, GET 이외의 새로운 요청이 들어왔습니다")
#     return redirect("core:artistupload")

# class ArtistItemUpload(CreateView):
#     form_class = Item_Form
#     template_name = 'account/mypageA/Mypage_artist_itemupload.html'
#     success_url = reverse_lazy('core:artistitemupload')

#     def form_valid(self, form):
#         self.object = form.save(commit=False)
#         self.object.artist = self.request.user.artist
#         self.object.save()
# #        form.cleaned_data.get('')
#         return super(ArtistItemUpload, self).form_valid(form)

# def UserCollection(request):

#     order_list = Order.objects.filter(user=request.user, ordered=True)    
#     context = {
#     'order_list':order_list        
#     }
#     return render(request, "account/mypageU/Mypage_user_collection.html", context)

# def UserOrder(request):
#     order_list = Order.objects.filter(user=request.user, ordered=True)
#     context={
#         'order_list':order_list
#     }
#     return render(request, "account/mypageU/Mypage_user_order.html", context)

# def UserPlay(request): 
#     ordervideolist=OrderVideos.objects.filter(user=request.user, orderartist__delivered=True)


#     # bdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sample')
#     # v1=os.path.join(bdir, 'intro.mp4')
#     # v2=os.path.join(bdir, 'body.mp4')
#     # v3=os.path.join(bdir, 'outro.mp4')
#     # clip1 = VideoFileClip(v1)
#     # clip1= clip1.crossfadein(2.0).crossfadeout(2.0).audio_fadein(2).audio_fadeout(2)
#     # clip2 = VideoFileClip(v2)
#     # clip2= clip2.crossfadein(2.0).crossfadeout(2.0).audio_fadein(2).audio_fadeout(2)
#     # clip3 = VideoFileClip(v3)
#     # clip3 = clip3.crossfadein(2.0).crossfadeout(2.0).audio_fadein(2).audio_fadeout(2)
#     # final_clip = concatenate_videoclips([clip1,clip2,clip3], method="compose")
#     # # final_clip=clip1
#     # logo = (ImageClip(bdir+"/logo.png")
#     #       .set_duration(final_clip.duration)
#     #       .resize(height=300) # if you need to resize...
#     #       .margin(right=10, top=15, opacity=0) # (optional) logo-border padding
#     #       .set_pos(("right","top")))
#     # final_clip = CompositeVideoClip([final_clip, logo])
#     # #method=compose 하기
#     # final_clip.write_videofile(bdir+"/concat.mp4")


#     # # txt_clip = ( TextClip("Playplz Present Only for you",fontsize=70,color='white')
#     # #             .with_position('center')
#     # #             .with_duration(10) )

#     # # result = CompositeVideoClip([final_clip, txt_clip]) # Overlay text on video
#     # # result.write_videofile(bdir+"/concat.mp4") # Many options...

#     if request.method == 'GET':
#         context = {
#             'ordervideo_list': ordervideolist,
#         }
#         return render(request, "account/mypageU/Mypage_user_play.html", context)

#     #POST요청 없음
#     elif request.method == 'POST':
#         # form=OrderVideo_Form(request.POST, request.FILES)
#         orderartist_pk=request.GET.get('pk','')
#         # if form.is_valid():
#         #     form.save(commit=False)

#         #     form.save()
#         try:
#             orderartist=OrderArtists.objects.get(pk=orderartist_pk)
#             ordervideo, created = OrderVideos.objects.get_or_create(
#             artist = request.user.artist,
#             user=orderartist.user,
#             orderartist=orderartist,
#             )
#             ordervideo.video = request.FILES['video']
#             ordervideo.save()

#             orderartist.deliver_detail=2

#             messages.success(request, "비디오 업로드가 완료되었습니다. 팬분께 비디오를 전달해드릴게요!")


#         except:
#             messages.info(request, "업로드에 실패하였습니다.")
#         return redirect("core:artistupload")
#         #return render(request, 'account/Mypage_artist_upload.html', context)
#     messages.info(request, "POST, GET 이외의 새로운 요청이 들어왔습니다")
#     return redirect("core:userplay")



# def begin(request):
#     items = Item.objects.all()
#     userprofiles = UserProfile.objects.all()
#     context={
#         "items": items,
#         "userprofiles" : userprofiles
#     }
#     return render(request,"begin.html", context)

# def introduce(request):
#     return render(request, "introduce.html", None)

# class article_upload(View):

#     def get(self, request, *args, **kwargs):
#         order_list = Order.objects.filter(user=request.user, ordered=False)
#         form = Article_uploadForm(request.user)
#         context = {
#             'order_list': order_list,
#             'form': form
#         }

#         return render(request, 'account/myvideopage.html', context)

#     def post(self ,request, *args, **kwargs):
#         order_list = Order.objects.filter(user=request.user, ordered=False)
#         form = Article_uploadForm(request.user, request.POST, request.FILES)
#         if form.is_valid():
#             form = form.save(commit=False)
#             form.author = request.user
#             v = vimeo.VimeoClient(
#                 token = 'f2e8eaa7fe9fcf4358433f77e369770d',
#                 key = '6bd32199cdfca969f81ea9b636fd4182dc49228b',
#                 secret = VIMEO_SECRET_KEY
#             )
#             file_data = request.FILES["file_data"]
#             path = file_data.temporary_file_path()
#             try:
#                 vimeo_authorization_url = v.auth_url(
#                     ['private'],
#                     'http://127.0.0.1:8000/',
#                     1
#                 )
#                 name = form.author.username + "→" + form.client.username
#                 description = "password : " + form.article_password + "\n" + "Title : " + form.title + "\n" + form.description
#                 video_uri = v.upload(path, data={'name': name, 'description': description})
#                 v.patch(video_uri, data={'privacy': {'view': 'password', 'download': False}, 'password': form.article_password})
#                 video_data = v.get(video_uri + '?fields=link').json()
#                 video_url = video_data['link']
#                 video_id = parse("https://vimeo.com/{id}", video_url)

#                 #            headers = {'Content-Type': 'application/json; charset=utf-8'}
#                 #            content1 = requests.get('https://vimeo.com/api/oembed.json', params=params1, headers=headers)
#                 #            print('"{}" has been uploaded to {}'.format(file_data, video_data['link']))

#                 embedurl = "<div style = 'padding:56.34% 0 0 0;position:relative;'><iframe src = 'https://player.vimeo.com/video/{0}?badge=0&amp;autopause=0&amp;player_id=0&amp;app_id=58479' frameborder = '0' allow = 'autoplay; fullscreen; picture-in-picture' allowfullscreen style = 'position:absolute;top:0;left:0;width:100%;height:100%;' title={1}></iframe></div><script src = 'https://player.vimeo.com/api/player.js'></script>".format(video_id["id"], form.title)
#                 form.title = name
#                 form.description=description
#                 form.embedurl = embedurl

#                 #제작중으로 승급
#                 orderitem = form.orderitem
#                 orderitem.ordered_detail = 2
#                 orderitem.save()
#                 # 결제 -> 판매자창 -> 비디오 업로드 -> 주문자창 자동화 FLOW 작업중
#                 # client_order = Order.Objects.filter(user=form_article.client)
#                 # for a in client_order:

#                 #video 모델 article 저장!
#                 form.save()
#                 context = {
#                     'order_list': order_list,
#                 }
#                 messages.success(request, "비디오 업로드가 완료되었습니다. 팬분께 비디오를 전달해드릴게요!")
#                 return render(request, 'account/mypage.html', context)

#             except vimeo.exceptions.VideoUploadFailure as e:
#                 messages.info(request, "업로드에 실패하였습니다.")

#             finally:
#                 file_data.close()  # Theoretically this should remove the file
#                 if os.path.exists(path):
#                     os.unlink(path)  # But this will do it, barring permissions

#         messages.info(request, "업로드에 문제가 생겼습니다.")
#         return render(request, 'account/mypage.html', None)





# def myvideopage(request, pk):
#     user = get_object_or_404(User, pk=pk)
#     order = Order.objects.filter(user=request.user, ordered=True)
#     article = Article.objects.filter(client=request.user)

#     context = {
#         'user': user,
#         'order': order,
#         'article':article
#     }
#     if request.method == 'POST':

#         form = seller_upload(request.POST, request.FILES)
#         if form.is_valid():
#             form = form.save(commit=False)
#             form.user = request.user
#             form.save()

#         return render(request, 'account/myvideopage.html', context)
#     else:
#         form = seller_upload()
#        # order = Order.objects.filter(user=request.user, ordered=True)
#         context = {
#             'user': user,
#             'form': form,
#             'order': order,
#             'article' : article
#         }
#         return render(request, 'account/myvideopage.html', context)


#     #return render(request, 'account/mypage.html', context)


# def payment_complete(request):
#     messages.success(request, "Your order was successful!")
#     qs = Order.objects.filter(user=request.user, ordered=True).order_by('-ordered_date')
#     order_complete = qs[0]
#     context={
#         'order': order_complete
#     }
#     return render(request, "payment_complete.html", context)

# def special_product(request, pk, orderitem_pk):
#     user = get_object_or_404(User, pk=pk)
#     orderitem = get_object_or_404(OrderItem, pk=orderitem_pk, user=user)
#     return redirect("core:product", slug=orderitem.item.slug)

# @login_required
# def like_album(request, pk):
#     like_item = request.user.like_item.all()
#     if like_item.exists():
#         context={
#             'like_item':like_item
#         }
#         return render(request, 'account/like_album.html', context)
#     else:
#         messages.info(request, "좋아하는 상품이 없습니다. 이제부터 좋아해 보시는건 어떨까요?")
#         return redirect('core:product_list')

# @login_required
# def like_artist(request, pk):
#     like_artist=request.user.userprofile.followings.all()
#     if like_artist.exists():
#         context={
#             'like_artist':like_artist
#         }
#         return render(request, 'account/like_artist.html', context)

#     else:
#         messages.info(request, "좋아하는 아티스트가 없습니다. 이제부터 좋아해 보시는건 어떨까요?")
#         return redirect('core:artist_profile')

# @login_required
# def specialalbum_add_to_cart(request, pk, orderitem_pk):

#     orderitem=get_object_or_404(OrderItem, pk=orderitem_pk, user= request.user)
#     orderitem.author=orderitem.item.user
#     item, created = Item.objects.get_or_create(
#         title = orderitem.item.title + "의 스페셜 에디션",
#         description = orderitem.item.title + "\n" + orderitem.item.user.username + "아티스트님이 특별한 추억을 실물로 만들어 보내드릴게요!",
#         slug = orderitem.item.slug + "special",
#         onlyforspecial=True,
#         user=orderitem.item.user,
#         price=orderitem.item.special_price,
#         discount_price = orderitem.item.discount_special_price,
#         image = orderitem.item.image,
#         video = orderitem.item.video
#     )
#     item.price = orderitem.item.special_price
#     item.discount_price = orderitem.item.discount_special_price


#     order_item, created = OrderItem.objects.get_or_create(
#         item=item,
#         user=request.user,
#         ordered=False,
#         author=item.user
#     )
#     order_qs = Order.objects.filter(user=request.user, ordered=False)
#     if order_qs.exists():
#         order = order_qs[0]
#         order.pre_request = orderitem.item.user.username + "아티스트님의 Speical Edition 주문 중입니다."
#         order.save()
#         # check if the order item is in the order
#         if order.items.filter(item__slug=item.slug).exists():
#             order_item.quantity += 1
#             order_item.save()
#             messages.info(request, "This item quantity was updated.")
#             return redirect("core:checkout")
#         else:
#             order.items.add(order_item)
#             messages.info(request, "This item was added to your cart.")
#             return redirect("core:checkout")
#     else:
#         ordered_date = timezone.now()
#         order = Order.objects.create(
#             user=request.user, ordered_date=ordered_date)
#         order.pre_request = orderitem.item.user.username + "아티스트님의 Speical Edition 주문 중입니다."
#         order.save()
#         order.items.add(order_item)
#         messages.info(request, "This item was added to your cart.")
#         return redirect("core:checkout")


#     return redirect("/")




# def myorder(request, pk):
#     user = get_object_or_404(models.Users, pk=pk)
#     print(user)
#     order = Order.objects.filter(user=request.user, ordered=True)
#     order_list = Order.objects.filter(user=request.user, ordered=False)
#     context = {
#         'user': user,
#         'order': order,
#         'order_list' : order_list
#     }
#     return render(request, 'account/myorder.html', context)


# def fake_mypage(request, pk):
#     user = get_object_or_404(User, pk=pk)
#     order = Order.objects.filter(user=request.user, ordered=True)
#     order_list = Order.objects.filter(user=request.user, ordered=False)
#     context = {
#         'user': user,
#         'order': order,
#         'order_list' : order_list
#     }
#     if request.method == 'POST':

#         form = Article_uploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             form = form.save(commit=False)
#             form.user = request.user
#             form.save()

#         return render(request, 'account/mypage.html', None)
#     else:
#         form = Article_uploadForm(user)
#        # order = Order.objects.filter(user=request.user, ordered=True)
#         context = {
#             'user': user,
#             'form': form,
#             'order': order,
#             'order_list':order_list
#         }
#         return render(request, 'account/mypage.html', context)


#     #return render(request, 'account/mypage.html', context)

# def aran(request):
#     return render(request, "aran/aran.html", None)


# def video_new(request):
#     if request.method == 'POST':
#         #title = request.POST['title']
#         #video = request.POST['video']

#         form = UploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             form = form.save(commit=False)
#             form.user = request.user
#             form.save()
#             return redirect("core:video_list")
#     else:
#         form = UploadForm()
#         return render(request, 'videos/video_new.html', {'form': form})


# #하드코딩... 실험적으로 해보고 request.GET.get('next','') 으로 httpresponseredirect 해서 뒤로가기해라...
# @login_required()
# def like_item(request, pk, select):
# #    if request.method == 'POST':
#         item = get_object_or_404(Item, pk=pk)
#         if request.user in item.like_user.all():
#             item.like_user.remove(request.user)
#             if(select==1):
#                 return redirect("core:product_list")
#             elif(select==2):
#                 return redirect("core:product", item.slug)
#             else:
#                 return redirect("core:home")
#         else:
#             item.like_user.add(request.user)
#             if(select==1):
#                 return redirect("core:product_list")
#             elif(select==2):
#                 return redirect("core:product", item.slug)
#             else:
#                 return redirect("core:home")

# @login_required()
# def follow_userprofile(request, pk):
#         next = request.GET.get('next','/')
#         target_userprofile = get_object_or_404(UserProfile, pk=pk)

#         # 언팔
#         if request.user.userprofile in target_userprofile.followers.all():
#             target_userprofile.followers.remove(request.user.userprofile)
#             request.user.userprofile.followings.remove(target_userprofile)

#         # 팔로우
#         else:
#             target_userprofile.followers.add(request.user.userprofile)
#             request.user.userprofile.followings.add(target_userprofile)

#         return HttpResponseRedirect(next)

# @login_required()
# def product_review(request, pk):
# #    if request.method == 'POST':
#         item = get_object_or_404(Item, pk=pk)
#         comment = CommentForm(request.POST)
#         if comment.is_valid():
#             comment = comment.save(commit=False)
#             comment.user = request.user
#             comment.item = item
#             comment.save()
#         return redirect("core:product", item.slug)


# def video_list(request):
#     video_list = Video.objects.all()
#     return render(request, 'videos/video.html', {'video_list': video_list})

# def seller_item_new(request):
#     if request.method == 'POST':
#         title = request.POST['title']
#         text = request.POST['text']
#         image = request.POST['image']
#         video = request.POST['video']
#         form = seller_upload(request.POST, request.FILES)
#         if form.is_valid():
#             form.user=request.user
#             form.save()
#             return redirect("core:mypage")
#     else:
#         form = seller_upload()
#         return render(request, 'mypage/mypage_upload.html', {'form':form})

# def seller_item_list(request):
#     context = {
#         'title' : Article.title.object.all(),
#         'text': Article.text.object.all(),
#         'video': Article.video.object.all(),
#         'image': Article.image.object.all()
#     }

#     return render(request, 'mypage.html', {'seller_item_list': context})




# def create_ref_code():
#     return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


# def products(request):
#     context = {
#         'items': Item.objects.all()
#     }
#     return render(request, "products.html", context)


# def is_valid_form(values):
#     valid = True
#     for field in values:
#         if field == '':
#             valid = False
#     return valid


# class CheckoutView(View):
#     def get(self, *args, **kwargs):
#         try:
#             order = Order.objects.get(user=self.request.user, ordered=False)
#             form = CheckoutForm()
#             context = {
#                 'form': form,
#                 'couponform': CouponForm(),
#                 'order': order,
#                 'DISPLAY_COUPON_FORM': True
#             }

#             address_qs = Address.objects.filter(
#                 user=self.request.user,
#                 address_type='S',
#                 default=True
#             )
#             if address_qs.exists():
#                 context.update(
#                     {'default_address': address_qs[0]})

#             special_address_qs = Address.objects.filter(
#                 user=self.request.user,
#                 address_type='B',
#                 default=True
#             )
#             if special_address_qs.exists():
#                 context.update(
#                     {'default_special_address': special_address_qs[0]})
#             return render(self.request, "checkout.html", context)

#         except ObjectDoesNotExist:
#             messages.info(self.request, "You do not have an active order")
#             return redirect("core:home")


#     def post(self, *args, **kwargs):
#         form = CheckoutForm(self.request.POST or None)
#         try:
#             order = Order.objects.get(user=self.request.user, ordered=False)
#             if form.is_valid():
#                 use_default_address = form.cleaned_data.get(
#                     'use_default_address')
#                 if use_default_address:
#                     print("Using the default request")
#                     address_qs = Address.objects.filter(
#                         user=self.request.user,
#                         address_type='S',
#                         default=True
#                     )
#                     if address_qs.exists():
#                         address = address_qs[0]
#                         order.address = address
#                         order.save()
#                     else:
#                         messages.info(
#                             self.request, "No default request available")
#                         return redirect('core:checkout')
#                 else:
#                     print("User is entering a new request")
#                     email = form.cleaned_data.get(
#                         'email')
#                     request = form.cleaned_data.get(
#                         'request')
#                     phone = form.cleaned_data.get(
#                         'phone')
#                     zip = form.cleaned_data.get('zip')

#                     if is_valid_form([email, request, phone, zip]):
#                         address = Address(
#                             user=self.request.user,
#                             email=email,
#                             request=request,
#                             phone=phone,
#                             zip=zip,
#                             address_type='S'
#                         )
#                         address.save()

#                         order.address = address
#                         order.save()

#                         set_default_address = form.cleaned_data.get(
#                             'set_default_address')
#                         if set_default_address:
#                             address.default = True
#                             address.save()

#                     else:
#                         messages.info(
#                             self.request, "Please fill in the required request fields")
#                         return redirect('core:checkout')

#                 use_default_special_address = form.cleaned_data.get(
#                     'use_default_special_address')
#                 same_special_address = form.cleaned_data.get(
#                     'same_special_address')

#                 if same_special_address:
#                     # special_address = address
#                     # special_address.pk = None
#                     # special_address.save()
#                     # special_address.address_type = 'B'
#                     # special_address.save()
#                     # order.special_address = special_address
#                     # order.save()
#                     order.special_address = None
#                     order.save()

#                 elif use_default_special_address:
#                     print("Using the default special request")
#                     address_qs = Address.objects.filter(
#                         user=self.request.user,
#                         address_type='B',
#                         default=True
#                     )
#                     if address_qs.exists():
#                         special_address = address_qs[0]
#                         order.special_address = special_address
#                         order.save()
#                     else:
#                         messages.info(
#                             self.request, "No default special request available")
#                         return redirect('core:checkout')
#                 else:
#                     print("User is entering a new special request")
#                     s_email = form.cleaned_data.get(
#                         's_email')
#                     s_request = form.cleaned_data.get(
#                         's_request')
#                     s_phone = form.cleaned_data.get(
#                         's_phone')
#                     s_zip = form.cleaned_data.get('s_zip')

#                     if is_valid_form([s_email, s_phone, s_zip, s_request]):
#                         special_address = Address(
#                             user=self.request.user,
#                             email=s_email,
#                             request=s_request,
#                             phone=s_phone,
#                             zip=s_zip,
#                             address_type='B'
#                         )
#                         special_address.save()

#                         order.special_address = special_address
#                         order.save()

#                         set_default_special_address = form.cleaned_data.get(
#                             'set_default_special_address')
#                         if set_default_special_address:
#                             special_address.default = True
#                             special_address.save()




#                     else:
#                         messages.info(
#                             self.request, "특별요청 사항 없음 버튼을 눌러주세요")
#                         return redirect('core:checkout')

#                 payment_option = form.cleaned_data.get('payment_option')
#                 order.PG = payment_option
#                 order.save()
#                 if payment_option == 'T':
#                     return redirect('core:payment', payment_option='toss')
#                 elif payment_option == 'P':
#                     return redirect('core:payment', payment_option='paypal')
#                 elif payment_option == 'K':
#                     return redirect('core:payment', payment_option='kakao')
#                 else:
#                     messages.warning(
#                         self.request, "Invalid payment option selected")
#                     return redirect('core:checkout')
#             else:
#                 messages.warning(
#                     self.request, "적절하지 않은 형식입니다. 형식을 맞춰서 기입해주세요")
#                 return redirect('core:checkout')
#         except ObjectDoesNotExist:
#             messages.warning(self.request, "You do not have an active order")
#             return redirect("core:order-summary")



# class PaymentView(View):
#     def get(self, *args, **kwargs):
#         order = Order.objects.get(user=self.request.user, ordered=False)
#         # if order.special_address:
#         context = {
#             'order': order,
#             'DISPLAY_COUPON_FORM': False
#            # 'STRIPE_PUBLIC_KEY' : settings.STRIPE_PUBLIC_KEY
#         }
#         userprofile = self.request.user.userprofile
#         # if userprofile.one_click_purchasing:
#         #     # fetch the users card list
#         #     cards = stripe.Customer.list_sources(
#         #         userprofile.stripe_customer_id,
#         #         limit=3,
#         #         object='card'
#         #     )
#         #     card_list = cards['data']
#         #     if len(card_list) > 0:
#         #         # update the context with the default card
#         #         context.update({
#         #             'card': card_list[0]
#         #         })
#         return render(self.request, "payment.html", context)
#         # else:
#         #     messages.warning(
#         #         self.request, "You have not added a billing address")
#         #     return redirect("core:checkout")


#     def post(self, request, *args, **kwargs):
#         data = request.body
#         data = data.decode('utf-8')

#         if data[8] == "t":

#             order = Order.objects.get(user=self.request.user, ordered=False)
#             #form = PaymentForm(self.request.POST)
#             userprofile = UserProfile.objects.get(user=self.request.user)
#             #if form.is_valid():
#             #token = form.cleaned_data.get('stripeToken')
#             #save = form.cleaned_data.get('save')
#             #use_default = form.cleaned_data.get('use_default')

#             # if save:
#             #     if userprofile.stripe_customer_id != '' and userprofile.stripe_customer_id is not None:
#             #         customer = stripe.Customer.retrieve(
#             #             userprofile.stripe_customer_id)
#             #         customer.sources.create(source=token)
#             #
#             #     else:
#             #         customer = stripe.Customer.create(
#             #             email=self.request.user.email,
#             #         )
#             #         customer.sources.create(source=token)
#             #         userprofile.stripe_customer_id = customer['id']
#             #         userprofile.one_click_purchasing = True
#             #         userprofile.save()





#                 # if use_default or save:
#                 #     # charge the customer because we cannot charge the token more than once
#                 #     charge = stripe.Charge.create(
#                 #         amount=amount,  # cents
#                 #         currency="usd",
#                 #         customer=userprofile.stripe_customer_id
#                 #     )
#                 # else:
#                 #     # charge once off on the token
#                 #     charge = stripe.Charge.create(
#                 #         amount=amount,  # cents
#                 #         currency="usd",
#                 #         source=token
#                 #     )

#             # create the payment



#             payment = Payment()
#             #payment.stripe_charge_id = charge['id']
#             payment.user = self.request.user
#             payment.amount = order.get_total()
#             payment.save()

#             # assign the payment to the order

#             order_items = order.items.all()
#             order_items.update(ordered=True, ordered_detail=1)
#             for item in order_items:
#                 item.save()

#             order.ordered = True
#             order.payment = payment
#             order.user = self.request.user
#             order.ref_code = create_ref_code()
#             order.save()

#             messages.success(self.request, "Your order was successful!")

#             return render(self.request, "payment_complete.html", {'order' : order})

#         else:
#             messages.warning(
#                 self.request, "결제가 처리되지 않았습니다. 다시한번 확인해주세요")
#             return redirect("core:checkout")

# class Artist_HomeView(ListView):
#     model = Item
#     paginate_by = 20
#     template_name = "artist_home.html"
#     # def get_context_data(self, **kwargs):
#     #     context = super(Artist_HomeView, self).get_context_data(**kwargs)
#     #     if self.request.user.is_authenticated:
#     #         context['order_list'] = Order.objects.filter(user=self.request.user, ordered=False)
#     #     return context

# class fake_HomeView(ListView):

#     model = Item
#     paginate_by = 8
#     template_name = "home.html"
#     form_class = LForm

#     # def get_context_data(self, **kwargs):
#     #     context = super(HomeView, self).get_context_data(**kwargs)
#     #     if self.request.user.is_authenticated:
#     #         context['order_list'] = Order.objects.filter(user=self.request.user, ordered=False)
#     #     return context

# class artist_profile(ListView):

#     model = UserProfile
#     paginate_by = 8
#     template_name = "artist_profile/artist_profile.html"

#     # def get_context_data(self, **kwargs):
#     #     context = super(artist_profile, self).get_context_data(**kwargs)
#     #     if self.request.user.is_authenticated:
#     #         context['order_list'] = Order.objects.filter(user=self.request.user, ordered=False)
#     #
#     #     return context


# class MD_artist_profile(ListView):
#     mdpick = ""
#     def get(self, request, *args, **kwargs):
#         self.mdpick = request.GET.get('mdpick')
#         return super(MD_artist_profile, self).get(request, *args, **kwargs)

#     model = UserProfile
#     paginate_by = 8
#     template_name = "artist_profile/artist_profile.html"

#     #    User = get_user_model()
#     def get_context_data(self, **kwargs):
#         context = super(MD_artist_profile, self).get_context_data(**kwargs)
#         sm_mdpick = get_object_or_404(SM_MDPICK, title=self.mdpick)
#         context['mdpick'] = self.mdpick
#         context['object_list'] = sm_mdpick.artists.all()
#         return context


# def artist_profile_detail(request, pk):
#     userprofile = get_object_or_404(UserProfile, pk=pk)
#     context = {
#         'userprofile': userprofile
#     }
#     return render(request, 'artist_profile/artist_profile_detail.html', context)


# class myvideolist(ListView):
#     model = Article
#     paginate_by = 8
#     template_name = "myvideolist.html"

#     # def get_context_data(self, **kwargs):
#     #     context = super(myvideolist, self).get_context_data(**kwargs)
#     #     if self.request.user.is_authenticated:
#     #         context['order_list'] = Order.objects.filter(user=self.request.user, ordered=False)
#     #     return context

# class OrderSummaryView(LoginRequiredMixin, View):
#     def get(self, *args, **kwargs):
#         try:
#             order = Order.objects.get(user=self.request.user, ordered=False)
#             context = {
#                 'object': order
#             }
#             context['order_list'] = Order.objects.filter(user=self.request.user, ordered=False)
#             return render(self.request, 'order_summary.html', context)
#         except ObjectDoesNotExist:
#             messages.warning(self.request, "You do not have an active order")
#             return redirect("/")

# class ItemListView(ListView):

#     model = Item
#     paginate_by = 8
#     template_name = "product_list.html"
#     User = get_user_model()
#     def get_context_data(self, **kwargs):
#         context = super(ItemListView, self).get_context_data(**kwargs)
#         if self.request.user.is_authenticated:
#             context['order_list'] = Order.objects.filter(user=self.request.user, ordered=False)
#         context['artist_list'] = User.objects.filter(is_staff=True)
#         return context

# class MD_ItemListView(ListView):
#     mdpick=""
#     def get(self, request, *args, **kwargs):
#         self.mdpick=request.GET.get('mdpick')
#         return super(MD_ItemListView, self).get(request, *args, **kwargs)

#     model = Item
#     paginate_by = 8
#     template_name = "product_list.html"
#     User = get_user_model()
#     def get_context_data(self, **kwargs):
#         context = super(MD_ItemListView, self).get_context_data(**kwargs)
#         sm_mdpick = get_object_or_404(SM_MDPICK, title=self.mdpick)
#         context['artist_list'] = User.objects.filter(is_staff=True)
#         context['mdpick'] = self.mdpick
#         context['object_list'] = sm_mdpick.items.all()
#         return context

# class ItemDetailView(FormMixin,DetailView):
#     form_class = CommentForm
#     model = Item
#     template_name = "product.html"
#     # def get_context_data(self, **kwargs):
#     #     context = super(ItemDetailView, self).get_context_data(**kwargs)
#     #     if self.request.user.is_authenticated:
#     #         context['order_list'] = Order.objects.filter(user=self.request.user, ordered=False)
#     #     return context

# class customer_ItemDetailView(FormMixin,DetailView):

#     form_class = passwordForm
#     model = Article
#     template_name = "customer_password.html"
#     def post(self, request, *args, **kwargs ):
#         this_slug = get_object_or_404(Article, slug=self.kwargs['slug'])
#         form_class = passwordForm(request.POST)
#         if form_class.is_valid():
#             password = form_class.cleaned_data.get('password')
#             print(password)
#             model = Article.objects.filter(slug=this_slug)
#             model = model[0]
#             print(model)
#             if model.article_password == password:
#                 return render(self.request, "customer_product.html", {'object': model} )
#             else:
#                 messages.info(request, "비밀번호가 잘못되었습니다")
#                 return redirect("core:myvideolist")
#         else :
#             messages.info(request, "입력이 잘못되었습니다")
#             return redirect("core:myvideolist")
#     # def get_context_data(self, **kwargs):
#     #     context = super(customer_ItemDetailView, self).get_context_data(**kwargs)
#     #     if self.request.user.is_authenticated:
#     #         context['order_list'] = Order.objects.filter(user=self.request.user, ordered=False)
#     #     return context


# class Artist_ItemDetailView(DetailView):
#     model = Item
#     template_name = "product.html"
#     # def get_context_data(self, **kwargs):
#     #     context = super(HomeView, self).get_context_data(**kwargs)
#     #     if self.request.user.is_authenticated:
#     #         context['order_list'] = Order.objects.filter(user=self.request.user, ordered=False)
#     #     return context


# @login_required
# def direct_add_to_cart(request, slug):
# #    direct_message = CommentForm(request.POST)
# #    if direct_message.is_valid():
# #        content = direct_message.cleaned_data['content']
# #        item = get_object_or_404(Item, slug=slug)
# #        order_item, created = OrderItem.objects.get_or_create(
# #            item=item,
# #            user=request.user,
# #            ordered=False
# #        )
#     if request.method == 'POST':
#         content = request.POST.get('pre_request')
#         item = get_object_or_404(Item, slug=slug)
#         order_item, created = OrderItem.objects.get_or_create(
#             item=item,
#             user=request.user,
#             ordered=False,
#             author=item.user
#         )


#         order_qs = Order.objects.filter(user=request.user, ordered=False)
#         if order_qs.exists():
#             order = order_qs[0]
#             order.pre_request = content
#             order.save()
#             # check if the order item is in the order
#             if order.items.filter(item__slug=item.slug).exists():
#                 order_item.quantity += 1
#                 order_item.save()
#                 messages.info(request, "This item quantity was updated.")
#                 return redirect("core:checkout")
#             else:
#                 order.items.add(order_item)
#                 messages.info(request, "This item was added to your cart.")
#                 return redirect("core:checkout")
#         else:
#             ordered_date = timezone.now()
#             order = Order.objects.create(
#                 user=request.user, ordered_date=ordered_date)
#             order.pre_request = content
#             order.save()
#             order.items.add(order_item)
#             messages.info(request, "This item was added to your cart.")
#             return redirect("core:checkout")


#     return redirect("core:product")


# @login_required
# def add_to_cart(request, slug):
#     item = get_object_or_404(Item, slug=slug)
#     order_item, created = OrderItem.objects.get_or_create(
#         item=item,
#         user=request.user,
#         ordered=False,
#         author=item.user
#     )
#     order_qs = Order.objects.filter(user=request.user, ordered=False)
#     if order_qs.exists():
#         order = order_qs[0]
#         # check if the order item is in the order
#         if order.items.filter(item__slug=item.slug).exists():
#             order_item.quantity += 1
#             order_item.save()
#             messages.info(request, "This item quantity was updated.")
#             return redirect("core:order-summary")
#         else:
#             order.items.add(order_item)
#             messages.info(request, "This item was added to your cart.")
#             return redirect("core:order-summary")
#     else:
#         ordered_date = timezone.now()
#         order = Order.objects.create(
#             user=request.user, ordered_date=ordered_date)
#         order.items.add(order_item)
#         messages.info(request, "This item was added to your cart.")
#         return redirect("core:order-summary")


# @login_required
# def remove_from_cart(request, slug):
#     item = get_object_or_404(Item, slug=slug)
#     order_qs = Order.objects.filter(
#         user=request.user,
#         ordered=False
#     )
#     if order_qs.exists():
#         order = order_qs[0]
#         # check if the order item is in the order
#         if order.items.filter(item__slug=item.slug).exists():
#             order_item = OrderItem.objects.filter(
#                 item=item,
#                 user=request.user,
#                 ordered=False,
#                 author=item.user
#             )[0]
#             order.items.remove(order_item)
#             order_item.delete()
#             messages.info(request, "This item was removed from your cart.")
#             return redirect("core:order-summary")
#         else:
#             messages.info(request, "This item was not in your cart")
#             return redirect("core:product", slug=slug)
#     else:
#         messages.info(request, "You do not have an active order")
#         return redirect("core:product", slug=slug)


# @login_required
# def remove_single_item_from_cart(request, slug):
#     item = get_object_or_404(Item, slug=slug)
#     order_qs = Order.objects.filter(
#         user=request.user,
#         ordered=False,
#         author=item.user
#     )
#     if order_qs.exists():
#         order = order_qs[0]
#         # check if the order item is in the order
#         if order.items.filter(item__slug=item.slug).exists():
#             order_item = OrderItem.objects.filter(
#                 item=item,
#                 user=request.user,
#                 ordered=False
#             )[0]
#             if order_item.quantity > 1:
#                 order_item.quantity -= 1
#                 order_item.save()
#             else:
#                 order.items.remove(order_item)
#             messages.info(request, "This item quantity was updated.")
#             return redirect("core:order-summary")
#         else:
#             messages.info(request, "This item was not in your cart")
#             return redirect("core:product", slug=slug)
#     else:
#         messages.info(request, "You do not have an active order")
#         return redirect("core:product", slug=slug)


# def get_coupon(request, code):
#     try:
#         coupon = Coupon.objects.get(code=code)
#         return coupon
#     except ObjectDoesNotExist:
#         messages.info(request, "This coupon does not exist")
#         return redirect("core:checkout")



# class RequestRefundView(View):
#     def get(self, *args, **kwargs):
#         form = RefundForm()
#         context = {
#             'form': form
#         }
#         return render(self.request, "request_refund.html", context)

#     def post(self, *args, **kwargs):
#         form = RefundForm(self.request.POST)
#         if form.is_valid():
#             ref_code = form.cleaned_data.get('ref_code')
#             message = form.cleaned_data.get('message')
#             email = form.cleaned_data.get('email')
#             # edit the order
#             try:
#                 order = Order.objects.get(ref_code=ref_code)
#                 order.refund_requested = True
#                 order.save()

#                 # store the refund
#                 refund = Refund()
#                 refund.order = order
#                 refund.reason = message
#                 refund.email = email
#                 refund.save()

#                 messages.info(self.request, "Your request was received.")
#                 return redirect("core:request-refund")

#             except ObjectDoesNotExist:
#                 messages.info(self.request, "This order does not exist.")
#                 return redirect("core:request-refund")




def page_not_found_404(request,exception):
    messages.error(request, '잘못된 주소입니다. 올바른 주소값으로 다시 시도해주십시오.')
    return redirect('core:home')
    # return render(request, 'error/404.html', status=404)    

def server_error_500(request, *args, **argv):
    messages.error(request, '에러가 발생했습니다. 다시 시도해보시고, 같은 현상이 반복되면 하단 채봇을 통해 문의하시면 도와드리겠습니다.')    
    return render(request, 'error/500.html', status=500)

def permission_denied_403(request, exception=None):
    messages.error(request, '권한이 없습니다. 하단 채봇을 통해 문의하시면 도와드리겠습니다.')        
    return render(request, 'error/403.html', status=403)

def bad_request_400(request, exception=None):
    messages.error(request, '잘못된 요청입니다. 올바른 요청으로 다시 시도해주십시오.')
    return redirect('core:home')    
    # return render(request, 'error/400.html', status=400)
