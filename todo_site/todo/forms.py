from django import forms
from .models import Todo,Tag

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

    class Meta:
        model = Todo
        fields = "__all__"
    
    
    def clean_details(self):
        details = self.cleaned_data.get('details')
        if not details or details.strip() == "":
            raise forms.ValidationError('Details field cannot be empty')
        return details