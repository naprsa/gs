from django.contrib.auth import get_user_model
from django.db import models

# Create your models here.
from django.utils.translation import ugettext_lazy as _
from icecream import ic

from game.models import Deck
from office.models import PromoCode


class PromocodeUsageLog(models.Model):
    user = models.ForeignKey(
        get_user_model(), verbose_name=_("Player"), on_delete=models.CASCADE
    )
    user_ip = models.CharField(_("Player IP"), max_length=20)
    code = models.ForeignKey(
        PromoCode,
        verbose_name=_("Promo code"),
        related_name="usages",
        on_delete=models.CASCADE,
    )
    created = models.DateTimeField(_("Was used"), auto_now=False, auto_now_add=True)


class DeckAccessLog(models.Model):
    deck = models.ForeignKey(
        Deck,
        verbose_name=_("Deck"),
        null=True,
        on_delete=models.SET_NULL,
        related_name="pin_accesses",
    )
    player = models.ForeignKey(
        get_user_model(), verbose_name="Player", null=True, on_delete=models.SET_NULL
    )
    player_ip = models.CharField(_("Player IP"), max_length=20)
    created = models.DateTimeField(_("Recorded"), auto_now=True, auto_now_add=False)

    class Meta:
        verbose_name = "Deck access Log"
        verbose_name_plural = "Deck access logs"
        ordering = ["-created"]


class DiskSpaceInfo(models.Model):
    total = models.CharField("Total space", max_length=50)
    used = models.CharField("Used space", max_length=50)
    free = models.CharField("Free space", max_length=50)
    created = models.DateTimeField("Created", auto_now_add=True)

    def __str__(self):
        return f"Disk info [{self.created.date()}]"


class Stats(models.Model):
    users_count = models.PositiveSmallIntegerField(_("Users count"))
    count_payed = models.JSONField(_("Count payed"))
    count_mto = models.JSONField(_("Count more than once"))
    count_mtt = models.JSONField(_("Count more than ten"))
    count_boxlayout = models.JSONField(_("Count box layout request"))
    count_demo_played = models.JSONField(_("Count demo payed"))
    created = models.DateTimeField(_("Stats created"), auto_now_add=True)

    class Meta:
        ordering = [
            "-created",
        ]
        verbose_name = _("Statistic")
        verbose_name_plural = _("Statistics")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.decks = Deck.objects.filter()

    def save(self) -> None:
        self.update_stats()
        super().save()

    def update_stats(self):
        if self.decks:
            try:
                # self.users_count = User.objects.exclude(is_staff=True).count()
                self.count_payed = self.count_decks_by_paytype()
                self.count_mto = self.count_payed_mto_decks()
                self.count_mtt = self.count_payed_mtt_decks()
                self.count_boxlayout = self.count_by_box_layout_request()
                self.count_demo_played = self.count_play_demo_decks()
            except Exception as e:
                ic()
                ic(e)

    def filter_by_paytype(query):
        promo_count = query.filter(transaction__pay_type=1).count()
        money_count = query.filter(transaction__pay_type__in=(1, 2)).count()
        all_count = promo_count + money_count
        return {"all": all_count, "promo": promo_count, "money": money_count}

    def count_decks_by_paytype(self):
        decks = self.decks.filter(deck_type=Deck.CUSTOM)
        return self.filter_by_paytype(decks)

    def count_payed_mto_decks(self):
        """
        Decks that played more than once
        """
        decks = self.decks.filter(played__gte=1, deck_type=Deck.CUSTOM)
        return self.filter_by_paytype(decks)

    def count_payed_mtt_decks(self):
        """
        Decks that played more than 10 times
        """
        decks = self.decks.filter(played__gt=10, deck_type=Deck.CUSTOM)
        return self.filter_by_paytype(decks)

    def count_by_box_layout_request(self):
        decks = self.decks.filter(box__layout_request__gte=1)
        return self.filter_by_paytype(decks)

    def count_play_demo_decks(self):
        decks = self.decks.filter(deck_type=Deck.DEMO)
        ctx = {}
        for deck in decks:
            ctx[deck.id] = deck.played
        return ctx
