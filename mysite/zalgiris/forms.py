from django import forms
from .models import GameScore, Totalizator


class TotalizatorForm(forms.ModelForm):
    game_score = forms.ModelChoiceField(queryset=GameScore.objects.all(
    ), empty_label=None, initial=GameScore.objects.first(), label="Select the game by date")

    class Meta:
        model = Totalizator
        fields = ['name', 'zalgiris_guess', 'barcelona_guess', 'game_score']


class EditScoreForm(forms.ModelForm):
    class Meta:
        model = GameScore
        fields = ['zalgiris_score', 'barcelona_score']


class SelectGameForm(forms.Form):
    game_id = forms.ModelChoiceField(
        queryset=GameScore.objects.all(), empty_label='Select a game')
