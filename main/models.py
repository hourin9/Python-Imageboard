from django.db import models

class Artwork(models.Model):
    title = models.CharField(max_length=200);
    image = models.ImageField(upload_to="artworks/");
    uploadt = models.DateTimeField(auto_now_add=True);
    # TODO: tag and uploader foreign key

class Tag(models.Model):
    class Type(models.IntegerChoices):
        ARTIST = 1;
        CHARACTER = 2;
        SERIES = 3;

    name = models.CharField(max_length=50);
    ttype = models.IntegerField(choices=Type);

