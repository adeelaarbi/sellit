from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from app.models import Post, Category, Location, Tag


class PostSitemap(Sitemap):
    limit = 10
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
        return reverse('app:search-list', args=[item.slug()])


class CategoryLocationSitemap(Sitemap):
    def items(self):
        posts = [str(post.slug + "-in-" + location.slug()) for post in Category.objects.all() for location in Location.objects.all()]
        return posts

    def location(self, obj):
        return reverse('app:search-list', args=[str(obj).lower()])


class TagLocationSitemap(Sitemap):
    def items(self):
        posts = [str(post.slug + "-in-" + location.slug()) for post in Tag.objects.all() for location in Location.objects.all()]
        return posts

    def location(self, obj):
        return reverse('app:search-list', args=[str(obj).lower()])