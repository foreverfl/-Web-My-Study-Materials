from django.contrib.sitemaps.views import sitemap
from .sitemaps import StudyMaterialsSitemap
from django.urls import path, include
from . import views
from .views import my_sitemap
from django.urls import re_path
from django.views.static import serve
from django.conf import settings
import os

sitemaps = {
    'study_materials': StudyMaterialsSitemap,
}

urlpatterns = [
    path('', views.index_view, name='index'),
    # allauth 라이브러리에서 제공하는 모든 url 패턴을 포함
    path('accounts/', include('allauth.urls')),

    # Notice
    path('notice/create_form/', views.notice_create_form,
         name='notice_create_form'),
    path('notice/create/', views.notice_create,
         name='notice_create'),
    path('notice/<int:notice_id>/', views.notice_detail,
         name='notice_detail'),
    path('notice/<int:notice_id>/update_form/', views.notice_update_form,
         name='notice_update_form'),
    path('notice/<int:notice_id>/update/', views.notice_update,
         name='notice_update'),
    path('notice/<int:notice_id>/delete/', views.notice_delete,
         name='notice_delete'),

    # Category
    path('category/create/', views.category_create, name='category_create'),
    path('category/<int:category_id>/',
         views.category_detail, name='category_detail'),
    path('category/update/',
         views.category_update, name='category_update'),
    path('category/<int:category_id>/delete/',
         views.category_delete, name='category_delete'),

    # Classification
    path('category/<int:category_id>/classification/create/>', views.classification_create,
         name='classification_create'),
    path('category/<int:category_id>/classifications/', views.classification_list,
         name='classification_list'),
    path('category/<int:category_id>/classification/<int:classification_id>/',
         views.classification_detail, name='classification_detail'),
    path('category/<int:category_id>/classification/update',
         views.classification_update, name='classification_update'),
    path('category/<int:category_id>/classification/<int:classification_id>/delete/',
         views.classification_delete, name='classification_delete'),

    # Data
    path('category/<int:category_id>/classification/<int:classification_id>/data/create_form/', views.data_create_form,
         name='data_create_form'),
    path('category/<int:category_id>/classification/<int:classification_id>/data/create/', views.data_create,
         name='data_create'),
    path('category/<int:category_id>/classification/<int:classification_id>/data/<int:data_id>/',
         views.data_detail, name='data_detail'),
    path('category/<int:category_id>/classification/<int:classification_id>/data/<int:data_id>/update_form/',
         views.data_update_form, name='data_update_form'),
    path('category/<int:category_id>/classification/<int:classification_id>/data/<int:data_id>/update/',
         views.data_update, name='data_update'),
    path('category/<int:category_id>/classification/<int:classification_id>/data/<int:data_id>/delete/',
         views.data_delete, name='data_delete'),

    # Search
    path('search/', views.search, name='search'),

    # payment
    path('payment/prohibition', views.payment_test, name='payment_prohibition'),
    path('payment/describe', views.payment_describe, name='payment_describe'),
    path('payment/', views.payment, name='payment'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/fail/', views.payment_fail, name='payment_fail'),

    # Sitemap
    path('sitemap.xml', my_sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),

    # robots.txt
    path('robots.txt', serve, {'path': 'robots.txt',
         'document_root': settings.STATICFILES_DIRS[0]}),

    # Adsense
    re_path(r'^ads\.txt$', serve, {
        'path': 'ads.txt',
        'document_root': os.path.join(settings.STATICFILES_DIRS[0]),
    }),

    # Naver
    path('naver3a7b0c9f306d7cf81119e203ee3be4bf.html', views.naver_verification),
]
