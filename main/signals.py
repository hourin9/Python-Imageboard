from django.db.models.signals import m2m_changed;
from django.dispatch import receiver;

from main import models;

@receiver(m2m_changed, sender=models.Artwork.tags.through)
def update_tag_count(sender, instance, action, pk_set, **kwargs):
    if action in ["post_add", "post_remove", "post_clear"]:
        for tag in models.Tag.objects.filter(pk__in=pk_set):
            tag.artwork_count = tag.artwork_set.count();
            tag.save();

