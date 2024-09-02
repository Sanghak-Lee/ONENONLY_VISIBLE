from django import template
from auction.models import Placement, PlacementBid

from core.models import Articles

register = template.Library()

@register.simple_tag
def sidebar():
  a=Articles.objects.exclude(category='5')
  p_articles=a.order_by('-n_hit')[:4]
  r_articles=a.order_by('-created')[:4]
  c={
    '0': a.count(),
    '1': 0,
    '2': 0,
    '3': 0,
    '4': 0,
    '5': 0,
  }  
  for aa in a:
    if aa.category == '1':
      c['1']+=1
    elif aa.category == '2':
      c['2']+=1
    elif aa.category == '3':
      c['3']+=1
    elif aa.category == '4':
      c['4']+=1
    elif aa.category == '5':
      c['5']+=1      
  context={
    'p_articles' : p_articles,
    'r_articles' : r_articles,
    'c' : c,
  }
  return context

@register.simple_tag
def menubar(request, **kwargs):
  if request.user.is_authenticated:
      try:
          p_list=[]
          pbds=PlacementBid.objects.filter(user_id=request.user.id).select_related('placement')
          for pbd in pbds:
              if pbd.placement.id not in p_list:
                  p_list.append(pbd.placement.id)
          my_placement=Placement.objects.filter(id__in=p_list)
          return my_placement
      except:
          pass