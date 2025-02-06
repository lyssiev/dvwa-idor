from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    body = forms.CharField(required=True)

    class Meta:
        model = Post
        exclude = ("user", )

    def clean_body(self):
        body = self.cleaned_data.get('body')
        if len(body) > 140:
            raise forms.ValidationError("Your post cannot have more than 140 characters.")
        return body