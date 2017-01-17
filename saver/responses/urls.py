from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<client_id>[0-9]+)/responses/$' , views.client_responses, name='client_responses'),
]
