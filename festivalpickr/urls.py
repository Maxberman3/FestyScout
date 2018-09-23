from django.urls import path
from . import views

urlpatterns=[
path("",views.index,name='index'),
path("index.html",views.index,name='index'),
path("getspotify",views.getspotify,name='getspotify'),
path("landing/",views.landing,name='landing'),
path("refreshlanding",views.refreshlanding,name='refreshlanding'),
path("contactus",views.contactus,name='contactus'),
path("toemail",views.toemail,name='toemail'),
path("accounts/signup",views.signup,name='signup'),
]
