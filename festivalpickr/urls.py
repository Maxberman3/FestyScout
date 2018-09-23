from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns=[
path("",views.index,name='index'),
path("index",views.index,name='index'),
path("about",views.about,name='about'),
path("getspotify",views.getspotify,name='getspotify'),
path("landing/",views.landing,name='landing'),
path("refreshlanding",views.refreshlanding,name='refreshlanding'),
path("contact",views.contact,name='contact'),
path("toemail",views.toemail,name='toemail'),
path("signup",views.signup,name='signup'),
path('accounts/', include('django.contrib.auth.urls')),
]
