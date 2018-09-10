import pycountry
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
# Create your models here.

countries = ((str(country.name).lower(), str(country.name)) for country in pycountry.countries)


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, blank=True, null=True)

    class Meta:
        abstract = True


class Category(BaseModel):
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='app/static/app/categories', null=True, blank=True)
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "categories"       #categories under a parent with same
        ordering = ('-created', 'name')

    def __str__(self):                           # __str__ method elaborated later in
        # full_path = [self.name]                  # post.  use __unicode__ in place of
        #                                          # __str__ if you are using python 2
        # k = self.parent
        #
        # while k is not None:
        #     full_path.append(k.name)
        #     k = k.parent
        #
        # return ' -> '.join(full_path[::-1])
        return self.name

    def get_absolute_url(self):
        return reverse('app:search-list', args=[str(self.name).replace(' ', '-').lower()])

    def load_image(self, width=50, height=50):
        url = '/static/sellit.png'
        if self.image:
            url = '/static/app/' + str(self.image.url).rsplit('app/', 1)[1]
        return mark_safe('<img src="{}" width="{}" height="{}"'.format(url, width, height))


class Location(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=30, choices=countries, default="pakistan")
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children',default='Pakistan', on_delete=models.CASCADE)

    class Meta:
        ordering = ('name',)

    def __str__(self):  # __str__ method elaborated later in
        # full_path = [self.name]  # post.  use __unicode__ in place of
        # # __str__ if you are using python 2
        # k = self.parent
        #
        # while k is not None:
        #     full_path.append(str(k.name))
        #     k = k.parent
        #
        # return ' --> '.join(full_path)
        return self.name

    def location(self):
        full_path = [self.name]
        k = self.parent

        while k is not None and k.parent_id is not None:
            full_path.append(str(k.name))
            k = k.parent

        return ' '.join(full_path[::-1])


class Post(BaseModel):
    title = models.CharField(max_length=100)
    price = models.PositiveIntegerField(default=0)
    phone_no = models.CharField(max_length=20)
    image = models.ImageField(upload_to="app/static/app/post", null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    description = models.TextField(max_length=500)
    sold = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    views = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('-created', 'title')

    def get_absolute_url(self):
        return reverse('app:post-detail', args=[str(self.slug)])

    def get_tags(self):
        return self.tag_set.all()

    def tags(self):
        tags = [tag.name for tag in self.get_tags()]
        return ', '.join(tags)

    def images(self, height=50, widht=50, cls=""):
        images = ['<img src="{}" width="{}" height="{}" class="{}" />'.format('/static/app/' + str(image.image.url).rsplit('app/', 1)[1], height, widht, cls) for image in self.postimage_set.all() if str(image.image.name).startswith('app')]
        images = '  '.join(images)
        return mark_safe(images)

    def images_url(self):
        return ['/app/' + str(image.image.url).rsplit('app/', 1)[1] for image in self.postimage_set.all()]

    def post_image(self, height=50, width=50, cls=""):
        image = '/static/sellit.png'
        if self.image.name:
            image = '<img src="{}" width="{}" height="{}" class="{}" />'.format('/static/app/' + str(self.image.url).rsplit('app/', 1)[1], height, width, cls)
        return mark_safe(image)

    def post_image_url(self):
        url = 'sellit.png'
        if self.image.name:
            url = '/app/' + str(self.image.url).rsplit('app/', 1)[1]
        return url

    def locations(self):
        location = str(self.location).rsplit('-->', -1)
        return location[1:]

    def address(self):
        full_path = [self.location.name]
        k = self.location.parent

        while k is not None:
            full_path.append(str(k.name))
            k = k.parent
        return ' '.join(full_path) + ' Pakistan'

    def categories(self):
        try:
            full_path = [self.category.name]
            k = self.category.parent

            while k is not None:
                full_path.append(str(k.name))
                k = k.parent
            return ' '.join(full_path)
        except AttributeError as attr_error:
            return "all"

    def search_query(self):
        query = str(self.title + " " + self.tags().replace(',', '') + " " + self.categories() + " " + self.address()).lower()
        return query


class Tag(BaseModel):
    post = models.ForeignKey(Post, blank=True, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class PostImage(models.Model):
    image = models.ImageField(max_length=50, upload_to='app/static/app/post', blank=True, null=True)
    post = models.ForeignKey(Post, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.image.name

    def load_image(self, width=50, height=50):
        url = '/static/sellit.png'
        if self.image:
            url = '/static/app/' + str(self.image.url).rsplit('app/', 1)[1]
        return mark_safe('<img src="{}" width="{}" height="{}"'.format(url, width, height))

    def get_posts(self):
        if self.post:
            return self.post