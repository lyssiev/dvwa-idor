from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    body = forms.CharField(required=True)

    class Meta:
        model = Post
        exclude = ("user", )