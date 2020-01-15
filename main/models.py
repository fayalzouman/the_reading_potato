from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver

class Article(models.Model):
    title = models.CharField(max_length=250)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="articles")
    created_on = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    slug = models.SlugField(blank=True)

    def __str__(self):
        return self.title

class Contribution(models.Model):
    PENDING = "Pending"
    ACCEPTED = "Accepted"
    DECLINED = "Declined"

    STATUS = (
        (PENDING, PENDING),
        (ACCEPTED, ACCEPTED),
        (DECLINED, DECLINED),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="contributions")
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="contributions")
    status = models.CharField(max_length=10 , choices=STATUS, default=PENDING)
    date = models.DateTimeField(auto_now_add=True)


class Change(models.Model):
    new_content = models.TextField()
    contribution = models.OneToOneField(Contribution, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.contribution.article)

def create_slug(instance, new_slug=None):
    slug = slugify(instance.title)
    if new_slug is not None:
        slug = new_slug
    qs = Article.objects.filter(slug=slug)
    if qs.exists():
        try:
            int(slug[-1])
            if "-" in slug:
                slug_list = slug.split("-")
                new_slug = "%s%s" % (slug[:-len(slug_list[-1])], int(slug_list[-1]) + 1)
            else:
                new_slug = "%s-1" % (slug)
        except:
            new_slug = "%s-1" % (slug)
        return create_slug(instance, new_slug=new_slug)
    return slug


@receiver(pre_save, sender=Article)
def generate_slug(instance, *args, **kwargs):
    if not instance.slug:
        instance.slug=create_slug(instance)