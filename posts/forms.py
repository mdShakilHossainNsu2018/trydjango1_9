from django import forms

from .models import Post


class PostForm(forms.ModelForm):

    title = forms.CharField(widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Write a title...'
        }))
    content = forms.CharField(widget=forms.Textarea(
        attrs={
            'class': 'form-control',
            'placeholder': 'Contents goes here...'
        }))

    image = forms.ImageField(widget=forms.FileInput(
        attrs={
            'class': 'form-control-file',
        }
    ))

    draft = forms.BooleanField(required=False, widget=forms.CheckboxInput(
        attrs={
            'class': 'form-check-input ml-sm-2 ',
        }
    ))

    publish = forms.DateField(required=False, initial="2018-06-21", widget=forms.DateInput(
        attrs={
            'class': 'form-control ',

        }
    ),)

    class Meta:
        model = Post

        fields = [
            'title',
            'content',
            'image',
            'draft',
            'publish',
        ]

