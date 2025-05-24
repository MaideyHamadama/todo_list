# Documentation

## Administration panel access

username = superadmin \
password = superadmin

## Features Implemented

### Rich Text Feature

We implemented the rich text feature that allows the user to better format the details of a task.

*Before implementation*

![Before implementing rich text feature](resources/img1.png)

*After implementation*

![After implementing rich text feature](resources/img2.png)

### Sort, Filter and Search Feature

We implemented the sort, filter and search features that allows the user to apply these operations on the todo list elements

*Before implementation*
![Before implementing sort_filter_search feature](resources/img3.png)

*After implementation*
![After implementing sort_filter_search feature](resources/img4.png)

### Email Notification

The mail notification system was implemented to send email to user when the due date of the task is near (in this case less than 7 days or a week). To implement this feature there are some requirements first we have to install the django-background-taks using the command below :

`pip install django-background-tasks`

After installing the module we need to add the "background_task" module in the INSTALLED_APPS in [settings.py](/todo_site/todo_site/settings.py#L41-L42). Run the known migrate command to update the database with the new module.

With a proper and complete installation of the background task module we have to move on to designing the logic in the view that plans the task depending on the due date and code the send mail notification task. To do so we write in the views file the following code after saving each task.

```python
task = form.save()
# Send email notification for due tasks
notify_at = task.due_date - timedelta(days=7)
# If the task is due day greater than a week
if notify_at >= now().date():
    notify_at = datetime.combine(notify_at, datetime.min.time())
    send_due_soon_email(task.id, schedule=notify_at)
else:
    send_due_soon_email(task.id, schedule=now() + timedelta(seconds=5))          
```

We create the send mail notification task in a tasks.py file that have to be located in the todo app.

```python
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
```

*After implementation*
![After implementing the email notification feature](resources/img5.png)

Don't forget to always run the process tasks in background to track tasks for notification. This is done using the following command :

`python manage.py process_tasks`

### In-App Notification

To implement the In-App Notification, we had to work on five files. These files are tasks.py, models.py, views.py, index.html and urls.py.

In tasks.py, we added the following code to be sure upon scheduling the email notification one week close to the due date we also add an alert on the frontend of the application to notify the user along with the email. See [tasks.py](/todo_site/todo/tasks.py#L26-L30)

In models.py, we added a new object which is the notification object having the message, is_read, created_at and task fields.

- The message field contains the message that is displayed on the fronted informing the user on the corresponding task and it's due date.
- The is_read field contains the true or false status to track if the notification has been read or not.
- The created_at field just hold the date of the creation of the notification.
- The task field holds the corresponding task which due date is close.

See [models.py](/todo_site/todo/models.py#L68-L76) to have a view on the code.

In the views.py, we just called with a filter method on the notification object all the notifications with the *is_read* status as False. See [views.py](/todo_site/todo/views.py#L114-L115)

In the index.html, we added some html components alongside with interesting bootstrap features to display a notification button with an alert icon and a counter. We can see the code at [index.html](/todo_site/todo/templates/todo/index.html#L133-L154). In the same file we added some javascript to update the is_read field of the notification so as the update is executed after the user has clicked on the "Mark as read" button. We can see the script here, [index.html](/todo_site/todo/templates/todo/index.html#L289-L319).

*After Implementation*
![After implementing the In-App notification feature](/resources/img6.png)

![Notification button](/resources/img7.png)

![Mark as read button](/resources/img8.png)