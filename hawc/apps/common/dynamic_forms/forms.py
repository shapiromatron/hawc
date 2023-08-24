from django import forms
from models import CustomDataExtraction


class CustomDataExtractionForm(forms.ModelForm):
    model = CustomDataExtraction
