from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('index', views.index, name='index'),
    path('member', views.member, name='member'),
    path('member_single', views.member_single, name='member_single'),
    path('blog', views.blog, name='blog'),
    path('contact', views.contact, name='contact'),
    # path('searchpert_origin', views.searchpert_origin, name='searchpert_origin'),
    # path('searchpert_reverse', views.searchpert_reverse, name='searchpert_reverse'),
    path('searchpert_shuffle', views.searchpert_shuffle, name='searchpert_shuffle'),
    path('w2v', views.searchpert_shuffle, name='w2v'),
]