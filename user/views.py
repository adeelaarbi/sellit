from django.contrib.auth.forms import (
    UserCreationForm,
)
from django.urls import (
    reverse_lazy,
)
from django.views import generic

# Create your views here.


class RegisterView(generic.CreateView):
    template_name = 'user/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy(
        'app:posts'
    )