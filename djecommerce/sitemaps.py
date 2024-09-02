from django.contrib.sitemaps import Sitemap
from auction.models import Placement
from datetime import datetime

class PlacementSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.8
    def items(self):
        results = Placement.objects.exclude(placement_order=0).filter(placement_end__gte=datetime.now(),placement_start__lte=datetime.now()).order_by('placement_start')
        return results
    def location(self,obj):
        return obj.get_absolute_url()
    def lastmod(self, obj):
        return obj.updated