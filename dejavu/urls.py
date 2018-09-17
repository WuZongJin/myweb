from django.conf.urls import include, url
from . import views

app_name = 'dejavu'

urlpatterns = [
    url(r'^', views.index, name="index"),
    url(r'test/', views.test, name="test"),
]