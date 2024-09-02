from django.utils.translation import ugettext_lazy as _
from jet.dashboard import modules
from jet.dashboard.dashboard import Dashboard, AppIndexDashboard
# from jet.dashboard.dashboard_modules import google_analytics

class CustomIndexDashboard(Dashboard):
    columns = 3

    def init_with_context(self, context):
        #LinList
        self.available_children.append(modules.LinkList)
        self.children.append(modules.LinkList(
            _('Support'),
            children=[
                {
                    'title': _('채널톡 관리자'),
                    'url': 'https://desk.channel.io/#/channels/84903/user_chats/634fb90c8d7e19e544dd',
                    'external': True,
                },
                {
                    'title': _('아임포트 관리자'),
                    'url': 'https://admin.iamport.kr/',
                    'external': True,
                },
                {
                    'title': _('구글 애널리틱스'),
                    'url': 'https://analytics.google.com/analytics/web/?authuser=2#/p339616954/reports/intelligenthome?params=_u..nav%3Dmaui&collectionId=life-cycle',
                    'external': True,
                },
                {
                    'title': _('Sentry'),
                    'url': 'https://sentry.io/organizations/revenor-fs/issues/?project=6419887',
                    'external': True,
                },
                {
                    'title': _('비즈톡 관리자'),
                    'url': 'https://center.biztalk.co.kr/#/login',
                    'external': True,
                },
                {
                    'title': _('네이버 SMS 관리자'),
                    'url': 'https://console.ncloud.com/dashboard',
                    'external': True,
                },                
                {
                    'title': _('네이버 로그인 관리자'),
                    'url': 'https://developers.naver.com/apps/#/myapps/szEzIa93kDv4ItDDjZcv/overview',
                    'external': True,
                },
                {
                    'title': _('카카오 개발자 관리자'),
                    'url': 'https://developers.kakao.com/console/app/731629',
                    'external': True,
                },
                {
                    'title': _('카카오 채널 관리자'),
                    'url': 'https://center-pf.kakao.com/_kmkDb/dashboard',
                    'external': True,
                },
                {
                    'title': _('카카오 스토어 관리자'),
                    'url': 'https://shopping-sell.kakao.com/hub',
                    'external': True,
                },
            ],
            column=0,
            order=0
        ))

        #AppList
        self.children.append(modules.AppList(
            _('Applications'),
            exclude=('auth.*',),
            column=0,
            order=0
        ))

        #ModelList
        self.children.append(modules.ModelList(
            _('Models'),
            exclude=('auth.*',),
            column=0,
            order=0
        ))

        #RecentActions
        self.children.append(modules.RecentActions(
            _('Recent Actions'),
            10,
            column=0,
            order=0
        ))

        #Feed
        self.available_children.append(modules.Feed)        
        self.children.append(modules.Feed(
            _('Latest Django News'),
            feed_url='http://www.djangoproject.com/rss/weblog/',
            limit=5,
            column=0,
            order=0
        ))

        # #Google Analytics
        # self.available_children.append(google_analytics.GoogleAnalyticsVisitorsTotals)
        # self.available_children.append(google_analytics.GoogleAnalyticsVisitorsChart)
        # self.available_children.append(google_analytics.GoogleAnalyticsPeriodVisitors)