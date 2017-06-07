from django import forms


class ChatForm(forms.Form):
    chat = forms.CharField(max_length=200)

    def __init__(self, *args, **kwargs):
        super(ChatForm, self).__init__(*args, **kwargs)
        self.fields['chat'].widget.attrs.update({
            'class':'form-control chat-val',
            'style':'font-size:13px; width:300px; height:36px; color:grey;'
        })
