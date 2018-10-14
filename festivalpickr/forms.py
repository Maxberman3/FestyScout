from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    name = forms.CharField(max_length=50, required=True, help_text='Required')
    email = forms.EmailField(max_length=254, required=True, help_text='Required')
    city = forms.CharField(required=True, help_text='Required')
    state = forms.CharField(required=True, help_text='Required')
    zip_code = forms.CharField(min_length=5, max_length=5, required=True, help_text='Required')

    class Meta:
        model = User
        fields = ('username', 'name', 'email', 'city', 'state', 'zip_code', 'password1', 'password2', )
