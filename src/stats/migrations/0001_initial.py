# Generated by Django 3.1.6 on 2021-06-15 18:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("office", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="DeckAccessLog",
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
                    "player_ip",
                    models.CharField(max_length=20, verbose_name="Player IP"),
                ),
                (
                    "created",
                    models.DateTimeField(auto_now_add=True, verbose_name="Recorded"),
                ),
            ],
            options={
                "verbose_name": "Deck access Log",
                "verbose_name_plural": "Deck access logs",
                "ordering": ["-created"],
            },
        ),
        migrations.CreateModel(
            name="DiskSpaceInfo",
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
                ("total", models.CharField(max_length=50, verbose_name="Total space")),
                ("used", models.CharField(max_length=50, verbose_name="Used space")),
                ("free", models.CharField(max_length=50, verbose_name="Free space")),
                (
                    "created",
                    models.DateTimeField(auto_now_add=True, verbose_name="Created"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Stats",
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
                    "users_count",
                    models.PositiveSmallIntegerField(verbose_name="Users count"),
                ),
                ("count_payed", models.JSONField(verbose_name="Count payed")),
                ("count_mto", models.JSONField(verbose_name="Count more than once")),
                ("count_mtt", models.JSONField(verbose_name="Count more than ten")),
                (
                    "count_boxlayout",
                    models.JSONField(verbose_name="Count box layout request"),
                ),
                (
                    "count_demo_played",
                    models.JSONField(verbose_name="Count demo payed"),
                ),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Stats created"
                    ),
                ),
            ],
            options={
                "verbose_name": "Statistic",
                "verbose_name_plural": "Statistics",
                "ordering": ["-created"],
            },
        ),
        migrations.CreateModel(
            name="PromocodeUsageLog",
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
                ("user_ip", models.CharField(max_length=20, verbose_name="Player IP")),
                (
                    "created",
                    models.DateTimeField(auto_now_add=True, verbose_name="Was used"),
                ),
                (
                    "code",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="usages",
                        to="office.promocode",
                        verbose_name="Promo code",
                    ),
                ),
            ],
        ),
    ]
