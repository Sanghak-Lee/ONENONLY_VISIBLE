from django import forms
from django.contrib.admin.helpers import ActionForm
from auction.models import Placement

#ADMIN
class PlacementSelectForm(ActionForm):
    placement = forms.ModelChoiceField(queryset=Placement.objects.all(), required=False) 

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
class Admin_PlacementForm_Crowd(forms.ModelForm):
    placement_start=DateTimeLocalField()
    placement_end=DateTimeLocalField()
    d_day=DateTimeLocalField()
    class Meta:
        model = Placement
        fields = [
                "title",
                "description",
                "category",
                "rep",
                "duration",
                # "d_day",
                "d_place",
                "thumbnail",
                "m_banner_video_mp4",
                "pc_banner_video_mp4",
                "youtube_id",
                "image_1",
                "image_2",
                "image_3",
                "image_4",
                "image_5",                
                "detail_1_title",
                "detail_1",
                "detail_2_title",
                "detail_2",
                "detail_3_title",
                "detail_3",
                "detail_4_title",
                "detail_4",
                "detail_5_title",
                "detail_5",
                "detail_6_title",
                "detail_6",
                "etc_1",
                "etc_1_on",
                "placement_type",
                "placement_price",
                # "placement_start",
                # "placement_end",
                "is_encore",
                "unit_price",
                # 'deposit',
                "buy_limit",                
            ]
    def save(self, commit=True):
        m = super().save(commit=False)
        m.placement_start=self.cleaned_data.get('placement_start')
        m.placement_end=self.cleaned_data.get('placement_end')        
        m.d_day=self.cleaned_data.get('d_day')
        if commit:
            m.save()
        return m            
    # def clean(self):
    #     cleaned_data = super().clean()
    #     print(cleaned_data.get('placement_start'))
    #     for d in cleaned_data:
    #         print(d)
class Admin_PlacementForm(forms.ModelForm):
    placement_start=DateTimeLocalField()
    placement_end=DateTimeLocalField()
    d_day=DateTimeLocalField()
    class Meta:
        model = Placement
        fields = [
                "title",
                "description",
                "category",
                "rep",
                "duration",
                # "d_day",
                "d_place",
                "thumbnail",
                "m_banner_video_mp4",
                "pc_banner_video_mp4",
                "youtube_id",
                "image_1",
                "image_2",
                "image_3",
                "image_4",
                "image_5",                
                "detail_1_title",
                "detail_1",
                "detail_2_title",
                "detail_2",
                "detail_3_title",
                "detail_3",
                "detail_4_title",
                "detail_4",
                "detail_5_title",
                "detail_5",
                "detail_6_title",
                "detail_6",
                "etc_1",
                "etc_1_on",
                "placement_type",
                "placement_price",
                # "placement_start",
                # "placement_end",                
                "is_encore",
                "unit_price",
                "placement_start_price",
                "placement_estimated_price",
                "placement_buynow_price",
                "deposit",
                # "buy_limit",
            ]
    def save(self, commit=True):
        m = super().save(commit=False)
        m.placement_start=self.cleaned_data.get('placement_start')
        m.placement_end=self.cleaned_data.get('placement_end')        
        m.d_day=self.cleaned_data.get('d_day')
        if commit:
            m.save()
        return m
    # def clean(self):
    #     cleaned_data = super().clean()
    #     print(cleaned_data.get('placement_start'))        
    #     for d in cleaned_data:
    #         print(d)
            
    # def clean_placement_start(self):
    #     v=self.cleaned_data.get('placement_start')
    #     return datetime(v)
