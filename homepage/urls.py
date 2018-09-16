from django.conf.urls import url


from . import views

app_name = 'homepage'
urlpatterns = [
    url(r'^$', views.hello, name='index'),
    url(r'aboutme/', views.aboutme, name='aboutme'),
]
