from django.core.mail import send_mail
from django.utils.timezone import now, timedelta, localtime, make_aware, datetime
from todo.models import Todo
from background_task import background

@background(schedule=60) # runs in 60 seconds from now unless rescheduled
def send_due_soon_email(task_id):
    try:
        task = Todo.objects.get(id=task_id)
        # Convert due_date to datetime format
        due_datetime = make_aware(datetime.combine(task.due_date, datetime.min.time()))
        if task.due_date < now().date():
            return
        
        if task.tags == "Completed":
            return
        
        recipient_email = 'dilanechristian2@gmail.com'
        send_mail(
            subject=f"[Reminder] Task '{task.title}' is due on {localtime(due_datetime).strftime('%d %b %Y')}",
            message=f"Hello,\n\nThis is your daily reminder: the task \"{task.title}\" is due on {localtime(due_datetime).strftime('%A, %d %B %Y at %I:%M %p')}.\n\nStay focused!",
            from_email='noreply@yourapp.com',
            recipient_list=[recipient_email],  # Replace with user's email
            fail_silently=False,
        )
        # Reschedule the task for the next day
        send_due_soon_email(task_id, schedule=now() + timedelta(days=1))
    except Todo.DoesNotExist:
         print(f"Task {task_id} does not exist.")
