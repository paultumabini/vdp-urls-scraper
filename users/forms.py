from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from .models import Profile


class UserRegisterForm(UserCreationForm):
    # Email is required for account communication and password reset flows.
    email = forms.EmailField(label='Email')
    password1 = forms.CharField(label='Enter password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        help_texts = {
            'username': None,
        }


class MyLogInForm(AuthenticationForm):
    # Widget attrs keep login UI consistent with the existing template design.
    username = forms.CharField(label='Username', widget=forms.TextInput(attrs={'style': 'margin:1rem 0 2rem', 'placeholder': 'Username'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'mb-4', 'placeholder': 'Password'}))

    error_messages = {
        'invalid_login': _("Invalid login. Note that both " "fields may be case-sensitive."),
        'inactive': _("This account is inactive."),
    }


class UserUpdateForm(forms.ModelForm):
    # Keep email editable from profile screen without exposing unrelated fields.
    email = forms.EmailField(label='Email')

    class Meta:
        model = User
        fields = ['username', 'email']
        help_texts = {
            'username': None,
        }


class ProfileUpdateForm(forms.ModelForm):
    image = forms.ImageField(label='', widget=forms.FileInput)
    # Hide native input and trigger via custom template control.
    image.widget.attrs['style'] = 'visibility: hidden'

    class Meta:
        model = Profile
        fields = ['image']
