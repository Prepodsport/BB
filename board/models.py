from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


# Create your models here.
class Article(models.Model):
    CHOICE = (
        ('tanks', 'Танки'),
        ('hils', 'Хилы'),
        ('dd', 'ДД'),
        ('trader', 'Торговцы'),
        ('guildmasters', 'Гилдмастеры'),
        ('questgivers', 'Квестгиверы'),
        ('blacksmiths', 'Кузнецы'),
        ('tanners', 'Кожевники'),
        ('potionmakers', 'Зельевары'),
        ('spellmasters', 'Мастера заклинаний'),
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор поста')
    title = models.CharField(max_length=24, verbose_name='Название поста')
    category = models.CharField(max_length=12, choices=CHOICE, default='hils', verbose_name='Категория поста')
    date_time = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания поста')
    text = RichTextUploadingField(verbose_name='Текст поста')

    def __str__(self):
        return self.title

    """ от прошлых наработок """

    # @property
    # def comments(self):
    #     queryset = self.comments.all().article_list('author__id', flat=True)
    #     return queryset
    #
    # def __str__(self):
    #     """ Отображение названия поста и краткого текста поста """
    #     return f'{self.title.title()}:{self.text[:20]}'
    #
    def get_absolute_url(self):
        """ Вернуть url, зарегистрированный для отображения одиночного товара """
        return reverse('articles_list')

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"


class Feedback(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор отклика')
    text = RichTextUploadingField(verbose_name='Текст отклика')
    created_on = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments',
                                verbose_name='Статья отклика')
    status = models.BooleanField(default=False, verbose_name='Опубликовать отклик')
    parent = models.ForeignKey('self', verbose_name="Родитель", related_name='replies', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.text[:60]

    # def __str__(self):
    #     return f"{self.author} - {self.article}"
    # def __str__(self):
    #     return 'Комментарий {} от {}'.format(self.text, self.article)

    def get_absolute_url(self):
        return reverse('article_detail', kwargs={'pk': self.article_id})

    class Meta:
        ordering = ['-created_on']
        verbose_name = "Отклик"
        verbose_name_plural = "Отклики"
