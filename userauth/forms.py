from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, SetPasswordForm

# class PasswordChangeForm(SetPasswordForm):
#     ...
#     def clean(self):
#         password1 = self.cleaned_data.get('password1')
#         password2 = self.cleaned_data.get('password2')
#         if password1 == password2:
#             raise forms.ValidationError('password mismatch')

# class GetUsernameForm(forms.Form):
#     username = 