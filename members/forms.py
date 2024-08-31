from django import forms
from django import forms
from .models import Member

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField()

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['surname', 'first_name', 'last_name', 'phone_number', 'birthdate', 'email', 'location_type']
        # Exclude the non-editable field
        exclude = ['date_of_registration', 'status']

