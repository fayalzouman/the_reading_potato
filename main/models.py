from django.db import models
from django.contrib.auth.models import User


class Article(models.Model):
    title = models.CharField(max_length=250)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="articles")
    created_on = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

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