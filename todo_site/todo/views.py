from django.shortcuts import render,redirect
from django.contrib import messages

# import todo form and models
from .forms import TodoForm
from .models import Todo,Tag

# Create your views here.

def index(request):
    # Get the selected tag from the query parameters, if any
    selected_tag = request.GET.get('tag', None)
    
    # Filter tasks by the selected tag if present
    if selected_tag:
        item_list = Todo.objects.filter(tags__name=selected_tag).order_by('-date')
    else:
        item_list = Todo.objects.order_by('-date')
        
    # Handle form submission
    if request.method == "POST":
        form = TodoForm(request.POST)
        if form.is_valid():
            form.save()
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