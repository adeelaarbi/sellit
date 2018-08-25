import random
import string
from django.core.files.storage import FileSystemStorage
from django.utils.text import slugify
from .models import Post, PostImage, Tag


def random_string(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choices(chars)[0] for _ in range(size))


def unique_slug_generator(instance, new_slug=None):
    """
    This is for a Django project and it assumes your instance
    has a model with a slug field and a title character (char) field.
    """
    if new_slug is not None:
        slug = new_slug
    else:
        title = instance.title if isinstance(instance, Post) else instance.name
        slug = slugify(title)

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(slug=slug).exists()
    if qs_exists:
        new_slug = "{slug}-{randstr}".format(
            slug=slug,
            randstr=random_string(size=4)
        )
        return unique_slug_generator(instance, new_slug=new_slug)
    return slug


def upload_post_images(instance, request, upload_to='app/static/app/post', update=False):
    fs = FileSystemStorage(location=upload_to)
    errors = []
    uploaded = True
    images = [v for k, v in request.FILES.items() if k != "image"]
    if images and update and instance.postimage_set.all().count() > 0:
        for image in instance.postimage_set.all():
            image.delete()

    for img in images:
        try:
            image = PostImage()
            filename = fs.save(img.name, img)
            uploaded_file_url = fs.url(upload_to + "/" + filename)
            image.image.name = uploaded_file_url
            image.post = instance
            image.save()
        except Exception as error:
            errors.append(str(error))
            uploaded = False
            break
    return {'uploaded': uploaded, 'errors': errors}


def add_tags(instance, tags=None, update=False):
    errors = []
    added = True
    if update and instance.tag_set.all().count() > 0:
        for tag in instance.tag_set.all():
            tag.delete()
    if tags:
        for tag in tags:
            try:
                tagobj = Tag()
                tagobj.name = tag
                slug = unique_slug_generator(tagobj)
                tagobj.slug = slug
                tagobj.post = instance
                tagobj.save()
            except Exception as error:
                added = False
                errors.append(str(error))
                break
    return {'saved': added, 'errors': errors}