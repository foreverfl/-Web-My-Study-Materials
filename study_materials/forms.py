from django import forms
from .models import Users, Category, Classification, Data


class CategoryForm(forms.ModelForm):  # Django의 ModelForm 클래스를 상속받는 CategoryForm 클래스를 선언
    class Meta:  # form과 관련된 옵션들을 설정
        model = Category  # form이 처리할 model
        fields = ['name']  # form이 처리할 model의 필드를 리스트 형태로 지정


class ClassificationForm(forms.ModelForm):
    class Meta:
        model = Classification
        fields = ['category', 'name']


class DataForm(forms.ModelForm):
    class Meta:
        model = Data
        fields = ['classification', 'name', 'concept',
                  'features', 'command', 'frequency', 'code', 'others']
