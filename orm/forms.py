from django import forms

class UploadForm(forms.Form):
    image = forms.ImageField(label='Upload Image', required=True)
    name = forms.CharField(label='Your Name', widget=forms.TextInput, max_length=255)
    code = forms.CharField(label='Exam Code', widget=forms.TextInput, max_length=255)
