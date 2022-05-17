import os

import safedelete.models
from django.conf import settings
from django.contrib import admin
from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django_singleton_admin.admin import SingletonAdmin
from icecream import ic

from users.models import User
from .forms import DeckFaceAdminForm
from game.models import (
    Card,
    Deck,
    Box,
    Image,
    DeckShirt,
    DeckFace,
    ImageCollection,
    DeckFacesJsonSchema,
    GameScore,
    DeckTranslate,
)
from stats.models import DeckAccessLog


class CardInline(admin.TabularInline):
    """Tabular Inline View for"""

    model = Card
    extra = 0
    fields = ["image_thumb", "card"]
    readonly_fields = ["image_thumb", "card"]

    def image_thumb(self, obj):
        if obj.image.img:
            return format_html(
                '<a href="{}"><img src="%s" style="height: 65px;" /></a>&nbsp;'
                % obj.image.img.url,
                reverse("admin:game_card_change", args=[obj.pk]),
            )
        else:
            return format_html(
                '<a href="{}"><img src="%s" style="height: 65px;" /></a>&nbsp;'
                % "/static/imgs/cap.png",
                reverse("admin:game_card_change", args=[obj.pk]),
            )

    def card(self, obj):
        return obj.humanize_card()

    def has_delete_permission(self, request, obj=None):
        return False


class DeckTranslateInline(admin.StackedInline):
    model = DeckTranslate
    extra = 0


class ImageInline(admin.TabularInline):
    model = Image
    extra = 0


class DeckAccessInline(admin.TabularInline):
    model = DeckAccessLog
    extra = 0
    list_filter = ["created"]

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    fields = ["img_thumb", "updated"]
    readonly_fields = ["updated", "img_thumb"]
    list_display = ["img_thumb", "deck"]

    def img_thumb(self, obj):
        if obj.image.img:
            return format_html(
                '<a href="{}"><img src="%s" style="height: 65px;" /></a>&nbsp;'
                % obj.image.img.url,
                reverse("admin:game_image_change", args=[obj.image.pk]),
            )
        else:
            return format_html(
                '<a href="{}"><img src="%s" style="height: 65px;" /></a>&nbsp;'
                % "/static/imgs/cap.png",
                reverse("admin:game_image_change", args=[obj.image.pk]),
            )


@admin.register(Deck)
class DeckAdmin(admin.ModelAdmin):
    save_on_top = True
    inlines = [DeckTranslateInline, CardInline]
    list_display = (
        "title",
        "owner_link",
        "uploaded",
        "updated",
        "pay_type",
        "played",
        "expires",
    )
    list_display_links = ("title",)
    list_filter = (
        "uploaded",
        "updated",
        "expires",
    )
    search_fields = (
        "title",
        "uid",
        "user__email",
        "uploaded",
        "updated",
        "transaction__pay_type",
        "games__count",
        "expires",
    )
    readonly_fields = [
        "uid",
        "owner_link",
        "type_of_deck",
        "full_path_to_deck_media",
        "uploaded",
        "updated",
        "pay_type",
        "played",
        "played_won",
        "deck_box_link",
        "expires",
    ]
    fieldsets = (
        (
            "EDIT",
            {
                "fields": (
                    ("title", "cong_text"),
                    "pin",
                    ("shirt", "face", "mirror"),
                    ("active", "demo_mobile"),
                )
            },
        ),
        (
            "INFO",
            {
                "fields": (
                    ("owner_link", "deck_box_link"),
                    ("type_of_deck", "pay_type"),
                    ("played", "played_won"),
                    ("uploaded", "updated", "expires"),
                )
            },
        ),
        ("TECH INFO:", {"fields": (("uid", "full_path_to_deck_media"),)}),
    )
    exclude = ["user", "transaction", "box"]
    date_hierarchy = "uploaded"
    change_form_template = "admin/game/deck_change_form.html"

    class Media:
        css = {"all": ("css/hide_admin_original.css",)}

    def get_queryset(self, request):
        qs = super(DeckAdmin, self).get_queryset(request)
        qs = qs.annotate(models.Count("games"))
        return qs

    def delete_model(self, request, qs):
        qs.delete(force_policy=safedelete.models.HARD_DELETE)

    def owner_link(self, deck):
        if deck.user:
            url = reverse("admin:users_user_change", args=[deck.user.id])
            link = '<a href="%s">%s</a>' % (url, deck.user.email)
            return mark_safe(link)
        else:
            return ""

    owner_link.short_description = "Owner"
    owner_link.admin_order_field = "user__email"

    def deck_box_link(self, deck):
        if deck.box:
            url = reverse("admin:game_box_change", args=[deck.box.id])
            link = '<a href="%s">%s</a>' % (url, deck.box)
            return mark_safe(link)
        else:
            return ""

    def played(self, obj):
        return obj.pin_accesses.count()

    played.admin_order_field = "games__count"
    played.short_description = "Was played times"

    def played_won(self, obj):
        return obj.games.filter(won=True).count()

    played_won.short_description = "Was won times"

    def type_of_deck(self, deck):
        if deck.user:
            deck_type = "USER DECK"
        else:
            deck_type = "DEMO DECK"

        # if DeckAccess.objects.filter(deck=deck):
        #     deck_type = "GIFTED DECK"
        return deck_type

    def pay_type(self, deck):
        if not deck.transaction:
            return ""
        elif deck.transaction.pay_type == 1:
            return f"Promocode [{deck.transaction.promocode.code}]"
        elif deck.transaction.pay_type == 2:
            return f"Google Pay [{deck.transaction.pay_id}]"
        elif deck.transaction.pay_type == 3:
            return f"Apple Pay [{deck.transaction.pay_id}]"

    pay_type.admin_order_field = "transaction__pay_type"

    def full_path_to_deck_media(self, deck):
        decks = "decks/demo" if self.deck.is_demo else "decks"
        deck_path = (
            str(deck.uid) if deck.is_demo else f"{str(deck.user.uid)}/{str(deck.uid)}"
        )
        return os.path.abspath(
            os.path.join(settings.MEDIA_ROOT, decks, deck_path, str(deck.uid))
        )

    def change_view(self, request, object_id, form_url="", extra_context=None):
        response = super(DeckAdmin, self).change_view(request, object_id)
        accesses = DeckAccessLog.objects.filter(deck_id=object_id)
        games = GameScore.objects.filter(deck_id=object_id)
        players = set(
            [acc.player_ip if not acc.player else acc.player for acc in accesses]
            + [game.ip if not game.user else game.user for game in games]
        )

        ctx = []
        for user in players:
            upd_ctx = {"player": user}
            stats = {"accesses": 0, "games": 0}
            if isinstance(user, User):
                stats["accesses"] = accesses.filter(player=user).count()
                stats["games"] = games.filter(user=user).count()
            else:
                stats["accesses"] = accesses.filter(player_ip=user).count()
                stats["games"] = games.filter(ip=user).count()
            upd_ctx["stats"] = stats
            ctx.append(upd_ctx)

        if response.get("context_data"):
            response.context_data.update({"players": ctx})
        return response


