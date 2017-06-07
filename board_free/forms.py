from django import forms
from django_summernote.widgets import SummernoteWidget
from .models import FreeBoard


class FreeBoardForm(forms.ModelForm):
    is_superuser = forms.BooleanField(required=False)
    class Meta:
        model = FreeBoard
        fields = ('sort', 'title', 'user', 'body', 'player_review', 'after_game_review', 'before_game_review', 'is_superuser')
        widgets = {'body': SummernoteWidget()}

    def __init__(self, *args, **kwargs):
        super(FreeBoardForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({
            'class': 'form-control',
            'style': 'width:600px; font-size:14px; height:36px; color:#4a4a4a;',
        })


class SearchForm(forms.Form):
    search_value = forms.CharField(label="Search", max_length=200,
                                   widget=forms.TextInput(attrs={
                                       'class': 'form-control', 'placeholder': '검색어를 입력해주세요',
                                       'style': 'font-size:12px; height:36px; width:200px; color:#7D7D7D;'
                                   }))
