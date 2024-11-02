from django.db import models
from django.utils import timezone

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
    
    
    title = models.CharField(max_length=100)
    details = models.TextField()
    date = models.DateTimeField(default=timezone.now)
    tags = models.ManyToManyField(Tag, related_name='todos', blank=True)
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)
    
    def __str__(self):
        return f"{self.title} ({self.get_priority_display()})"