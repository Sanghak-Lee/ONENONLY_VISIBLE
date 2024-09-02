from django.urls import path
from . import views

app_name = 'auction'
urlpatterns = [

    #List
    path('list/', views.PlacementListView.as_view(), name='plv'),
    path('list/<int:pk>/', views.PlacementDetailView.as_view(), name='pdv'),
    path('list/bidding/<int:pk>/', views.BiddingDetailView.as_view(), name='pdv-bidding'),
    path('list/<int:pk>/admin/', views.AdminPlacementDetailView.as_view(), name='admin-pdv'),

    #OPEN, SECRET FUNDING
    path('bidding/<int:pk>/', views.BiddingView, name='bidding'),

    #CROWD FUNDING
    path('crowdfunding/<int:pk>/', views.CrowdFundingStart, name='crowdfundingstart'),

    #UTILS
    path('bidding/<int:pk>/refresh/', views.BiddingRefresh, name='bidding-refresh'),

    #Time Store
    path('timestore/', views.TimeStoreListView.as_view(), name='tlv'),
    path('timestore/<int:pk>/', views.TimeStoreDetailView.as_view(), name='tdv'),

    #Time Store
    path('timestore/', views.TimeStoreListView.as_view(), name='tlv'),
    path('timestore/<int:pk>/', views.TimeStoreDetailView.as_view(), name='tdv'),

    #Display View(파트너스)
    path('display/', views.DisplayListView.as_view(), name='dlv'),
    # path('display/<int:pk>/', views.DisplayDetailView.as_view(), name='ddv'),

    #Portfolio
    # path('portfolio/', views.AuctionArtistListView.as_view(), name='alv'),
    # path('portfolio/<slug:slug>/', views.AuctionArtistDetailView.as_view(), name='adv'),

    #Authorization
    # path('authorization/<int:pk>/', views.InvitationToAuctionAuthorization, name='invi-auth'),
    # path('NFTauthorization/', views.InvitationToAuctionAuthorization2, name='invi-auth-2'),

    #Alarm, Encore, Plike
    path('toggle/encore/', views.Toggle_Encore, name="encore"),
    path('toggle/alarm/', views.Toggle_Alarm, name="alarm"),
    path('toggle/plike/', views.Toggle_Plike, name="plike"),
]