from django.db import models


class Users(models.Model):  # Users 테이블
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)


class Category(models.Model):  # Category 테이블
    name = models.CharField(max_length=255)


class Classification(models.Model):  # Classification 테이블
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)


class Data(models.Model):  # Data 테이블
    classification = models.ForeignKey(
        Classification, on_delete=models.CASCADE)
    name = models.TextField()
    concept = models.TextField()
    features = models.TextField()
    command = models.TextField()
    frequency = models.IntegerField()
    code = models.TextField()
    others = models.TextField()

    def save(self, *args, **kwargs):
        if self.frequency > 5:
            self.frequency = 5

        super(Data, self).save(*args, **kwargs)
