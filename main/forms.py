# from django import 좃;
from django import forms;

from main.models import Artwork;

class ImagePost(forms.ModelForm):
    class Meta:
        model = Artwork;

        # NOTE: in future update, title is automatically replaced
        # with either the image hash or current time.
        fields = ["title", "image"];

