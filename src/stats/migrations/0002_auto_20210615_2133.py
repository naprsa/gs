# Generated by Django 3.1.6 on 2021-06-15 18:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("game", "0002_auto_20210615_2133"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("stats", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="promocodeusagelog",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name="Player",
            ),
        ),
        migrations.AddField(
            model_name="deckaccesslog",
            name="deck",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="pin_accesses",
                to="game.deck",
                verbose_name="Deck",
            ),
        ),
        migrations.AddField(
            model_name="deckaccesslog",
            name="player",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
                verbose_name="Player",
            ),
        ),
    ]
