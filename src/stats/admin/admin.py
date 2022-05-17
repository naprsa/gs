from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.contrib import admin

# Register your models here.
from django.db.models import Count
from django.shortcuts import render
from icecream import ic

from game.models import Deck
from users.models import User
from .forms import FilterPeriodForm
from ..models import PromocodeUsageLog, DeckAccessLog, DiskSpaceInfo
from ..utils import get_disk_space


class FakeModel(object):
    class _meta:
        app_label = "stats"  # This is the app that the form will exist under
        app_config = "stats"  # This is the app that the form will exist under
        model_name = "statistic"  # This is what will be used in the link url
        verbose_name_plural = "Statistics"  # This is the name used in the link text
        object_name = "stat"

        swapped = False
        abstract = False


@admin.register(FakeModel)
class StatsAdmin(admin.ModelAdmin):
    def has_add_permission(*args, **kwargs):
        return False

    def has_change_permission(*args, **kwargs):
        return False

    def has_delete_permission(*args, **kwargs):
        return False

    def changelist_view(self, request, **kwargs):
        users = User.objects.filter()
        decks = (
            Deck.objects.prefetch_related("transaction__promocode", "games")
            .select_related("transaction")
            .annotate(games_count=Count("games"))
            .filter(user__isnull=False, transaction__isnull=False)
        )
        demo_decks = (
            Deck.objects.prefetch_related("games")
            .annotate(games_count=Count("games"))
            .filter(user__isnull=True)
        )
        td = None
        if request.GET.get("filter_by", None):
            if request.GET["filter_by"] == "ld":
                td = datetime.today() - relativedelta(days=1)
            if request.GET["filter_by"] == "lw":
                td = datetime.today() - relativedelta(days=7)
            if request.GET["filter_by"] == "lm":
                td = datetime.today() - relativedelta(month=1)
            if request.GET["filter_by"] == "ly":
                td = datetime.today() - relativedelta(year=1)

            if td:
                d_range = [td, datetime.today()]
                decks = decks.filter(uploaded__range=d_range)
                demo_decks = demo_decks.filter(games__created__range=d_range)
                users = users.filter(date_joined__range=d_range)

        elif request.GET.get("start_date") and request.GET.get("end_date"):
            s_date = datetime.strptime(request.GET.get("start_date"), "%d/%m/%Y")
            e_date = datetime.strptime(request.GET.get("end_date"), "%d/%m/%Y")
            d_range = [s_date, e_date]
            decks = decks.filter(uploaded__range=d_range)
            demo_decks = demo_decks.filter(games__created__range=d_range)
            users = users.filter(date_joined__range=d_range)
        elif request.GET.get("start_date") and not request.GET.get("end_date"):
            s_date = request.GET.get("start_date")
            date = datetime.strptime(s_date, "%d/%m/%Y")
            decks = decks.filter(uploaded__date__gte=date)
            demo_decks = demo_decks.filter(games__created__gte=date)
            users = users.filter(date_joined__gte=date)
        elif not request.GET.get("start_date") and request.GET.get("end_date"):
            date = datetime.strptime(request.GET.get("end_date"), "%d/%m/%Y")
            decks = decks.filter(uploaded__lte=date)
            demo_decks = demo_decks.filter(games__created__lte=date)
            users = users.filter(date_joined__lte=date)

        payed_decks = {
            "all": decks.count(),
            "promo": decks.filter(transaction__promocode__isnull=False).count(),
            "money": decks.exclude(transaction__promocode__isnull=False).count(),
        }
        payed_decks_was_played = {
            "all": decks.filter(games__isnull=False).count(),
            "promo": decks.filter(
                games__isnull=False, transaction__promocode__isnull=False
            ).count(),
            "money": decks.filter(
                games__isnull=False, transaction__promocode__isnull=True
            ).count(),
        }

        played_gte_ten_times_decks = {
            "all": decks.filter(games_count__gte=10).count(),
            "promo": decks.filter(
                games_count__gte=10, transaction__promocode__isnull=False
            ).count(),
            "money": decks.filter(
                games_count__gte=10, transaction__promocode__isnull=True
            ).count(),
        }

        print_layout_logs = {
            "all": decks.filter(printlayout__isnull=False).count(),
            "promo": decks.filter(
                printlayout__isnull=False, transaction__promocode__isnull=False
            ).count(),
            "money": decks.filter(
                printlayout__isnull=False, transaction__promocode__isnull=True
            ).count(),
        }

        demo_stats = []
        for deck in demo_decks:
            demo_stats.append(
                {
                    "title": deck.title,
                    "games_count": deck.games_count,
                    "games_started": deck.pin_accesses.count(),
                }
            )
        context = {
            "title": "Statistics",
            "users": users.count(),
            "payed_decks": payed_decks,
            "payed_decks_was_played": payed_decks_was_played,
            "played_gte_ten_times_decks": played_gte_ten_times_decks,
            "print_layout_logs": print_layout_logs,
            "demo_stats": demo_stats,
            "form_period": FilterPeriodForm(request.GET),
            "disk_space": get_disk_space(),
        }
        return render(request, "admin/stats/stats_changelist_view.html", context)


@admin.register(PromocodeUsageLog)
class PromocodeUsageLog(admin.ModelAdmin):
    pass


@admin.register(DiskSpaceInfo)
class StatisticsLog(admin.ModelAdmin):
    pass


@admin.register(DeckAccessLog)
class DeckAccessLog(admin.ModelAdmin):
    pass
