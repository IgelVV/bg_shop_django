from celery import shared_task
from django.core.mail import send_mail
from .models import Order


@shared_task
def order_confirmed(order_id):
    """
    Задание по отправке уведомления по электронной почте
    при успешном создании заказа.
    """
    order = Order.objects.get(id=order_id)
    subject = f'Order nr. {order.id}'
    message = f'Dear {order.user.first_name},\n\n' \
              f'You have successfully placed an order.' \
              f'Your order ID is {order.id}.'
    mail_sent = send_mail(subject, message,
                          'admin@myshop.com',
                          [order.user.email])
    return mail_sent