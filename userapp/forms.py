from django import forms

class UserProfileForm(forms.Form):
    username = forms.CharField(label='Kullanıcı Adı')
    email = forms.EmailField(label='Email')
    firstname = forms.CharField(label='Adı')
    lastname = forms.CharField(label='Soyadı')
    phone = forms.IntegerField(label='Telefon')
    address = forms.CharField(label='Adres')
    country = forms.CharField(label="country")
    city = forms.CharField(label="city")
    district = forms.CharField(label="district")
