from django import forms
from django.core.exceptions import ValidationError
from .models import Article, Feedback


class ArticleForm(forms.ModelForm):
    required_css_class = 'my-custom-class'
    title = forms.CharField(max_length=40)

    class Meta:
        model = Article
        fields = [
            'title',
            'category',
            'text',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': "form-control"})
        self.fields['title'].label = "Заголовок публикации"
        self.fields['title'].widget.attrs.update({'placeholder': "Введите название"})
        self.fields['text'].label = "Текст публикации"
        self.fields['text'].widget.attrs.update({'placeholder': "Введите текст здесь"})
        self.fields['category'].label = "Категория"

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get("title")
        text = cleaned_data.get("text")

        if title == text:
            raise ValidationError(
                "Текст статьи не должен быть идентичен заголовку."
            )
        return cleaned_data


# class FeedbackForm(forms.ModelForm):
#
#     class Meta:
#         model = Feedback
#         fields = ('text',)
#         widgets = {
#             "text": forms.Textarea(attrs={"class": "form-control border"})
#         }
#         labels = {
#             'text': 'Добавьте комментарий'
#         }
#
#     def __init__(self, *args, **kwargs):
#         super(FeedbackForm, self).__init__(*args, **kwargs)
#
#         for name, field in self.fields.items():
#             field.widget.attrs.update({'class': 'input'})
class FeedbackForm(forms.ModelForm):
    text = forms.CharField(label='Текст комментария', widget=forms.Textarea)

    class Meta:
        model = Feedback
        fields = ['text']

    def __init__(self, *args, **kwargs):
        """Save the request with the form so it can be accessed in clean_*()"""
        self.request = kwargs.pop('request', None)
        super(FeedbackForm, self).__init__(*args, **kwargs)



class FeedbackFilterForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(FeedbackFilterForm, self).__init__(*args, **kwargs)
        self.fields['title'] = forms.ModelChoiceField(
            label='Объявления',
            queryset=Article.objects.filter(author_id=user.id).order_by('-date_time').values_list('title', flat=True),
            empty_label="Все",
            required=False
        )
