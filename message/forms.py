from django import forms

from account.models import MyUser
from .models import Message


class MessageForm(forms.ModelForm):
    take_user = forms.CharField(max_length=50)
    class Meta:
        model = Message
        fields = ('send_user', 'take_user', 'message',)

    def __init__(self, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)
        self.fields['take_user'].widget.attrs.update({
            'class': 'form-control input-take-user',
            'style': 'width:590px; font-size:13px; color:#555555; height:36px;'
        })
        self.fields['message'].widget.attrs.update({
            'class': 'form-control',
            'style': 'width:800px; font-size:14px; color:#555555;'
        })

    def clean_take_user(self):
        take_user = self.cleaned_data['take_user']
        try:
            take_user = MyUser.objects.get(nickname=take_user)
        except MyUser.DoesNotExist:
            raise forms.ValidationError('Does not exist user nickname')
        else:
            return take_user
