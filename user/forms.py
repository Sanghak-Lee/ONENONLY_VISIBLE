from allauth.account.forms import SignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django import forms
from allauth.account.forms import SetPasswordField, PasswordField
class MyCustomSignupForm(SignupForm):
    agreement_1 = forms.BooleanField(required=False)
    agreement_2 = forms.BooleanField(required=False)
    agreement_3 = forms.BooleanField(required=False)
    agreement_4 = forms.BooleanField(required=False)

    def save(self, request):
        # Ensure you call the parent class's save.
        # .save() returns a User object.
        user = super().save(request)
        
        # Add your own processing here.

        # You must return the original result.
        return user
class MyCustomSocialSignupForm(SocialSignupForm):
    pass
    # password1 = SetPasswordField(max_length=12,label=("비밀번호"))
    # password2 = PasswordField(max_length=12, label=("비밀번호 재확인"))
    # def clean_password2(self):
    #     if ("password1" in self.cleaned_data and "password2" in self.cleaned_data):
    #         if (self.cleaned_data["password1"] != self.cleaned_data["password2"]):
    #             raise forms.ValidationError(("비밀번호와 재확인 비밀번호가 동일하지 않습니다. 다시 입력해주십시오."))
    #     return self.cleaned_data["password2"]

    # def signup(self, request, user):
    #     user.set_password(self.user, self.cleaned_data["password1"])
    #     user.save()