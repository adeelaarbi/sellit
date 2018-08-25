from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Post, PostImage, Location, Category


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')


class PostImageForm(forms.ModelForm):
    class Meta:
        model = PostImage
        fields = ['image', 'post']


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('title', 'slug', 'description', 'price', 'image', 'phone_no', 'location', 'category')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['location'].queryset = Location.objects.filter(parent=None)
        self.fields['category'].queryset = Category.objects.filter(parent=None)