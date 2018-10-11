from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        widgets = {
            'text': forms.TextInput(attrs={'class': 'comment-field'}),
        }
        fields = ['text']
