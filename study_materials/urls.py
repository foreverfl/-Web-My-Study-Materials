from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),  # update this line
    # allauth 라이브러리에서 제공하는 모든 url 패턴을 포함
    path('accounts/', include('allauth.urls')),
    path('layout/', views.layout_view, name='layout'),

    # Category
    path('category/create/', views.category_create, name='category_create'),
    path('category/<int:category_id>/',
         views.category_detail, name='category_detail'),
    path('categories/', views.category_list, name='category_list'),
    path('category/<int:category_id>/delete/',
         views.category_delete, name='category_delete'),

    # Classification
    path('classification/create/<int:category_id>/>', views.classification_create,
         name='classification_create'),
    path('classifications/', views.classification_list,
         name='classification_list'),
    path('classification/<int:classification_id>/',
         views.classification_detail, name='classification_detail'),
    path('classification/<int:classification_id>/delete/',
         views.classification_delete, name='classification_delete'),

    # Data
    path('classification/<int:classification_id>/data/create_form/', views.data_create_form,
         name='data_create_form'),
    path('classification/<int:classification_id>/data/create/', views.data_create,
         name='data_create'),
    path('data/', views.data_list,
         name='data_list'),
    path('classification/<int:classification_id>/data/<int:data_id>/',
         views.data_detail, name='data_detail'),
    path('classification/<int:classification_id>/data/<int:data_id>/update_form/',
         views.data_update_form, name='data_update_form'),
    path('classification/<int:classification_id>/data/<int:data_id>/update/',
         views.data_update, name='data_update'),
    path('classification/<int:classification_id>/data/<int:data_id>/delete',
         views.data_delete, name='data_delete'),

    # Search
    path('search/', views.search, name='search'),
]
