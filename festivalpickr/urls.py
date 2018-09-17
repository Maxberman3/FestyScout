from django.urls import path
from . import views

urlpatterns=[
path("",views.index,name='index'),
path("getspotify",views.getspotify,name='getspotify'),
path("landing/",views.landing,name='landing'),
]
