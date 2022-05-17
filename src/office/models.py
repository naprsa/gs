from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from shortuuidfield import ShortUUIDField
import datetime


class Feedback(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        verbose_name=_("Player"),
        on_delete=models.SET_NULL,
        null=True,
        related_name="feedbacks",
    )
    text = models.TextField(_("Feedback"))
    created = models.DateTimeField(_("Created"), auto_now=False, auto_now_add=True)
    updated = models.DateTimeField(_("Answered"), auto_now=True)
    new = models.BooleanField(_("New"), default=True)
    email = models.EmailField(_("Email"), max_length=254, blank=True)
    answer = models.TextField(_("Answer"), blank=True)

    class Meta:
        ordering = ["user", "-created"]

    def save(self, *args, **kwargs):
        if self.answer:
            self.new = False
        return super(Feedback, self).save(*args, **kwargs)


class PromoCode(models.Model):
    class Discount(models.IntegerChoices):
        D100 = 100
        D75 = 75
        D50 = 50
        D25 = 25

    code = ShortUUIDField(auto=False, unique=True, editable=True)
    start_date = models.DateField(_("Start promo date"), auto_now_add=False)
    end_date = models.DateField(_("End promo date"), auto_now_add=False)
    limit = models.PositiveSmallIntegerField(_("Limit of the usage"), default=0)
    discount = models.PositiveSmallIntegerField(
        _("Discount for the promo"), choices=Discount.choices, default=Discount.D100
    )
    counter = models.PositiveSmallIntegerField(
        "Usage counter", editable=False, default=0
    )

    def __str__(self):
        return f"{self.code} [{self.discount}%]"

    @property
    def used_count(self):
        return self.transactions.count()

    @property
    def check_usability(self):
        return True if self.limit == 0 else self.limit > self.counter

    @property
    def is_active(self):
        if self.end_date:
            expired = datetime.date.today() > self.end_date
            return self.check_usability and not expired

    def save(self, keep_deleted=True, **kwargs):
        self.code = self.code.upper()
        super(PromoCode, self).save()
