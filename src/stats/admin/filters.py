from django.contrib import admin
from icecream import ic


class YearMonthDayFilter(admin.SimpleListFilter):
    title = "filter"
    # parameter_name = "created"

    def lookups(self, request, model_admin):
        ic(request)
        ic(model_admin)
        # firstyear = (
        #     History.objects.order_by("date_and_time").first().date_and_time.year
        # )  # First year of the history
        # currentyear = datetime.datetime.now().year  # Current year
        years = ["a", "b"]  # Declaration of the list that'll contain the missing years
        # for x in range(currentyear - firstyear):  # Fill the list with the missing years
        #     yearinloop = firstyear + x
        #     years.insert(0, (str(yearinloop), str(yearinloop)))
        # years.insert(0, (str(currentyear), str(currentyear)))
        return years

    def queryset(self, request, queryset):
        ic(request)
        ic(queryset)
