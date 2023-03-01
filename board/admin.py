from django.contrib import admin
from .models import *
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget


class ArticleAdminForm(forms.ModelForm):
    text = forms.CharField(label='Описание', widget=CKEditorUploadingWidget())

    class Meta:
        model = Article
        fields = '__all__'

class FeedbackInline(admin.StackedInline):
    model = Feedback
    extra = 0


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'title', 'text', 'category', 'date_time',)
    list_display_links = ('id', 'author', 'title', 'category')
    list_filter = ('author', 'category',)
    form = ArticleAdminForm
    inlines = [
        FeedbackInline,
    ]

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'article', 'text', 'status', 'created_on', "parent")
    list_filter = ('status', 'created_on')
    search_fields = ('author', 'article', 'text')
    list_display_links = ('id', 'author',)
    actions = ['Опубликовать_отклик']
    form = ArticleAdminForm

    def Опубликовать_отклик(self, request, queryset):
        queryset.update(status=True)




admin.site.site_title = 'Админ панель Board'
admin.site.site_header = 'Админ панель Board'
