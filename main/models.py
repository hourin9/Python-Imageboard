import os, time;
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

class Artwork(models.Model):
    image = models.ImageField(upload_to=rename_image);
    uploadt = models.DateTimeField(auto_now_add=True);
    tags = models.ManyToManyField(Tag);
    # TODO: uploader foreign key

