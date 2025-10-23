import os, time;
from django.contrib.auth.models import User
from django.db import models;

def rename_image(instance, filename) -> str:
    ext = os.path.splitext(filename)[1].lower();
    ut = int(time.time());
    return f"artworks/{ut}{ext}";

class Tag(models.Model):
    class Type(models.IntegerChoices):
        ARTIST = 1;
        CHARACTER = 2;
        SERIES = 3;

    name = models.CharField(max_length=50, primary_key=True);
    ttype = models.IntegerField(choices=Type);
    artwork_count = models.PositiveBigIntegerField(default=0);

class Artwork(models.Model):
    image = models.ImageField(upload_to=rename_image);
    uploadt = models.DateTimeField(auto_now_add=True);
    tags = models.ManyToManyField(Tag);
    score = models.BigIntegerField(default=0);
    # TODO: uploader foreign key

class ArtworkVote(models.Model):
    class Type(models.IntegerChoices):
        UPVOTE = 1;
        DOWNVOTE = -1;

    artwork = models.ForeignKey(
        Artwork,
        on_delete=models.CASCADE,
        related_name="votes");

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="artwork_votes");

    vtype = models.IntegerField(choices=Type);

    class Meta:
        unique_together = ("artwork", "user");

