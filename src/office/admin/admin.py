from django.contrib import admin
from django.db.models import Sum, Count
from django.urls import reverse, path
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from icecream import ic

from .filters import PromocodeActiveFilter
from .forms import FeedbackAnswerAdminForm
from ..models import Feedback, PromoCode
from ..utils import generate_promocode


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "is_active",
        "start_date",
        "end_date",
        "limit",
        "counter",
        "discount",
    )
    fields = (
        "code",
        "is_active",
        ("start_date", "end_date"),
        "limit",
        "discount",
        "counter",
    )
    list_filter = (
        PromocodeActiveFilter,
        "start_date",
        "end_date",
        "limit",
        "discount",
        "counter",
    )
    search_fields = ("code", "start_date", "end_date")
    readonly_fields = (
        "is_active",
        "limit",
        "counter",
        # "discount",
    )
    date_hierarchy = "end_date"
    ordering = ["-end_date"]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:
            form.base_fields["code"].initial = generate_promocode()
        return form

    def get_readonly_fields(self, request, obj=None):
        # editing an existing object
        if obj:
            return self.readonly_fields + ("code",)
        return self.readonly_fields

    def has_delete_permission(self, request, obj=None):
        return False

    def is_active(self, obj):
        return "ACTIVE" if obj.is_active else "INACTIVE"


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = (
        "new",
        "text",
        "user_link",
        "email",
        "created",
        "updated",
        "feedback_actions",
    )
    list_filter = ("new", "created")
    search_fields = ["user__email", "email", "text"]
    list_display_links = ("text",)
    list_select_related = ("user",)
    ordering = ["-created"]
    exclude = ("user",)
    readonly_fields = ("new", "user_link", "text", "email", "created", "updated")

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = FeedbackAnswerAdminForm
        return form

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.answer:
            readonly_fields = self.readonly_fields + ("answer",)
            return readonly_fields
        else:
            return super(FeedbackAdmin, self).get_readonly_fields(request, obj)

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

    def user_link(self, obj):
        if obj.user:
            url = reverse("admin:users_user_change", args=[obj.user.id])
            link = '<a href="%s">%s</a>' % (url, obj.user.email)
            return mark_safe(link)
        else:
            return ""
