from django.urls import path
from . import views

urlpatterns=[
path("index.html",views.index,name='index'),
path("getspotify",views.getspotify,name='getspotify'),
path("landing/",views.landing,name='landing'),
path("refreshlanding",views.refreshlanding,name='refreshlanding'),
path("whatisthis.html",views.whatisthis,name='whatisthis'),
path("contactus.html",views.contactus,name='contactus'),
path("toemail",views.toemail,name='toemail'),
]
