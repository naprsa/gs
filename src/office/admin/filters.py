import datetime

from django.contrib.admin import SimpleListFilter
from icecream import ic


class PromocodeActiveFilter(SimpleListFilter):
    title = "activity"  # or use _('country') for translated title
    parameter_name = "activity"

    def lookups(self, request, model_admin):
        return [("ACTIVE", "Active promo"), ("INACTIVE", "Inactive promo")]

    def queryset(self, request, queryset):
        if self.value() == "ACTIVE":
            qs = queryset.filter(end_date__gte=datetime.datetime.now())
            for q in qs:
                if not q.is_active:
                    qs = qs.exclude(pk=q.pk)
            return qs
        if self.value() == "INACTIVE":
            qs = queryset.filter(end_date__lte=datetime.datetime.now())
            for q in qs:
                if q.is_active:
                    qs = qs.exclude(pk=q.pk)
            return qs
