from django.db import models
from django.utils import timezone
from datetime import timedelta

# Create your models here.

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name
    
class Todo(models.Model):
    PRIORITY_CHOICES = [
        (3, 'High'),
        (2, 'Medium'),
        (1, 'Low')
    ]
    
    RECURRENCE_INTERVAL_CHOICES = [("daily","Daily"), ("weekly", "Weekly"), ("monthly", "Monthly")]
    
    title = models.CharField(max_length=100)
    details = models.TextField()
    date = models.DateTimeField(default=timezone.now)
    tags = models.ManyToManyField(Tag, related_name='todos', blank=True)
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)
    due_date = models.DateTimeField(null=True, blank=True) # Optional due date
    is_recurring = models.BooleanField(default=False)
    recurrence_interval = models.CharField(
        max_length=20,
        choices=RECURRENCE_INTERVAL_CHOICES,
        blank=True,
        null=True
    )
    
    def save(self, *args, **kwargs):
        # Set the due_date automatically if the task is recurring
        if self.is_recurring and not self.due_date:
            self.due_date = self.calculate_next_due_date()
        super().save(*args,**kwargs)
    
    def calculate_next_due_date(self):
        """ Calculate the next due date based on recurrence interval. """
        if self.recurrence_interval == "daily":
            return self.date + timedelta(days=1)
        elif self.recurrence_interval == "weekly":
            return self.date + timedelta(weeks=1)
        elif self.recurrence_interval == "monthly":
            return self.date + timedelta(days=30)
        return self.date
    
    def __str__(self):
        return f"{self.title} ({self.get_priority_display()})"
    
    def is_due_soon(self):
        """ Check if a task is due within the next day. """
        return self.due_date and self.due_date <= timezone.now() + timedelta(days=1)
    
    def is_overdue(self):
        """ Check if a task is overdue. """
        return self.due_date and self.due_date < timezone.now()