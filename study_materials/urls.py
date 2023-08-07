from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),  # update this line
    # allauth 라이브러리에서 제공하는 모든 url 패턴을 포함
    path('accounts/', include('allauth.urls')),
    path('layout/', views.layout_view, name='layout'),

    # Category
    path('category/<int:category_id>/',
         views.category_detail, name='category_detail'),
    path('categories/', views.category_list, name='category_list'),
    path('category/new/', views.category_new, name='category_new'),
    path('category/<int:category_id>/delete/',
         views.category_delete, name='category_delete'),

    # Classification
    path('classifications/', views.classification_list,
         name='classification_list'),
    path('classification/<int:classification_id>/',
         views.classification_detail, name='classification_detail'),
    path('classification/new/', views.classification_create,
         name='classification_new'),
    path('classification/<int:classification_id>/update/',
         views.classification_update, name='classification_update'),
    path('classification/<int:classification_id>/delete/',
         views.classification_delete, name='classification_delete'),

    # Data
]
