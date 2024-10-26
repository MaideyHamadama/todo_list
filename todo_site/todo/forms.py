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
    
    # Make the field detail to be optional
    details = forms.CharField(widget=forms.Textarea(attrs={"required": False}))
    
    def clean_details(self):
        details = self.cleaned_data.get('details')
        if not details or details.strip() == "":
            raise forms.ValidationError('Details field cannot be empty')
        return details