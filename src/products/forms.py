from django import forms
from .models import ReviewModel

class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewModel
        fields = ['text']
        widgets = {
            'text': forms.Textarea(
                attrs={'class': 'form-textarea', 'placeholder': 'Отзыв', 'title': "Пожалуйста, введите отзыв."}
            ),
        }
        labels = {
            'text': '',
        }
        error_messages = {
            'text': {
                'required': 'Пожалуйста, введите отзыв.',
                'max_length': 'Отзыв слишком длинный.',
            },
        }