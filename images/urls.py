from django.conf.urls import url
from . import views

app_name = 'images' # this is for namespacing
urlpatterns = [
    # /images
    url(r'^$', views.index, name='index'),
    # /images/create
    url(r'^create$', views.create, name='create'), # create POST happens here
    # /images/5
    url(r'^(?P<image_id>[0-9]+)/$', views.detail, name='detail'),
    # /images/5/edit
    url(r'^(?P<image_id>[0-9]+)/edit/$', views.edit, name='edit'),
    # /images/cheese
    url(r'^(?P<tagged>[0-9a-z]+)/$', views.tagged, name='tagged'), 
]
