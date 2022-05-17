from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import AuthProvider, User
from game.models import Deck, GameScore
from office.models import Feedback
from stats.models import DeckAccessLog
from icecream import ic


class DeckInline(admin.TabularInline):
    model = Deck
    extra = 0
    fields = (
        "deck_link",
        "uploaded",
        "ta_type",
        "played_counter",
        "access_counter",
    )
    readonly_fields = (
        "deck_link",
        "uploaded",
        "ta_type",
        "played_counter",
        "access_counter",
    )

    def ta_type(self, obj):
        ta = obj.transaction
        if ta:
            for k, v in ta.PAY_TYPE:
                if ta.pay_type == k:
                    return v

        return ""

    def played_counter(self, obj):
        return obj.games.count()

    def access_counter(self, obj):
        return obj.pin_accesses.count()

    def deck_link(self, obj):
        return format_html(
            '<a href="{}"><b>%s</b></a>&nbsp;' % obj,
            reverse("admin:game_deck_change", args=[obj.pk]),
        )


class FeedbackInline(admin.TabularInline):
    model = Feedback
    show_change_link = True
    extra = 0
    readonly_fields = ("new", "text", "email", "created", "feedback_actions")
    exclude = ("answer",)

    def feedback_actions(self, obj):
        if obj.new:
            return format_html(
                '<a class="button" href="{}">Answer</a>&nbsp;',
                reverse("admin:office_feedback_change", args=[obj.pk]),
            )
        else:
            return ""

    feedback_actions.short_description = "Feedback Actions"
    feedback_actions.allow_tags = True


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        "email",
        "date_joined",
        "count_of_decks",
        "accesses_to_decks",
        "games_with_decks",
        "feedbacks_count",
    ]
    readonly_fields = [
        "email",
        "date_joined",
        "provider",
        "date_joined",
        "count_of_decks",
        "accesses_to_decks",
        "games_with_decks",
        "feedbacks_count",
    ]
    fieldsets = (
        (
            "INFO",
            {
                "fields": (
                    ("email", "provider"),
                    "date_joined",
                    (
                        "count_of_decks",
                        "accesses_to_decks",
                        "games_with_decks",
                        "feedbacks_count",
                    ),
                )
            },
        ),
        ("EDIT", {"fields": (("is_superuser", "groups"),)}),
    )
    inlines = [DeckInline, FeedbackInline]

    class Media:
        css = {"all": ("css/hide_admin_original.css", "css/admin_users_info.css")}

    def get_fields(self, request, obj=None, **kwargs):
        if not request.user.is_superuser:
            self.fields.remove("groups")  # here!
            self.fields.remove("is_superuser")  # here!
        return super(UserAdmin, self).get_fields(request, obj)

    def count_of_decks(self, user):
        return user.decks.count()

    def accesses_to_decks(self, user):
        return DeckAccessLog.objects.filter(deck__user=user).count()

    def feedbacks_count(self, user):
        return Feedback.objects.filter(user=user).count()

    def games_with_decks(self, user):
        counter = 0
        for deck in user.decks.all():
            if GameScore.objects.filter(deck=deck).exists():
                counter += GameScore.objects.filter(deck=deck).count()
        return counter

    def has_change_permission(self, request, obj=None):
        return True


admin.site.register(AuthProvider)
