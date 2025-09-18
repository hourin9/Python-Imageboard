# from django import 좃;
from django import forms;

from main.models import Artwork, Tag;

class ImagePost(forms.ModelForm):
    class Meta:
        model = Artwork;

        # NOTE: in future update, title is automatically replaced
        # with either the image hash or current time.
        fields = ["image", "tags"];

class TagCreation(forms.ModelForm):
    class Meta:
        model = Tag;

        # NOTE: in future update, title is automatically replaced
        # with either the image hash or current time.
        fields = ["name", "ttype"];

