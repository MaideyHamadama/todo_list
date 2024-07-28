from django import forms
from .models import Todo,Tag

class TodoForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget = forms.CheckboxSelectMultiple,
        required = False
    )
    class Meta:
        model = Todo
        fields = "__all__"