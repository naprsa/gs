# Generated by Django 3.1.13 on 2021-10-15 21:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("office", "0002_feedback_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="promocode",
            name="discount",
            field=models.PositiveSmallIntegerField(
                choices=[(100, "D100"), (75, "D75"), (50, "D50"), (25, "D25")],
                default=100,
                verbose_name="Discount for the promo",
            ),
        ),
    ]
