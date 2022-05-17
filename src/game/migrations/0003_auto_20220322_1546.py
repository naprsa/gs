# Generated by Django 3.1.13 on 2022-03-22 12:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("game", "0002_auto_20210615_2133"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="deck",
            name="cong_text",
        ),
        migrations.CreateModel(
            name="DeckTranslate",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        blank=True,
                        default="",
                        max_length=150,
                        verbose_name="Deck title",
                    ),
                ),
                (
                    "cong_text",
                    models.TextField(
                        blank=True,
                        default="",
                        max_length=1000,
                        verbose_name="Congratulation text",
                    ),
                ),
                (
                    "translate_prefix",
                    models.CharField(
                        default="ru",
                        max_length=3,
                        verbose_name="Translate prefix(ru, en, de..",
                    ),
                ),
                (
                    "deck",
                    models.OneToOneField(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="translate",
                        to="game.deck",
                    ),
                ),
            ],
            options={
                "verbose_name": "Deck Translate",
                "verbose_name_plural": "Deck Translations",
            },
        ),
    ]