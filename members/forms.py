from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Member, Profile

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField()

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['surname', 'first_name', 'last_name', 'phone_number', 'birthdate', 'email', 'location_type']
        exclude = ['date_of_registration', 'status']

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone_number', 'birthdate', 'email', 'location_type', 'town_name', 'has_children', 'number_of_children']

class UserSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
