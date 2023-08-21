from django import forms
from django.contrib.auth.models import User
from .models import Notice, Category, Classification, Data


class NoticeForm(forms.ModelForm):  # Django의 ModelForm 클래스를 상속받는 CategoryForm 클래스를 선언
    class Meta:  # form과 관련된 옵션들을 설정
        model = Notice  # form이 처리할 model
        # form이 처리할 model의 필드를 리스트 형태로 지정
        fields = ['user', 'title', 'content', 'date']


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']


class ClassificationForm(forms.ModelForm):
    class Meta:
        model = Classification
        fields = ['category', 'name']


class DataForm(forms.ModelForm):
    class Meta:
        model = Data
        fields = ['classification', 'name', 'description', 'frequency']
