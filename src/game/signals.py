import os
import shutil
from django.conf import settings
from django.db.models.signals import post_save, post_delete, pre_save, pre_delete
from django.dispatch import receiver
from .models import Deck, Image, Card, DeckFace
from .services import make_cards, make_box


@receiver(post_save, sender=Deck)
def post_save_deck(sender, instance, created, **kwargs):
    if created:
        make_cards(instance)
        make_box(instance)


@receiver(pre_save, sender=Image)
def cache_old_image(sender, instance, **kwargs):
    old_instance = sender.objects.filter(pk=instance.id).first()
    if old_instance is not None:
        instance.old_img = old_instance.img


@receiver(post_save, sender=Image)
def delete_old_image(sender, instance, **kwargs):
    if not kwargs.get("update_fields", None):
        old_file_value = instance.old_img if hasattr(instance, "old_img") else None
        new_file_value = instance.img

        if old_file_value and old_file_value != new_file_value:
            if hasattr(old_file_value, "storage") and hasattr(old_file_value, "path"):
                storage_, path_ = old_file_value.storage, old_file_value.path
                storage_.delete(path_)


@receiver(post_delete, sender=Image)
def clean_media_after_delete(sender, instance, **kwargs):
    if instance.img:
        instance.img.delete()


@receiver(post_delete, sender=Card)
def delete_card_image(sender, instance, **kwargs):
    instance.image.delete()


@receiver(post_delete, sender=DeckFace)
def delete_face_style(sender, instance, **kwargs):
    collection = instance.images
    collection.images.all().delete()
    collection.delete()


@receiver(pre_delete, sender=Deck)
def clean_media_after_delete(sender, instance, **kwargs):
    if instance.is_demo:
        deck_dir = os.path.join(settings.MEDIA_ROOT, "decks", "demo", str(instance.uid))
    else:
        deck_dir = os.path.join(
            settings.MEDIA_ROOT, "decks", str(instance.user.uid), str(instance.uid)
        )
    shutil.rmtree(deck_dir, ignore_errors=True)
