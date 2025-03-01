from celery import shared_task
from django.core.mail import send_mail
from django.utils.timezone import now
from todo.models import Todo

@shared_task
def send_task_notifications():
    today = now().date()
    tasks = Todo.objects.filter(due_date=today)

    for task in tasks:
        subject = f"Reminder: Task '{task.title}' is due today"
        message = f"Hello,\n\nYour task '{task.title}' is due today.\n\nDetails:\n{task.description}\n\nMake sure to complete it on time!"
        recipient = "dilanechristian2@gmail.com"  # Ensure `user` ForeignKey exists

        if recipient:
            send_mail(subject, message, 'your_email@example.com', [recipient])
            print(f"Notification sent to {recipient} for task '{task.title}'")

