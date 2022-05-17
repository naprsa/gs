from django.forms import DateInput


class DatePickerInput(DateInput):
    template_name = "admin/stats/datepicker.html"
