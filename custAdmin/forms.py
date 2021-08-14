from django import forms

class GolfForm(forms.Form):
    year = forms.CharField()
    full_date = forms.DateField()
    course_name = forms.CharField()
    description = forms.CharField()
    events = [forms.DateField() for _ in range(3)]

class FoursomeRegistration(forms.Form):
    date_code = forms.CharField()
    payment_id = forms.CharField()
    contact_email = forms.CharField()
    golf_1_fname = forms.CharField()
    golf_1_lname = forms.CharField()
    golf_2_fname = forms.CharField()
    golf_2_lname = forms.CharField()
    golf_3_fname = forms.CharField()
    golf_3_lname = forms.CharField()
    golf_4_fname = forms.CharField()
    golf_4_lname = forms.CharField()