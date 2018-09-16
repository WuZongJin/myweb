from django.conf.urls import include, url
from . import views

app_name = 'store'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^products/$', views.products, name='products'),
    url(r'^tags/$', views.tags, name='tags'),
    url(r'^detail/$', views.detail, name='detail'),
    url(r'^register/$', views.do_reg, name='register'),
    url(r'^login/$', views.do_login, name='login'),
    url(r'^logout/$', views.do_logout, name='logout'),
    url(r'^view_cart/$', views.view_cart, name='view_cart'),
    url(r'^add_cart/$', views.add_cart, name='add_cart'),
    url(r'^clean_cart/$', views.cleanCart, name='clean_cart'),
    url(r'^brands/$', views.brands, name='brands'),
    url(r'discount/$', views.getDiscount, name='discount')
]
