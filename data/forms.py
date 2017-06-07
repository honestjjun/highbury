from django import forms

from .models import Match, UserPoint


class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = (
            'result', 'home_score', 'away_score', 'player1', 'player2', 'player3', 'player4', 'player5', 'player6',
            'player7', 'player8', 'player9', 'player10', 'player11', 'player12', 'player13', 'player14'
        )

    def __init__(self, *args, **kwargs):
        super(MatchForm, self).__init__(*args, **kwargs)
        self.fields['result'].widget.attrs.update({
            'class': 'form-control',
            'style': 'font-size:13px; height:36px; color:#555555;'
        })
        self.fields['home_score'].widget.attrs.update({
            'class': 'form-control',
            'style': 'font-size:13px; height:36px; color:#555555;'
        })
        self.fields['away_score'].widget.attrs.update({
            'class': 'form-control',
            'style': 'font-size:13px; height:36px; color:#555555;'
        })


class UserPointForm(forms.ModelForm):
    class Meta:
        model = UserPoint
        fields = ('sort', 'value')

