from django.db import models


# Create your models here.
class PrintLayout(models.Model):
    file = models.FileField("Print layout", null=True)
    deck = models.ForeignKey("game.Deck", verbose_name="Deck", on_delete=models.CASCADE)
    updated = models.DateTimeField(auto_now=True)
    counter = models.IntegerField("counter", default=0)
    task = models.CharField("Task", max_length=50)

    class Meta:
        verbose_name = "Print layout"
        verbose_name_plural = "Print layouts"
