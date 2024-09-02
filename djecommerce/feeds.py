from django.contrib.syndication.views import Feed
from auction.models import Placement
from datetime import datetime
from django.utils import feedgenerator
import urllib
class CorrectTypeFeed(feedgenerator.DefaultFeed):
    content_type = 'application/xml; charset=utf-8'

class PlacementFeed(Feed):
    title = '원앤온리 시간상품들'
    link = '/feeds/'
    description = '새로운 시간 상품들을 만나보세요'
    feed_type = CorrectTypeFeed

    def items(self):
        results = Placement.objects.exclude(placement_order=0).filter(placement_end__gte=datetime.now(),placement_start__lte=datetime.now()).order_by('placement_start')
        return results

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return "<![CDATA[<p>{}</p><img src='{}' alt='원앤온리'></img>".format(item.description, item.thumbnail.url)

    def item_enclosures(self, item):
        return [feedgenerator.Enclosure(item.thumbnail.url, str(item.thumbnail.size), 'image/{}'.format(item.thumbnail.url.split('.')[-1]))]