from django import forms
from django.conf import settings
from django.db.models import fields
from allauth.account.forms import LoginForm
from .models import Partnership, Posts, Comments, Articles, Article_Comments
from user.models import Users
from artist.models import Artists, Reviews


class DateTimeLocalField(forms.DateTimeField):
    # Set DATETIME_INPUT_FORMATS here because, if USE_L10N 
    # is True, the locale-dictated format will be applied 
    # instead of settings.DATETIME_INPUT_FORMATS.
    # See also: 
    # https://developer.mozilla.org/en-US/docs/Web/HTML/Date_and_time_formats
     
    input_formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f", 
        "%Y-%m-%dT%H:%M:%S:%f",
        "%Y-%m-%dT%H:%M",
        '%Y-%m-%d %H:%M:%S',    # '2006-10-25 14:30:59'
        '%Y-%m-%d %H:%M',       # '2006-10-25 14:30'
        '%Y-%m-%d',             # '2006-10-25'
        '%m/%d/%Y %H:%M:%S',    # '10/25/2006 14:30:59'
        '%m/%d/%Y %H:%M',       # '10/25/2006 14:30'
        '%m/%d/%Y',             # '10/25/2006'
        '%m/%d/%y %H:%M:%S',    # '10/25/06 14:30:59'
        '%m/%d/%y %H:%M',       # '10/25/06 14:30'
        '%m/%d/%y'             # '10/25/06'
    ]
class PartnershipForm(forms.ModelForm):
    class Meta:
        model = Partnership
        exclude = ['updated, created']
class Article_Form(forms.ModelForm):
    display_day=DateTimeLocalField()
    class Meta:
        model = Articles
        fields = ['category', 'text', 'title', 'thumbnail','badge','display_text', 'display_day', 'display_place']
    # def clean(self):
    #     cleaned_data = super().clean()
    #     for d in cleaned_data:
    #         print(d)

class Article_comment_Form(forms.ModelForm):
    class Meta:
        model = Article_Comments
        exclude = ['updated', 'parent_article_comment']

class Post_Form(forms.ModelForm):
    class Meta:
        model = Posts
        exclude = ['created']

class Comment_Form(forms.ModelForm):
    class Meta:
        model = Comments
        exclude = ['created']

class Review_Form(forms.ModelForm):
    class Meta:
        model = Reviews
        exclude = ['created']

class Artist_Form(forms.ModelForm):
    class Meta:
        model = Artists
        fields = ['avatar', 'K_name', 'E_name', 'instrument', 'bio_text', 'bio_video']
#'account_verify1','account_verify2','account_num','account_host','account_bank'

class User_Form(forms.ModelForm):
    class Meta:
        model = Users
        fields = ['email', 'avatar']




# #--------------------------------------------------
# class Article_uploadForm(forms.ModelForm):

#    class Meta:
#        model = Article
#        fields = ['video', 'title', 'description', 'article_password', 'client', 'orderitem']
# #    def __init__(self, user, *args, **kwargs):
# #        super(Article_uploadForm, self).__init__(*args, **kwargs)
# # user하는 중       self.fields['client'].queryset = settings.AUTH_USER_MODEL.objects.filter(pk=)
# #        self.fields['orderitem'].queryset = OrderItem.objects.filter(author=user, ordered=True, ordered_detail=1)

# class CustomLoginForm(LoginForm):

#     def get(self, *args, **kwargs):

#         # Add your own processing here.

#         # You must return the original result.
#         return super(CustomLoginForm, self).login(*args, **kwargs)

# class CommentForm(forms.ModelForm):
#     content = forms.CharField(
#                 label='댓글',
#                 widget=forms.Textarea(
#                         attrs={
#                             'rows': 2,
#                         }
#                     )
#             )
#     class Meta:
#         model = Comment
#         fields = ['content']

# class LForm(forms.Form):
#     password = forms.CharField(required=True)
#     username = forms.CharField(required=True)

# class passwordForm(forms.Form):
#     password = forms.CharField(required=True)

# class seller_upload(forms.ModelForm):
#     class Meta:
#         model = Item
#         fields = {'title', 'price', 'discount_price', 'category', 'label', 'description', 'image', 'video', 'slug','special_price','discount_special_price'}


# class UploadForm(forms.ModelForm):
#     class Meta:
#         model = Video
#         fields = {'title', 'video'}


# class CheckoutForm(forms.Form):
#     email = forms.CharField(required=False)
#     request = forms.CharField(required=False)
#     phone = forms.CharField(required=False)
#     zip = forms.CharField(required=False)

#     s_email = forms.CharField(required=False)
#     s_request = forms.CharField(required=False)
#     s_phone = forms.CharField(required=False)
#     s_zip = forms.CharField(required=False)

#     same_special_address = forms.BooleanField(required=False)
#     set_default_address = forms.BooleanField(required=False)
#     use_default_address = forms.BooleanField(required=False)
#     set_default_special_address = forms.BooleanField(required=False)
#     use_default_special_address = forms.BooleanField(required=False)


# class CouponForm(forms.Form):
#     code = forms.CharField(widget=forms.TextInput(attrs={
#         'class': 'form-control',
#         'placeholder': '쿠폰입력',
#         'aria-label': 'Recipient\'s username',
#         'aria-describedby': 'basic-addon2'
#     }))


# class RefundForm(forms.Form):
#     ref_code = forms.CharField()
#     message = forms.CharField(widget=forms.Textarea(attrs={
#         'rows': 4
#     }))
#     email = forms.EmailField()


# class PaymentForm(forms.Form):
#     stripeToken = forms.CharField(required=False)
#     save = forms.BooleanField(required=False)
#     use_default = forms.BooleanField(required=False)
