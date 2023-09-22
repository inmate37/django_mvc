# Django
from django import forms

# Local
from .models import (
    Album,
    Song
)


class AlbumForm(forms.ModelForm):

    class Meta:
        model = Album
        fields = ['band', 'title', 'logo', 'release_date']


class SongForm(forms.ModelForm):

    class Meta:
        model = Song
        fields = ['title', 'audio_file']