@admin.register(DeckFace)
class DeckFace(admin.ModelAdmin):
    fields = [
        "uid",
        "images_full",
        # "version",
        "title",
        "file",
        "updated",
        "json_settings",
        "md5",
    ]
    list_display = ["images_thumbs", "title", "created", "updated"]
    readonly_fields = ["uid", "images_full", "updated", "json_settings", "md5"]
    ordering = ["pk"]

    def get_form(self, request, obj=None, change=True, **kwargs):
        form = DeckFaceAdminForm
        return form

    def images_thumbs(self, obj):
        images = obj.images.get_collection_qs()
        thumbs = []
        for i in images:
            filename = os.path.basename(i.img.name).split(".")[0]
            if filename in ["spades", "hearts", "clubs", "diamonds"]:
                thumbs.append(f'<img src="{i.img.url}" style="height: 25px;" />')
        return format_html("".join(thumbs))

    def images_full(self, obj):
        images = obj.images.get_collection_qs()
        images = [f'<img src="{i.img.url}" style="height: 45px;" />' for i in images]
        return format_html("".join(images))


@admin.register(DeckShirt)
class DeckShirtAdmin(admin.ModelAdmin):
    fields = [
        "uid",
        "image_full",
        "title",
        "border_color",
        "image",
        "created",
        "updated",
    ]
    list_display = ["image_thumb", "title", "created", "updated"]
    list_display_links = ["image_thumb", "title"]
    readonly_fields = ["image_full", "uid", "updated", "created"]

    def image_thumb(self, obj):
        return format_html(f'<img src="{obj.image.img.url}" style="height: 45px;" />')

    def image_full(self, obj):
        return format_html(f'<img src="{obj.image.img.url}" style="height: 200px;" />')


@admin.register(ImageCollection)
class ImageCollectionAdmin(admin.ModelAdmin):
    inlines = [
        ImageInline,
    ]


@admin.register(DeckFacesJsonSchema)
class JsonSchemaValidationAdmin(SingletonAdmin):
    pass


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    readonly_fields = ["md5"]


@admin.register(GameScore)
class GameScoreAdmin(admin.ModelAdmin):
    list_display = ["user", "deck", "score", "time", "ip", "won"]
    list_filter = ["user", "deck", "ip", "time"]
    readonly_fields = ["user", "deck", "score", "time", "ip", "won", "created"]


@admin.register(Card)
class CardsAdmin(admin.ModelAdmin):
    fields = ["img_thumb", "deck", "image", "suit", "value"]
    list_display = ["img_thumb", "card"]
    readonly_fields = ["deck", "suit", "value", "img_thumb"]

    def card(self, obj):
        return obj.humanize_card()

    def img_thumb(self, obj):
        if obj.image.img:
            return format_html(
                '<a href="{}"><img src="%s" style="height: 65px;" /></a>&nbsp;'
                % obj.image.img.url,
                reverse("admin:game_card_change", args=[obj.pk]),
            )
        else:
            return format_html(
                '<a href="{}"><img src="%s" style="height: 65px;" /></a>&nbsp;'
                % "/static/imgs/cap.png",
                reverse("admin:game_card_change", args=[obj.pk]),
            )
