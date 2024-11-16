from datetime import timedelta, datetime
from django.shortcuts import render,redirect
from django.contrib import messages

# import todo form and models
from .forms import TodoForm
from .models import Todo,Tag

# Create your views here.

def create_recurring_tasks(task, start_date, frequency):
    if frequency == 'daily':
        while start_date < task.due_date:
            start_date += timedelta(days=1)
            new_task = Todo.objects.create(
                title = task.title,
                details = task.details,
                due_date = start_date,
                priority = task.priority,
                is_recurring=False,
                recurrence_interval=None
            )
            new_task.save() # Save the new task before assigning tags
            new_task.tags.set(task.tags.all())
            new_task.save()
    elif frequency == 'weekly':
        while start_date < task.due_date:
            start_date += timedelta(weeks=1)
            new_task = Todo.objects.create(
                title = task.title,
                details = task.details,
                due_date = start_date,
                is_recurring=False,
                recurrence_interval=None,
                priority = task.priority
            )
            new_task.save()
            new_task.tags.set(task.tags.all())
            new_task.save()
    elif frequency == 'monthly':
        while start_date < task.due_date:
            start_date = start_date.replace(month=start_date.month % 12 + 1)
            new_task = Todo.objects.create(
                title = task.title,
                details = task.details,
                due_date = start_date,
                is_recurring=False,
                recurrence_interval=None,
                priority = task.priority
            )
            new_task.save()
            new_task.tags.set(task.tags.all())
            new_task.save()
    return None
        
def index(request):
    # Get the selected tag from the query parameters, if any
    selected_tag = request.GET.get('tag', None)
    
    # Filter tasks by the selected tag if present and ordering by priority then date
    if selected_tag:
        item_list = Todo.objects.filter(tags__name=selected_tag).order_by('-priority', '-date')
    else:
        item_list = Todo.objects.order_by('-priority', '-date')
    
    # Handle form submission
    if request.method == "POST":
        form = TodoForm(request.POST)
        if form.is_valid():
            task = form.save()
            # If the task is recurring, handle the recurrence creation logic
            is_recurring = task.is_recurring
            recurrence_interval = task.recurrence_interval
            due_date = task.due_date
            
            if is_recurring and due_date:
                # Calculate the recurrences based on interval and due date
                start_date = datetime.now().date()
                task.save()
                
                # Handle task creation based on frequency
                create_recurring_tasks(task, start_date, recurrence_interval)
                if recurrence_interval == 'daily':
                    task.delete() # Delete the original task to avoid the last recurrent task and the original task having the same date in the database
            else:
                task.save()  
                
            return redirect('todo')
    else:
        form = TodoForm()
        
    # Get all tags for filtering and form
    tags = Tag.objects.all()
    
    # Context for rendering the page
    page = {
        "form" : form,
        "list" : item_list,
        "tags" : tags,
        "title" : "TODO LIST"
    }
    return render(request, 'todo/index.html', page)

### Function to remove item ###
def remove(request, item_id):
    item = Todo.objects.get(id=item_id)
    item.delete()
    messages.info(request, "item removed !!!")
    return redirect('todo')