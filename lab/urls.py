from django.urls import path
from . import views

urlpatterns = [
    path('', views.w2v_2, name='index'),
    path('w2v', views.w2v_2, name='w2v'),
    path('w2v_1', views.w2v_1, name='w2v_1'),
    path('w2v_2', views.w2v_2, name='w2v_2'),
]