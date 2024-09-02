from django import template

register = template.Library()

@register.filter(name='range')
def _range(_min, args=None):
    _max, _step = None, None
    if args:
        if not isinstance(args, int):
            _max, _step = map(int, args.split(','))
        else:
            _max = args
    args = filter(None, (_min, _max, _step))
    return range(*args)

@register.filter(name='multiply')
def _multiply(value, arg):
    return int(value * arg)

# @register.simple_tag
# def get_reviews(artist):
#     reviews = artist.review.all().order_by('-start_date')[:5]
#     return reviews  

# @register.simple_tag
# def percentage(artist, index, detail):
#     #index1,2,3,5 => calculate percentage of review socre
#     cnt = 0
#     if artist.review.all():
#         for s in artist.review.all():
#             if index == 5:
#                 if s.score == 5:
#                     cnt +=1
#                 else:
#                     pass
#             elif index == 4:
#                 if s.score == 4:
#                     cnt+=1
#                 else:
#                     pass
#             elif index == 3:
#                 if s.score == 3:
#                     cnt +=1
#                 else:
#                     pass                
#             elif index == 2:
#                 if s.score == 2:
#                     cnt +=1
#                 else:
#                     pass                
#             elif index == 1:
#                 if s.score == 1:
#                     cnt +=1
#                 else:
#                     pass                          
#         if detail == "on":            
#             return int(cnt) 
#         else :
#             return (cnt/artist.review.all().count())*100
#     else:
#         return 0

# @register.simple_tag(takes_context=True)
# def deliver_detail1(context):
#     request = context['request']
#     orderartist_list=context['orderartist_list']
#     ret = orderartist_list.filter(deliver_detail=1).count()
#     if ret:
#         return ret
#     else :
#         return 0

# @register.simple_tag(takes_context=True)
# def deliver_detail2(context):
#     request = context['request']
#     orderartist_list=context['orderartist_list']
#     ret = orderartist_list.filter(deliver_detail=2).count()
#     if ret:
#         return ret
#     else :
#         return 0    
  
# @register.filter
# def following_count(user):
#     if user.is_authenticated:
#         userprofile = UserProfile.objects.filter(user=user)
#         if userprofile.exists():
#             return userprofile[0].followings.count()
#     return 0

# @register.filter
# def follower_count(user):
#     if user.is_authenticated:
#         userprofile = user.userprofile
#         if userprofile.exists():
#             return userprofile.followers.count()
#     return 0

# @register.filter
# def like_count(user):
#     if user.is_authenticated:
#         item = user.like_item.all()
#         if item.exists():
#             return item.count()
#     return 0

# @register.simple_tag(takes_context=True)
# def get_order_list(context):
#     request = context['request']
#     return Order.objects.filter(user=request.user, ordered=False)
    