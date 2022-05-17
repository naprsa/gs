# Generated by Django 3.1.13 on 2022-03-27 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("game", "0003_auto_20220322_1546"),
    ]

    operations = [
        migrations.AddField(
            model_name="deck",
            name="cong_text",
            field=models.TextField(
                blank=True,
                default="",
                max_length=1000,
                verbose_name="Congratulation text",
            ),
        ),
    ]