from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Subscription(models.Model):  # Subscription 모델 선언
    user = models.OneToOneField(
        User, on_delete=models.CASCADE)  # User 모델과 1:1 관계 정의
    is_subscribed = models.BooleanField(default=False)  # 유료 구독 여부를 나타내는 필드
    start_date = models.DateTimeField(null=True, blank=True)  # 구독 시작일
    end_date = models.DateTimeField(null=True, blank=True)  # 구독 종료일
    payment_status = models.CharField(
        max_length=50, default='pending')  # 결제 상태
    billing_key = models.CharField(
        max_length=200, null=True, blank=True)  # 빌링키

    def __str__(self):
        return self.user.username + " subscription status: " + str(self.is_subscribed)

    @receiver(post_save, sender=User)  # User 모델 인스턴스가 저장되면 post_save 신호를 받음
    # User 모델이 저장된 후 실행될 함수
    def create_user_subscription(sender, instance, created, **kwargs):

        if created:  # User 인스턴스가 생성되었을 때만 실행
            Subscription.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_subscription(sender, instance, **kwargs):  # User 모델이 저장될 때마다 실행될 함수
        instance.subscription.save()


class Notice(models.Model):  # Notice 테이블
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    date = models.DateTimeField()


class Category(models.Model):  # Category 테이블
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    is_public = models.BooleanField(default=True)


class CategorySubscription(models.Model):  # 구독 정보를 담을 새로운 모델
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='category_subscriptions')
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='subscribers')

    class Meta:
        unique_together = ('user', 'category')  # 유저와 카테고리의 조합은 유일해야 함


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
        if self.frequency > 10:
            self.frequency = 10
        super(Data, self).save(*args, **kwargs)
