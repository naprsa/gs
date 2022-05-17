from django import forms
from office.models import Feedback
from ..tasks import send_feedback_answer


class FeedbackAnswerAdminForm(forms.ModelForm):
    answer = forms.CharField(required=True, widget=forms.Textarea())

    class Meta:
        model = Feedback
        fields = [
            "answer",
        ]

    def save(self, commit=True):
        feedback = super(FeedbackAnswerAdminForm, self).save(commit=False)
        feedback.new = False
        email = self.instance.email if self.instance.email else self.instance.user.email
        subj = "Support says... [GiftSolitaire.com]"
        message = (
            f"Dear Customer!"
            f"Thank you for your message. Your opinion is very important to us."
            f"We have studied your question and want to answer the following:"
            f"\n{self.cleaned_data['answer']}"
            f"\nWith the best wishes, always yours support of GiftSolitaire.com"
        )
        feedback.save()
        send_feedback_answer.apply_async((subj, message, email))
        return feedback
