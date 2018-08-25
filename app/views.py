import pycountry
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.views import generic
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from app.utils import upload_post_images, add_tags
from .forms import SignUpForm, PostForm, PostImageForm
from .models import Post, Tag, Location, Category, PostImage

countries = [{str(country.name).lower(): str(country.name)} for country in pycountry.countries]

# Create your views here


def signup(request):
    # errors = []
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('posts')
    else:
        form = SignUpForm()
    return render(request, 'posts/signup.html', {'errors': form.errors})


def load_locations_categories(request):
    location_id = request.GET.get('location')
    type = request.GET.get('type', "Select")
    data = request.GET.get('data', "location")

    if data == "category":
        category_id = request.GET.get('category')
        categories = Category.objects.filter(parent_id=category_id).order_by('name')
        return render(request, 'posts/options.html', {'options': categories, 'type': type})

    locations = Location.objects.filter(parent_id=location_id).order_by('name')
    return render(request, 'posts/options.html', {'options': locations, 'type': type})


def make_url(request):
    location_id = request.GET.get('location', None)
    query = request.GET.get('query', None)
    if not query and not location_id:
        query = 'all_in_pakistan'
    if location_id:
        location = Location.objects.get(pk=location_id)
        location = location.name
        if query:
            query = query + "_in_" + location
            return redirect('search-list', query.lower())
        query = location
    return redirect('search-list', query.lower())


def search_list(request, query=None):
    states = Location.objects.filter(parent=None)
    posts = Post.objects.filter(approved=True)
    if '_' in query:
        title = str(query).replace('_', ' ')
        query, location = str(query).rsplit('_in_', -1)[0], str(query).rsplit('_in_', -1)[1]
        posts = filter(lambda instance: str(location).lower() in instance.search_query(), posts)
        if str(query).lower() != "all":
            posts = filter(lambda instance: str(query).lower() in instance.search_query(), posts)
        return render(request, 'posts/search_list.html', {'posts': posts, 'states': states, 'title': title})
    title = query
    posts = filter(lambda instance: str(query).lower() in instance.search_query(), posts)
    return render(request, 'posts/search_list.html', {'posts': posts, 'states': states, 'title': title})


@login_required(login_url='login')
def myads(request):
    posts = Post.objects.filter(user=request.user)
    return render(request, 'posts/myads.html', {'posts': posts, 'title': 'my ads'})


class PostListView(generic.ListView):
    model = Post
    template_name = 'posts/index.html'
    context_object_name = 'posts'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet
        states = Location.objects.filter(parent=None)
        context['states'] = states
        locations = [location for state in states
                     for location in Location.objects.filter(parent_id__exact=state.id)]
        categories = Category.objects.filter(parent=None)
        context['locations'] = locations
        context['categories'] = categories
        context['title'] = 'Trade | Home'
        return context

    def get_queryset(self):
        query = self.request.GET.get('query')
        queryset = Post.objects.filter(approved=True).order_by('-created')
        if query:
            queryset = filter(lambda x: str(query).lower() in str(x.title).lower() or
                                        str(query).lower() in str(x.category.name).lower() or
                                        str(query).lower() in str(x.category.parent.name).lower() or
                                        str(query).lower() in str(x.location).lower() or
                                        str(query).lower() in str(x.address()).lower(), queryset)
        return queryset[:4]


class PostDetailView(generic.DetailView):
    model = Post
    template_name = 'posts/details.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        object = self.get_object()
        posts = Post.objects.filter(category=object.category, approved=True)
        context['posts'] = posts
        context['title'] = object.title + " | details"
        return context


class PostAddView(generic.CreateView):
    model = Post
    template_name = 'posts/add_post.html'
    form_class = PostForm
    success_url = 'posts'
    # queryset = None

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['title'] = 'add new ads'
        return context

    @method_decorator(login_required(login_url='login'), name='dispatch')
    def post(self, request, *args, **kwargs):
        tags = request.POST.get('tags', [])
        form = self.get_form()
        errors = form.errors
        if tags:
            tags = str(tags).rsplit(', ', -1)
        if request.method == 'POST':
            # request.POST['location'] = request.POST.get("address")
            # request.POST['category'] = request.POST.get("sub_category")
            form = self.get_form()
            if form.is_valid:
                print(request.POST)
                category_id = request.POST.get('sub_category')
                location_id = request.POST.get('area')
                print("Area :", location_id)
                category = Category.objects.get(pk=category_id)
                location = Location.objects.get(pk=int(location_id))

                form.save()
                instance = self.model.objects.get(slug=request.POST.get('slug'))
                instance.location = location
                instance.category = category
                instance.user = request.user
                instance.save()
                image = upload_post_images(instance, request)

                if not image.get('uploaded', False):
                    errors.update({'image': 'unable to upload images'})
                tag = add_tags(instance, tags)
                if not tag.get("added", False):
                    errors.update({'tags': 'unable to set tags'})
                return redirect(self.success_url)

        return render(request, 'posts/add_post.html', {'errors': form.errors})


class PostUpdateView(generic.UpdateView):
    model = Post
    template_name = 'posts/update_post.html'
    fields = ['title', 'slug', 'description', 'price', 'image', 'phone_no', 'location', 'category']
    context_object_name = 'post'
    success_url = 'posts'
    # queryset = None

    @method_decorator(login_required, name='dispatch')
    def get(self, request, *args, **kwargs):
        instance = Post.objects.get(pk=kwargs.get('pk'))
        form = PostForm(instance=instance)
        categories = Category.objects.filter(parent=instance.category.parent)
        locations = Location.objects.filter(parent=instance.location.parent)
        form.fields['category'].queryset = categories
        form.fields['location'].queryset = locations
        return render(request, 'posts/update_post.html', {'form': form, 'post': instance, 'title': instance.title + ' | update'})

    @method_decorator(login_required, name='dispatch')
    def post(self, request, *args, **kwargs):
        tags = request.POST.get('tags', [])
        instance = Post.objects.get(pk=kwargs.get('pk'))
        form = self.get_form()
        if tags:
            tags = str(tags).rsplit(', ', -1)
        if request.method == 'POST':
            form = self.get_form()
            errors = form.errors
            if form.is_valid:
                for k, value in form.data.items():
                    if hasattr(instance, k) and k != "slug" and k != "image" and k != "tags":
                        if k == "category":
                            v = int(value)
                            value = Category.objects.get(pk=v)
                        if k == "location":
                            v = int(value)
                            value = Location.objects.get(pk=v)
                        setattr(instance, k, value)
                instance.save()
                # return HttpResponse("Ok")
                image = upload_post_images(instance, request, update=True)
                if not image.get('uploaded', False):
                    errors.update({'image': 'unable to upload images'})
                tag = add_tags(instance, tags, update=True)
                if not tag.get("added", False):
                    errors.update({'tags': 'unable to set tags'})
                return redirect(self.success_url)

        return render(request, 'posts/update_post.html', {'errors': form.errors})

