from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from app.models import Post, Category, Location


class PostSitemap(Sitemap):
    def items(self):
        return Post.objects.all()


class CategorySitemap(Sitemap):
    def items(self):
        return Category.objects.all()


class LocationSitemap(Sitemap):
    def items(self):
        return Location.objects.all()

    def location(self, item):
        item = self.items().filter(name=item).first()
        return reverse('search-list', args=[str(item.name).lower()])


class PostLocationSitemap(Sitemap):
    def items(self):
        posts = [post.title + "_in_" + location.name for post in Post.objects.all() for location in Location.objects.all()]

        return posts

    def location(self, obj):
        return reverse('search-list', args=[str(obj).lower()])


class PostCategorySitemap(Sitemap):
    def items(self):
        posts = [post.title + "_in_" + location.name for post in Post.objects.all() for location in Category.objects.all()]
        return posts

    def location(self, obj):
        return reverse('search-list', args=[str(obj).lower()])