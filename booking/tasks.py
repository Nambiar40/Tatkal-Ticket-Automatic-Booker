from celery import shared_task
from .models import BookingTask
from django.core.mail import send_mail

@shared_task
def execute_booking(task_id):
    task = BookingTask.objects.get(id=task_id)
    task.status = 'Completed'
    task.save()

    send_mail(
        subject='Tatkal Booking Completed',
        message=f'Booking for {task.train_number} is completed.',
        from_email='your_email@gmail.com',
        recipient_list=[task.user.email],
    )