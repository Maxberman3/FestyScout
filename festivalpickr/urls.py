from django.urls import path, include
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views

urlpatterns=[

    path("",views.index,name='index'),

    path("index",views.index,name='index'),
    path("about",views.about,name='about'),
    path("contact",views.contact,name='contact'),
    path("signup",views.signup,name='signup'),
    path("login",views.login,name='login'),

    path("getspotify",views.getspotify,name='getspotify'),
    path("landing/",views.landing,name='landing'),
    path("refreshlanding",views.refreshlanding,name='refreshlanding'),

    path('', include('django.contrib.auth.urls')),
    path('', include('django_coinpayments.urls', namespace='django_coinpayments')),

    url(r'^payment/$', views.PaymentSetupView.as_view(), name='payment'),
    url(r'^payment/(?P<pk>[0-9a-f-]+)$', views.PaymentDetail.as_view(), name='payment_detail'),
    url(r'^payment/new/(?P<pk>[0-9a-f-]+)$', views.create_new_payment, name='payment_new'),

    url(r'^verify/(?P<uuid>[a-z0-9\-]+)/', views.verify, name='verify'),

]
