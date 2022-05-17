from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from uuid import uuid4
from django.db import models

from django.utils.translation import gettext_lazy as _


class Transaction(models.Model):
    PROMO = 1
    GOOGLE = 2
    APPLE = 3

    PAY_TYPE = (
        (PROMO, _("Promo code")),
        (GOOGLE, _("Play market")),
        (APPLE, _("Apple pay")),
    )

    uid = models.UUIDField(_("Transaction UUID"), default=uuid4)
    pay_date = models.DateTimeField(_("Pay date"), auto_now=False, auto_now_add=True)
    pay_type = models.PositiveSmallIntegerField(_("Type of pay"), choices=PAY_TYPE)
    promocode = models.ForeignKey(
        "office.PromoCode",
        verbose_name=_("Promo code"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="transactions",
    )

    pay_id = models.CharField(
        _("Pay ID"),
        max_length=25,
        blank=True,
        null=True,
    )
    pay_receipt_data = models.TextField(_("Receipt data"), blank=True, default="")
    pay_accepted = models.BooleanField(_("Transaction accepted"), default=False)

    def unique(self):
        qs = Transaction.objects.filter(pay_id=self.pay_id)
        if qs.exists():
            return qs.count() == 1
        else:
            return False
