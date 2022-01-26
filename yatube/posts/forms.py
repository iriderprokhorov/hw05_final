from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            "text",
            "group",
            "image",
        )
        help_texts = {
            "text": "Text for new post",
            "group": "Group's post",
            "image": "pickup the picture",
        }

    def clean_text(self):
        data = self.cleaned_data["text"]
        if not data:
            raise forms.ValidationError("Please fill empty field")
        return data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
