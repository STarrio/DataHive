from django import forms


class CronConfigForm(forms.Form):
    days = forms.IntegerField(label='Days')
    hours = forms.IntegerField(label='Hours')
    minutes = forms.IntegerField(label='Minutes')