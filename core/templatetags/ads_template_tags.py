from django import template
from core.models import Articles

register = template.Library()

@register.simple_tag
def get_ads(**kwargs):
  ads=Articles.objects.filter(category=5).order_by('-display_day')

  #7개만
  try:
    ads=ads[:7]
  except:
    pass

  if ads.exists():
    return ads
  else:
    return None