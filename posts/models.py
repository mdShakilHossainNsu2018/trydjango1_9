from django.db import models
import uuid
import os
from django.conf import settings
# Create your models here.
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


# def user_directory_path(instance, filename):
#     # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
#     return '{0}/{1}'.format(instance.id, filename)

class PostManager(models.Manager):
    def active(self, *args, **kwargs):
        return super(PostManager, self).filter(draft=False).filter(publish__lte=timezone.now())


class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, default=1, on_delete=models.CASCADE)
    title = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
    image = models.ImageField(upload_to='{}'.format(str('%d-%m-%y')), null=True, blank=True,
                              width_field="width_field",
                              height_field="height_field")
    height_field = models.IntegerField(default=0)
    width_field = models.IntegerField(default=0)
    draft = models.BooleanField(default=False)
    publish = models.DateField(auto_now=False, auto_now_add=False)

    objects = PostManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("posts:detail", kwargs={"slug": self.slug})

    class Meta:
        ordering = ['-timestamp', '-updated']


def getemptyfiles(rootdir):
    # print(rootdir)
    for root, dirs, files in os.walk(rootdir):
        # print('dir'+str(dirs))
        # print("root"+str(root))
        # print('files'+str(files))
        for d in ['RECYCLER', 'RECYCLED']:
            # print(d)
            if d in dirs:
                os.remove(d)

        for f in dirs:
            fullname = os.path.join(root, f)
            try:
                # print("size"+str(os.path.getsize(fullname)))
                # print("dirFull"+ str(fullname))
                if os.path.getsize(fullname) == 4096:

                    # print("0 full"+fullname)
                    os.rmdir(fullname)
            except :
                continue


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
@receiver(post_delete, sender=Post)
def submission_delete(sender, instance, **kwargs):
    instance.image.delete(False)
    # print("work")
    getemptyfiles(BASE_DIR+'/media')


def create_slug(instance, new_slug=None):
    slug = slugify(instance.title)

    if new_slug is not None:
        slug = new_slug
    qs = Post.objects.filter(slug=slug).order_by('-id')
    exist = qs.exists()

    if exist:
        new_slug = "{0}-{1}".format(slug, qs.first().id)
        return create_slug(instance, new_slug=new_slug)
    return slug


def pre_save_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)


pre_save.connect(pre_save_post_receiver, sender=Post)


