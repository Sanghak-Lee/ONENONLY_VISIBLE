from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from django.contrib.auth.admin import UserAdmin
from django import forms
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from . import models

@admin.register(models.Users)
class UserAdmin(UserAdmin):
    list_display=(
        'id',
        "date_joined",
        "is_artist",
        "username",
        "email",
        "password",
        "is_staff",
    )

    fieldsets = UserAdmin.fieldsets + (
    (None, {'fields': ('is_artist', 'avatar', 'encore','alarm','plike',)}),
    )
    ordering=['-last_login']


class CCForm(forms.ModelForm):
    class Meta:
        widgets = {
            'phone': PhoneNumberPrefixWidget(),
        }
@admin.register(models.Verification)
class VerificationAdmin(admin.ModelAdmin):
    readonly_fields = ('last_verified',)
    list_display=(
        'id',
        'user',
        'name',
        'phone',
    )
    list_display_link=(
        'id',
        'user',
        'name',
        'phone',
    )
    list_filter=(
        'id',
        'user',
        'name',
        'phone',
    )
    search_fields=(
        'id',
        'user__username',
        'name',
        'phone',
    )
    
@admin.register(models.UserPrivacy)
class UserPrivacyAdmin(admin.ModelAdmin):
    list_display=(
        'id',
        'user',
        'agreement_1',
        'agreement_2',
        'agreement_3',
        'agreement_4',        
    )
    list_display_link=(
        'id',
        'user',
        'agreement_1',
        'agreement_2',
        'agreement_3',
        'agreement_4',        
    )
    list_filter=(
        'id',
        'user',
        'agreement_1',
        'agreement_2',
        'agreement_3',
        'agreement_4',        
    )
    search_fields=(
        'id',
        'user__username',
        'agreement_1',
        'agreement_2',
        'agreement_3',
        'agreement_4',        
    )
@admin.register(models.AdminPhone)
class AdminPhoneAdmin(admin.ModelAdmin):
    def toggle_activate(modeladmin, request, queryset):
        for q in queryset:
            q.activate=not(q.activate)
            q.save()
    toggle_activate.short_description='알람 활성화/비활성화'

    list_display=(
        'label',
        'phone',
        'activate',
    )
    list_display_link=(
        'label',
        'phone',
        'activate',
    )
    list_filter=(
        'label',
        'phone',
        'activate',
    )
    search_fields=(
        'label',
        'phone',
        'activate',
    )
    actions=[toggle_activate]

# @admin.register(models.Users)
# class UserAuthAdmin(ModelAdmin):
#     list_display=(
#         'id',
#         'is_artist'
#         "date_joined",
#         "username",
#         "email",
#         "password",
#     )