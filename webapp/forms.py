from django import forms
from .models import Post, Profile, Comment

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
    
class PrivacyForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['private']

class CommentForm(forms.ModelForm):
    body = forms.CharField(required=True, max_length=140)

    class Meta:
        model = Comment
        exclude = ("user", "post")

    def clean_body(self):
        body = self.cleaned_data.get('body')
        if len(body) > 140:
            raise forms.ValidationError("Your comment cannot have more than 140 characters.")
        return body