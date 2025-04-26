
from django import forms
from .models import Fighter

class FighterComparisonForm(forms.Form):
    fighter1 = forms.ModelChoiceField(queryset=Fighter.objects.all(), label="Select First Fighter")
    fighter2 = forms.ModelChoiceField(queryset=Fighter.objects.all(), label="Select Second Fighter")
