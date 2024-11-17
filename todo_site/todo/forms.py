from django import forms
from .models import Todo,Tag
from django.forms.widgets import DateInput
from datetime import datetime, timedelta

class TodoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Exclude "complete" tag from the tags queryset hence don't appears in the checkbox options
        self.fields['tags'].queryset = Tag.objects.exclude(name="Completed")

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget = forms.CheckboxSelectMultiple,
        required = False
    )
    # Explicitly set the details field widget without required attribute
    details = forms.CharField(
        widget=forms.Textarea(),
        required = False
    )
    priority = forms.ChoiceField(
        choices=Todo.PRIORITY_CHOICES,
        widget=forms.Select,
        required=True
    )
    due_date = forms.DateField(
        widget=DateInput(attrs={
            'type':'date'
        }),
        required=False
    )
    recurrence_interval = forms.ChoiceField(
        choices=[("", "None"), ("daily","Daily"), ("weekly", "Weekly"), ("monthly", "Monthly")],
        required=False,
        label="Repeat",
        help_text="Choose a recurrence frequency. Weekly tasks need a due date > 7 days, monthly > 30 days."
    )
    
    class Meta:
        model = Todo
        fields = "__all__"
        
    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        today = datetime.now().date()
        if due_date and due_date <= today:
            raise forms.ValidationError('Due date cannot be before today')  
        return due_date

    def clean_recurrence_interval(self):
        recurrence_interval = self.cleaned_data.get('recurrence_interval')
        is_recurring = self.cleaned_data.get('is_recurring')
        if is_recurring and not recurrence_interval:
            raise forms.ValidationError("If a task is recurring, a recurrence interval must be set.")
        elif recurrence_interval and not is_recurring:
            self.add_error('is_recurring', "If a task has been set a recurrence interval, it must be set to recurring")
        return recurrence_interval
    
    def clean_details(self):
        details = self.cleaned_data.get('details')
        if not details or details.strip() == "":
            raise forms.ValidationError('Details field cannot be empty')
        return details
    
    def clean(self):
        cleaned_data = super().clean()
        due_date = cleaned_data.get('due_date')
        recurrence_interval = cleaned_data.get('recurrence_interval')
        is_recurring = cleaned_data.get('is_recurring')
        if is_recurring and recurrence_interval:
            today = datetime.now().date()
            # Validation for weekly recurrence
            if recurrence_interval == 'weekly' and due_date <= today + timedelta(days=7):
                raise forms.ValidationError("The due date must be at least a week from today for weekly recurrence.")
                # Validation for monthly recurrence
            if recurrence_interval == 'monthly' and due_date <= today + timedelta(days=30):
                raise forms.ValidationError("The due date must be at least a month from today for monthly recurrence.")
        return cleaned_data
