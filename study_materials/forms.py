from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import Subscription, Notice, Category, Classification, Data


class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription  # form이 처리할 model
        fields = ['is_subscribed']  # form이 처리할 model의 필드


class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice  # form이 처리할 model
        fields = ['user', 'title', 'content', 'date']  # form이 처리할 model의 필드


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

    def clean_name(self):  # 필드의 유효성 검사
        name = self.cleaned_data['name']
        user = self.user
        if Category.objects.filter(name=name, user=user).exists():
            raise ValidationError("category already exists")
        return name


class ClassificationForm(forms.ModelForm):
    class Meta:
        model = Classification
        fields = ['category', 'name']


class DataForm(forms.ModelForm):
    class Meta:
        model = Data
        fields = ['classification', 'name', 'description', 'frequency']
