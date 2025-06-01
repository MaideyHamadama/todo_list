from datetime import timedelta, datetime, date
from django.shortcuts import render,redirect
from django.contrib import messages
from dateutil.relativedelta import relativedelta
from django.db.models import Q # Used to search simulataneously on multiple fields of a table in the database/model
from django.utils.timezone import timedelta, now
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import csv,json
import pandas as pd

# import todo form and models
from .forms import TodoForm
from .models import Todo,Tag,Notification
from .tasks import send_due_soon_email

# Create your views here.

def create_recurring_tasks(task, start_date, frequency):
    # Frequency delta: weekly = 7 days, monthly = ~30 days
    if frequency == 'daily':
        frequency_delta = timedelta(days=1)
    elif frequency == 'weekly':
        frequency_delta = timedelta(days=7)
    elif frequency == 'monthly':
        frequency_delta = relativedelta(months=1)
        
    current_date = start_date   
    while current_date + frequency_delta <= task.due_date:
        current_date += frequency_delta
        # Stop if the next recurrence exceeds the due date
        if current_date >= task.due_date:
            break
        new_task = Todo.objects.create(
            title = task.title,
            details = task.details,
            due_date = current_date,
            priority = task.priority,
            is_recurring=True,
            recurrence_interval=frequency
        )
        new_task.save() # Save the new task before assigning tags
        new_task.tags.set(task.tags.all())
        new_task.save()
    return None
        
def index(request):
    # Get query parameters
    selected_tag = request.GET.get('tag', None)
    search_query = request.GET.get("search", "")
    priority_filter = request.GET.get("priority", "")
    sort_option = request.GET.get("sort", "")
    
    # Base queryset
    item_list = Todo.objects.all()
    
    # Filter tasks
    if selected_tag:
        item_list = Todo.objects.filter(tags__name=selected_tag).order_by('-priority', 'due_date', '-date')
    
    if search_query:
        item_list = item_list.filter(Q(title__icontains=search_query) | Q(details__icontains=search_query))
    
    if priority_filter:
        item_list = item_list.filter(priority=priority_filter)
    
    # Sorting logic
    sort_fields = {
        "title": "title",
        "-title": "-title",
        "due_date": "due_date",
        "-due_date": "-due_date",
        "priority": "priority",
        "-priority": "-priority",
    }
    if sort_option in sort_fields:
        item_list = item_list.order_by(sort_fields[sort_option])
    else:
        item_list = item_list.order_by('-priority', 'due_date', '-date')
        
    # Handle form submission
    if request.method == "POST":
        form = TodoForm(request.POST)
        if form.is_valid():
            task = form.save()
            # Send email notification for due tasks
            if task.due_date:
                notify_at = task.due_date - timedelta(days=7)
                # If the task is due day greater than a week
                if notify_at >= now().date():
                    notify_at = datetime.combine(notify_at, datetime.min.time())
                    send_due_soon_email(task.id, schedule=notify_at)
                else:
                    send_due_soon_email(task.id, schedule=now() + timedelta(seconds=5))          
            # If the task is recurring, handle the recurrence creation logic
            is_recurring = task.is_recurring
            recurrence_interval = task.recurrence_interval
            if is_recurring and request.POST['due_date']:
                # Calculate the recurrences based on interval and due date
                start_date = datetime.now().date()
                task.save()
                
                # Handle task creation based on frequency
                create_recurring_tasks(task, start_date, recurrence_interval)
            else:
                task.save()  
                
            return redirect('todo')
    else:
        form = TodoForm()
        
    # Get all tags for filtering and form
    tags = Tag.objects.all()
    
    # Get all notifications
    notifications = Notification.objects.filter(is_read=False).order_by('-created_at')[:10] # Limit to 10 most recent notifications
    # Context for rendering the page
    page = {
        "form" : form,
        "list" : item_list,
        "tags" : tags,
        "notifications": notifications,
        "title" : "TODO LIST"
    }
    return render(request, 'todo/index.html', page)

### Function to remove item ###
def remove(request, item_id):
    item = Todo.objects.get(id=item_id)
    item.delete()
    messages.info(request, "item removed !!!")
    return redirect('todo')

@require_POST
def ajax_mark_as_read(request):
    notif_id = request.POST.get("id")
    if notif_id:
        Notification.objects.filter(id=notif_id).update(is_read=True)
        return JsonResponse({"status":"success"})
    return JsonResponse({"status":"error"}, status=400) 

def export_tasks(request, format):
    tasks = Todo.objects.all()
    
    if format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="tasks.csv"'
        writer = csv.writer(response)
        writer.writerow(['Title', 'Details', 'Due Date', 'Priority', 'Date', 'Tags', 'Is Recurring', 'Recurrence Interval'])
        for task in tasks:
            tags = ','.join([tag.name for tag in task.tags.all()])  # Join tag names into a single string
            writer.writerow([task.title, task.details, task.due_date, task.priority, task.date, tags, task.is_recurring, task.recurrence_interval])
        return response
    elif format == 'json':
        response = HttpResponse(content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="tasks.json"'
        task_data = []
        for task in tasks:
            tags = list(task.tags.values_list('name', flat=True))  # Get tag names as a list
            task_data.append(
                {'Title' : task.title,
                 'Details' : task.details,
                 'Due Date' : task.due_date,
                 'Priority' : task.priority,
                 'Date' : task.date,
                 'Tags' : tags,
                 'Is Recurring' : task.is_recurring,
                 'Recurrence Interval' : task.recurrence_interval}
            )
        response.write(json.dumps(task_data, indent=4, default=str))  # Convert to JSON string
        return response
    else:
        return HttpResponse("Unsupported format", status=400)    

def import_tasks(request):
    if request.method == 'POST' and request.FILES.get('import_file'):
        file = request.FILES['import_file']
        ext = file.name.split('.')[-1].lower()

        if ext == 'json':
            data = json.load(file)
        elif ext == 'csv':
            data = list(csv.DictReader(file.read().decode('utf-8').splitlines()))
        else:
            return HttpResponse("Unsupported file type", status=400)

        # Create tasks
        for item in data:
            task = Todo.objects.create(
                title=item['Title'],
                details=item['Details'],
                due_date=datetime.strptime(item['Due Date'], "%Y-%m-%d").date(),
                priority=item.get('Priority', 2),  # default to medium
                date=item.get('Date', datetime.now()),
                is_recurring=item.get('Is Recurring', False),
                recurrence_interval=item.get('Recurrence Interval', None)
            )
            if ext == 'json':
                for tag_name in item.get('Tags', []):
                    tag, _ = Tag.objects.get_or_create(name=tag_name)
                    task.tags.add(tag)
            else:
                tag_names = [t.strip() for t in item.get('Tags', '').split(',') if t.strip()]
                for t_name in tag_names:
                    tag, _ = Tag.objects.get_or_create(name=t_name)
                    task.tags.add(tag)
            # Send email notification for due tasks
            if task.due_date:
                notify_at = task.due_date - timedelta(days=7)
                # If the task is due day greater than a week
                if notify_at >= now().date():
                    notify_at = datetime.combine(notify_at, datetime.min.time())
                    send_due_soon_email(task.id, schedule=notify_at)
                else:
                    send_due_soon_email(task.id, schedule=now() + timedelta(seconds=5))    
        return redirect('todo')  # Replace with your task view name
    return HttpResponse("No file uploaded", status=400)