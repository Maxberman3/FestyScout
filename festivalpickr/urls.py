from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns=[
<<<<<<< HEAD
path("",views.index,name='index'),
path("index",views.index,name='index'),
path("about",views.about,name='about'),
path("getspotify",views.getspotify,name='getspotify'),
path("landing/",views.landing,name='landing'),
path("refreshlanding",views.refreshlanding,name='refreshlanding'),
path("contact",views.contact,name='contact'),
path("toemail",views.toemail,name='toemail'),
path("accounts/signup",views.signup,name='signup'),
path("searchresults",views.searchresults,name='searchresults')
=======
    path("",views.index,name='index'),
    path("index",views.index,name='index'),
    path("about",views.about,name='about'),
    path("getspotify",views.getspotify,name='getspotify'),
    path("landing/",views.landing,name='landing'),
    path("refreshlanding",views.refreshlanding,name='refreshlanding'),
    path("contact",views.contact,name='contact'),
    path("toemail",views.toemail,name='toemail'),
    path("signup",views.signup,name='signup'),
    path("login",views.login,name='login'),
    path('', include('django.contrib.auth.urls')),
>>>>>>> 39d494a2624c56e298a6e2f428223abef49ddb15
]
