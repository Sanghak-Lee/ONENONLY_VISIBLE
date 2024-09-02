from django.urls import path
from . import views
from django.views.generic.base import TemplateView

app_name = 'core'

urlpatterns = [
    #홈
    # path('', views.FakeHomeView.as_view(), name='home'),
    path('', views.HomeView.as_view(), name='home'),

    ########-------------
    # Article
    path('guide/', views.GuideTemplateView.as_view(), name='guide'),
    path('info-1/', TemplateView.as_view(template_name="article/auction/info/1.html"), name='info-1'),
    path('info-2/', TemplateView.as_view(template_name="article/auction/info/2.html"), name='info-2'),
    path('info-3/', TemplateView.as_view(template_name="article/auction/info/3.html"), name='info-3'),
    path('article/', views.ArticleListView.as_view(), name='article_list'),
    path('article/write/', views.ArticleWriteView.as_view(), name='article_write'),
    path('article/<int:pk>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('article/<int:pk>/update', views.ArticleUpdateView.as_view(), name='article_update'),
    path('article/<int:pk>/delete', views.ArticleDeleteView.as_view(), name='article_delete'),
    #마이페이지
    path('mypage/', views.MypageUserView.as_view(), name='user2'),
    path('mypage/user/', views.MypageUserView.as_view(), name='user'),
    path('mypage/user/info/', views.MypageUserInfoUpdateView.as_view(), name='userinfo'),
    path('mypage/user/info/password', views.UserPasswordChangeView.as_view(), name='userpw'),
    path('mypage/user/info/privacy', views.UserPrivacyToggleView.as_view(), name='userprivacy'),
    path('mypage/user/info/update', views.UserUpdateView.as_view(), name='userupdate'),
    path('mypage/user/deactivate', views.DeActivateUser, name='userdeactivate'),

    #설문지
    path('mypage/qna/<slug:slug>/<int:pk>', views.QuestionnaireCreateView.as_view(), name='qna'),
    #설문지(관리자)
    path('mypage/qna/<int:pk>/admin/', views.QuestionnaireAdminView.as_view(), name='admin-qna'),
    #구글 공통 설문지
    path('mypage/Gcommon-qna/<int:pk>/', views.GcommonQuestionnarieView.as_view(), name='Gcommon-qna'),
    #공통 설문지
    path('mypage/common-qna/<int:pk>/', views.CommonQuestionnaireCreateView.as_view(), name='common-qna'),
    #공통 설문지(관리자)
    path('mypage/common-qna/<int:pk>/admin/', views.CommonQuestionnaireAdminView.as_view(), name='admin-common-qna'),

    #QR 티켓
    path('ticket/<slug:type>/<int:pk>/', views.TicketView.as_view(), name='ticket'),
    #파트너십 제안
    path('partnership/', views.PartnershipCreateView.as_view(), name='partnership'),
    #회사소개 제안
    path('about/', views.AboutTemplateView.as_view(), name='about'),    
    #환불
    path('refund/<slug:slug>/<int:pk>', views.ToggleRefundView, name='togglerefund'),

    #장바구니
    path('add-orderitem/<int:pk>/<int:placement_id>', views.AddAuctionToOrderItem, name='AddAuctionToOrderItem'),
    path('remove-item-from-cart/<slug:type>/<int:pk>/', views.remove_from_cart_orderitem, name='remove_from_cart_orderitem'),

    #본인인증
    path('auth/', views.AjaxAuthView.as_view(), name='auth'),
    path('authsignup/', views.AuthSignUpView.as_view(), name='authsignup'),
    path('mobile/auth/', views.MobileAuthView.as_view(), name='mobile-auth'),
    # path('mobile/auth/', views.MobileAjaxAuthView.as_view(), name='mobile-auth'),
    # path('mobile/authsignup/', views.MobileAjaxAuthView.as_view(), name='mobile-auth'),    
    #Verify
    path('verify/', views.PhoneVerifyView.as_view(), name='verify'),

    #결제
    path('checkout/webhook/', views.CheckoutWebhookView, name='checkout_webhook'),    
    path('checkout/<slug:type>/<int:pk>/', views.CheckoutView.as_view(), name='checkout'),
    path('checkout/<slug:type>/<int:pk>/process/', views.CheckoutProcessView, name='checkout_process'),
    path('checkout/<slug:type>/<int:pk>/complete/', views.CheckoutCompleteView.as_view(), name='checkout_complete'),
    #쿠폰
    path('coupon/<slug:type>/<int:pk>/', views.AddCouponView, name='addcoupon')
    
    ########-------------



    # path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    # path('payment/complete', payment_complete, name='payment_complete'),
    # path('request-refund/', RequestRefundView.as_view(), name='request-refund'),

    # #팔로우,언팔
    # path('follow_unfollow/<int:pk>/', follow_userprofile, name='follow_userprofile'),

    # #좋아요 페이지
    # path('like_album/<int:pk>/', like_album, name='like_album'),
    # path('like_artist/<int:pk>/', like_artist, name='like_artist'),

    # #order
    # path('myorder/<int:pk>/', myorder, name='myorder'),
    # path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    # path('special_product/<int:pk>/<int:orderitem_pk>/', special_product, name='special_product')

]

