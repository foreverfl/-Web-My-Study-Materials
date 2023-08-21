from django.contrib.auth.models import User
from django.db import models


class Notice(models.Model):  # Notice 테이블
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    date = models.DateTimeField()


class Category(models.Model):  # Category 테이블
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)


class Classification(models.Model):  # Classification 테이블
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)


class Data(models.Model):  # Data 테이블
    classification = models.ForeignKey(
        Classification, on_delete=models.CASCADE)
    name = models.TextField()
    description = models.TextField()
    frequency = models.IntegerField()

    def save(self, *args, **kwargs):
        if self.frequency > 5:
            self.frequency = 5
        super(Data, self).save(*args, **kwargs)
