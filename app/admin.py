from django.contrib import admin
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User, Group

from .utils import unique_slug_generator
from .models import Category, Post, PostImage, Tag, Location

# Register your models here.


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created', '_image', 'slug', 'parent']
    readonly_fields = ['_image', 'slug']

    def _image(self, obj):
        return obj.load_image()

    def save_model(self, request, obj, form, change):
        obj.slug = unique_slug_generator(obj)
        super().save_model(request, obj, form, change)


class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 2


class TagsInline(admin.TabularInline):
    model = Tag
    readonly_fields = ['slug']
    extra = 3


class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'slug', 'created', '_tags', '_description', 'sold', '_images', 'approved']
    readonly_fields = ['slug']
    search_fields = ['title', 'category__name', 'tag__name', 'location__name', 'location__parent__name']

    inlines = [TagsInline, PostImageInline]

    def save_model(self, request, obj, form, change):
        obj.slug = unique_slug_generator(obj)
        super().save_model(request, obj, form, change)

    def _description(self, obj):
        return str(obj.description)[:20] + " [...]"

    def _tags(self, obj):
        tags = [tag.name for tag in obj.get_tags()]
        return ', '.join(tags)

    def _images(self, obj):
        return obj.images(height=100, widht=100, cls="img-thumbnail")

    # def _location(self, obj):
    #     print(obj.location.__dir__())
    #     return obj.locations()


class LocationAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'parent_id', 'country']


admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.unregister([User, Group])
