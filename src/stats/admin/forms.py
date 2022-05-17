from django import forms


class FilterPeriodForm(forms.Form):
    CHOICES = (
        ("", None),
        ("ld", "Last day"),
        ("lw", "Last week"),
        ("lm", "Last month"),
        ("ly", "Last year"),
    )
    start_date = forms.DateField(
        input_formats=["%d/%m/%Y"], required=False, help_text="From:"
    )
    end_date = forms.DateField(
        input_formats=["%d/%m/%Y"], required=False, help_text="To:"
    )
    filter_by = forms.ChoiceField(choices=CHOICES, required=False, help_text="Period")

    class Meta:
        help_texts = {
            "start_date": "Start filter date",
            "end_date": "End filter date",
            "filter_by": "Filter by last periods",
        }
