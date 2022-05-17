from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import PrintLayout


@receiver(post_delete, sender=PrintLayout)
def delete_layout_file(sender, instance, **kwargs):
    if instance.file:
        instance.file.delete()
