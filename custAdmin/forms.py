from django import forms

class GolfForm(forms.Form):
    year = forms.CharField()
    full_date = forms.DateField()
    course_name = forms.CharField()
    description = forms.CharField()
    events = [forms.DateField() for _ in range(3)]