import pycountry
from django.contrib.auth import mixins
from django.views import generic
from django.shortcuts import render, redirect
from app.utils import upload_post_images, add_tags
from .forms import PostForm
from .models import Post, Location, Category

countries = [{str(country.name).lower(): str(country.name)} for country in pycountry.countries]

# Create your views here

def load_locations_categories(request):
    location_id = request.GET.get('location')
    type = request.GET.get('type', "Select")
    data = request.GET.get('data', "location")

    if data == "category":
        category_id = request.GET.get('category')
        categories = Category.objects.filter(parent_id=category_id)
        return render(request, 'posts/options.html', {'options': categories, 'type': type})

    locations = Location.objects.filter(parent_id=location_id)
    return render(request, 'posts/options.html', {'options': locations, 'type': type})


def make_url(request):
    if request.method == "POST":
        location_id = request.POST.get('location', None)
        query = request.POST.get('query', None)
        if not query and not location_id:
            return redirect('app:search-list', 'all-in-pakistan', permanent=True)
        if location_id:
            location = Location.objects.get(id=location_id)
            location = location.slug()
            if query:
                query = query + "-in-" + location
                return redirect('app:search-list', query, permanent=True)
            return redirect('app:search-list', location.lower(), permanent=True)
        return redirect('app:search-list', query, permanent=True)
    name = request.GET.get('location', None)
    query = request.GET.get('query', None)
    if not query and not name:
        return redirect('app:search-list', 'all-in-pakistan', permanent=True)
    if name:
        location = Location.objects.filter(name__icontains=str(name).replace('-', ' ').capitalize()).first()
        location = location.slug()
        if query:
            query = query + "-in-" + location
            return redirect('app:search-list', query, permanent=True)
        return redirect('app:search-list', location, permanent=True)
    return redirect('app:search-list', query, permanent=True)


def search_list(request, query=None):
    states = Location.objects.filter(parent=None)
    posts = Post.objects.filter(approved=True)
    if '-in-' in query:
        title = str(query.replace('-', ' ')).capitalize()
        query, location = str(query).rsplit('-in-', -1)[0], str(query).rsplit('-in-', -1)[1]
        query = query if '-' not in query else query.replace('-', ' ')
        location = location if '-' not in location else location.replace('-', ' ')
        if str(query).lower() != "all":
            posts = list(filter(lambda instance: str(query).lower() in instance.search_query(), posts))
        posts = list(filter(lambda instance: str(location).lower() in instance.search_query(), posts))
        count = len(posts)
        return render(request, 'posts/search_list.html', {'posts': posts, 'states': states, 'title': title, 'count': count})
    query = query if '-' not in query else query.replace('-', ' ')
    posts = list(filter(lambda instance: str(query).lower() in instance.search_query(), posts))
    count = len(posts)
    return render(request, 'posts/search_list.html', {'posts': posts, 'states': states, 'title': str(query).capitalize(), 'count': count})


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
        queryset = Post.objects.filter(approved=True)
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


class PostAddView(mixins.LoginRequiredMixin, generic.CreateView):
    model = Post
    template_name = 'posts/add_post.html'
    form_class = PostForm
    success_url = 'app:my-ads'
    login_url = "login"
    # queryset = None

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet
        context['title'] = 'add new ads'
        return context

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
                category_id = request.POST.get('sub_category')
                location_id = request.POST.get('area')
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


class MyAds(mixins.LoginRequiredMixin, generic.ListView):
    model = Post
    template_name = "posts/myads.html"
    context_object_name = "posts"
    login_url = "login"

    def get_queryset(self):
        posts = self.model.objects.filter(user=self.request.user)

        if self.request.user.is_superuser:
            posts = self.model.objects.all()
        return posts


class PostUpdateView(mixins.LoginRequiredMixin, generic.UpdateView):
    model = Post
    template_name = 'posts/update_post.html'
    fields = ['title', 'slug', 'description', 'price', 'image', 'phone_no', 'location', 'category']
    context_object_name = 'post'
    success_url = 'app:my-ads'
    login_url = "login"
    # queryset = None

    def get(self, request, *args, **kwargs):
        instance = Post.objects.get(pk=kwargs.get('pk'))
        form = PostForm(instance=instance)
        categories = Category.objects.filter(parent=instance.category.parent)
        locations = Location.objects.filter(parent=instance.location.parent)
        form.fields['category'].queryset = categories
        form.fields['location'].queryset = locations
        return render(request, 'posts/update_post.html', {'form': form, 'post': instance, 'title': instance.title + ' | update'})

    def post(self, request, *args, **kwargs):
        tags = request.POST.get('tags', [])
        instance = Post.objects.get(pk=kwargs.get('pk'))
        form = self.get_form()
        if tags:
            tags = str(tags).rsplit(', ', -1)
        if request.method == 'POST':
            form = self.get_form()
            errors = form.errors
            approved = bool(request.POST.get("approved", False))
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
                instance.approved = approved
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

