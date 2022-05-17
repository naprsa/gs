# Generated by Django 3.1.6 on 2021-06-15 18:33

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("office", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Transaction",
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
                    "uid",
                    models.UUIDField(
                        default=uuid.uuid4, verbose_name="Transaction UUID"
                    ),
                ),
                (
                    "pay_date",
                    models.DateTimeField(auto_now_add=True, verbose_name="Pay date"),
                ),
                (
                    "pay_type",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (1, "Promo code"),
                            (2, "Play market"),
                            (3, "Apple pay"),
                        ],
                        verbose_name="Type of pay",
                    ),
                ),
                (
                    "pay_id",
                    models.CharField(
                        blank=True, max_length=25, null=True, verbose_name="Pay ID"
                    ),
                ),
                (
                    "pay_receipt_data",
                    models.TextField(
                        blank=True, default="", verbose_name="Receipt data"
                    ),
                ),
                (
                    "pay_accepted",
                    models.BooleanField(
                        default=False, verbose_name="Transaction accepted"
                    ),
                ),
                (
                    "promocode",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="transactions",
                        to="office.promocode",
                        verbose_name="Promo code",
                    ),
                ),
            ],
        ),
    ]
