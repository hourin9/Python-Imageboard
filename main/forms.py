# from django import 좃;
from django import forms;
from django.core.exceptions import ValidationError;

from main.models import Artwork, Tag;

class ImagePost(forms.ModelForm):
    tags = forms.CharField(required=False, widget=forms.Textarea(attrs={
        "rows": 3,
        "placeholder": "tags separated by space",
        "class": "max-w-md w-full p-2 border",
    }));

    def clean_tags(self):
        raw = self.cleaned_data["tags"]
        names = raw.split()

        tags = []
        missing = []

        for name in names:
            try:
                t = Tag.objects.get(name=name)
                tags.append(t)
            except Tag.DoesNotExist:
                missing.append(name)

        if missing:
            raise ValidationError(
                f"These tags don’t exist: {', '.join(missing)}"
            )

        return tags

    def save(self, commit=True):
        artwork = super().save(commit=False)
        tags = self.cleaned_data["tags"]
        if commit:
            artwork.save()
            artwork.tags.set(tags)
        return artwork

    class Meta:
        model = Artwork;
        fields = ["image", "tags"];

class ImageUpdate(forms.ModelForm):
    class Meta:
        model = Artwork;
        fields = ["tags"];

class TagCreation(forms.ModelForm):
    class Meta:
        model = Tag;

        # NOTE: in future update, title is automatically replaced
        # with either the image hash or current time.
        fields = ["name", "ttype"];

