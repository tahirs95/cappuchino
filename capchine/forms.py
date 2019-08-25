from django import forms
from django.contrib.auth.models import User
from django_starfield import Stars

class LoginForm(forms.Form):
    username = forms.CharField(label=' ', widget=forms.TextInput(attrs={'maxlength':150, 'placeholder':'Email'}))
    password = forms.CharField(label=' ',widget=forms.PasswordInput(attrs={'maxlength':150,'placeholder':'Password'}))

CHOICES = [('student','Student'),('teacher','Teacher')]

class RegistrationForm(forms.ModelForm):
    role = forms.ChoiceField(label="Select Role", choices=CHOICES, widget=forms.Select(choices=CHOICES))
    password = forms.CharField(label=' ',widget= forms.PasswordInput(attrs={'maxlength':150,'placeholder':'Password'}))
    email = forms.EmailField(label=' ',required=True, widget=forms.EmailInput(attrs={'maxlength':150,'placeholder':'Email'}))
    first_name = forms.CharField(label=' ',widget=forms.TextInput(attrs={'maxlength':150,'placeholder':'First Name'}))
    last_name = forms.CharField(label = ' ',widget=forms.TextInput(attrs={'maxlength':150,'placeholder':'Last Name'}))
    #username = forms.CharField(label=' ',widget=forms.TextInput(attrs={'maxlength':150,'placeholder':'Username'}))

    class Meta:
        model = User
        fields = ('first_name','last_name','email')



class EditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name','last_name','email')

RATING_CHOICES = [(1,'*'),(2,'**'),(3,'***'),(4,'****'),(5,'*****')]

class RatingForm(forms.Form):
    rating = forms.ChoiceField(label="Rate Student", choices= RATING_CHOICES, widget=forms.Select(choices=RATING_CHOICES))
        
