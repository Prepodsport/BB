from celery import shared_task
from django.contrib.auth.models import User
from .models import Article, Feedback
from django.core.mail import send_mail
from datetime import timedelta
from django.utils import timezone


@shared_task
def feedback_send_email(feedback_id):
    feedback = Feedback.objects.get(id=feedback_id)
    send_mail(
        subject=f'BB: новый отклик на объявление!',
        message=f'Доброго дня, {feedback.article.author}, ! На ваше объявление есть новый отклик!\n'
                f'Прочитать отклик:\nhttp://127.0.0.1:8000/board/feedbacks/{feedback.article.id}',
        from_email='NewsPortalDjango@yandex.ru',
        recipient_list=[feedback.article.author.email, ],
    )


@shared_task
def feedback_accept_send_email(feedback_id):
    feedback = Feedback.objects.get(id=feedback_id)
    print(feedback.article.author.email)
    send_mail(
        subject=f'BB: Ваш отклик принят!',
        message=f'Доброго дня, {feedback.author}, Автор объявления {feedback.article.title} принял Ваш отклик!\n'
                f'Посмотреть принятые отклики:\nhttp://127.0.0.1:8000/board/feedbacks',
        from_email='NewsPortalDjango@yandex.ru',
        recipient_list=[feedback.article.author.email, ],
    )


@shared_task
def send_mail_monday_8am():
    # Создаем список всех объявлений, созданных за последние 7 дней (list_week_posts)
    now = timezone.now()
    list_week_articles = list(Article.objects.filter(date_time__gte=now - timedelta(days=7)))
    if list_week_articles:
        for user in User.objects.filter():
            print(user)
            list_articles = ''
            for article in list_week_articles:
                list_articles += f'\n{article.title}\nhttp://127.0.0.1:8000/board/{article.id}'
            send_mail(
                subject=f'News Portal: посты за прошедшую неделю.',
                message=f'Доброго дня, {user.username}!\nПредлагаем Вам ознакомиться с новыми объявлениями, '
                        f'появившимися за последние 7 дней:\n{list_articles}',
                from_email='NewsPortalDjango@yandex.ru',
                recipient_list=[user.email, ],
            )
