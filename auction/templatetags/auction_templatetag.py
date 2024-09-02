from django.utils import timezone as tz
from django import template
from auction.models import Placement, PlacementBid
from datetime import timedelta
register = template.Library()

@register.simple_tag
def get_top_3(p):    
    pbs=PlacementBid.objects.all().filter(placement=p).order_by('-offer')[:3]
    return pbs

@register.simple_tag
def count_bid(p):    
    pbs=PlacementBid.objects.all().filter(placement=p)
    return pbs.count()

@register.simple_tag
def yet_start_done(request, pk):
    placement = Placement.objects.get(pk=pk)
    now=tz.now()
    if placement.placement_start > now:
        if placement.placement_start - now > timedelta(hours=1):
            return "yet"
        else:
            #알람 설정 비활성화
            return "soon"

    elif placement.placement_start <= now and placement.placement_end >= now:
        # if placement.placement_type != 'crowdfunding':
        #     if placement.placement_win is not None:
        #         #낙찰대기중
        #         return 'pending'
        return "start"
    else:
        return "done"

@register.filter(name='removetag')
def _removetag(string, args=None):
    if args:
        args=args.split(',')
        for tag in args:
            string=string.replace(f"<{tag}>",'').replace(f"</{tag}>",'')
        # remove args tags only

    else:
        # remove all tags
        import re
        # as per recommendation from @freylis, compile once only
        CLEANR = re.compile('<.*?>')        
        string = re.sub(CLEANR, '', string)
        
    return string
