from django.core.mail import send_mail
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from board.models import Feedback, Article


@receiver(pre_save, sender=Feedback)
def handler(sender, instance, created, **kwargs):
    if instance.status:
        mail = instance.author.email
        send_mail(
            'Объект',
            'message',
            'тут почта',
            [mail],
            fail_silently=False,
        )
    mail = instance.article.author.email
    send_mail(
        'Объект',
        'message',
        'тут почта',
        [mail],
        fail_silently=False,
    )


@receiver(post_save, sender=Article)
def notify_about_new_post(sender, instance, created, **kwargs):
    """сигнал уведомление о выходе новой статьи через post_save"""
    if created and instance.__class__.__name__ == 'Post':
        send_notifications.apply_async(
            (instance.preview(), instance.pk, instance.title),
            countdown=10)
