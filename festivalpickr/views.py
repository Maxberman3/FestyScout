import requests
import json
import secrets

from django import forms
from decimal import Decimal
from django.shortcuts import render,reverse,redirect
from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.conf import settings
from django.http import HttpResponse
from urllib.parse import urlencode
from festivalpickr.utils import songkickcall,ourdbcall
from .forms import SignUpForm, PaymentForm
from .models import Profile, Festival
from festivalpickr.utils import songkickcall
from django_coinpayments.models import Payment
from django_coinpayments.exceptions import CoinPaymentsProviderError
from django.views.generic import FormView, ListView, DetailView
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.core.mail import send_mail

spot_client_id=settings.SPOT_CLIENT_ID
spot_secret_id=settings.SPOT_SECRET_ID
spot_uri=settings.SPOT_CALLBACK

def index(request):
    return render(request,'festivalpickr/index.html')

def about(request):
    return render(request, 'festivalpickr/about.html')

def contact(request):
    if request.method == 'POST':
        send_mail(
        request.POST['subject'],
        request.POST['message'],
        request.POST['email'],
        ['festivalpickr@gmail.com'],
        fail_silently=False,
        )
        return redirect('index')
    else:
        return render(request,'festivalpickr/contact.html')

def login(request):
    return render(request,'registration/login.html')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():

            user = form.save();
            user.refresh_from_db()
            user.profile.address = form.cleaned_data.get('address')
            user.profile.city = form.cleaned_data.get('city')
            user.profile.state = form.cleaned_data.get('state')
            user.profile.zip = form.cleaned_data.get('zip')
            user.profile.email = form.cleaned_data.get('email')
            user.save()

            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            django_login(request, user)

            if not user.profile.is_verified:
                send_mail(
                    'Verify your FestivalPickr account',
                    'Follow this link to verify your account: '
                        'http://127.0.0.1:8000%s' % reverse('verify', kwargs={'uuid': str(user.profile.verification_uuid)}),
                    'from@festivalpickr.dev',
                    [user.profile.email],
                    fail_silently=False,
                )

            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'festivalpickr/signup.html', {'form': form})

def verify(request, uuid):
    try:
        user = Profile.objects.get(verification_uuid=uuid, is_verified = False)
    except Profile.DoesNotExist:
        raise Http404("User doesn't exist or is already verified!")

    user.is_verified = True
    user.save()

    return redirect('index')

def getspotify(request):
    if request.method != 'POST':
        return render('festivalpicr/error.html',{'problem':'unable to handle due to bad request','message':'This url should only be accessed through a post request'})
    if "songkick" in request.POST:
        request.session['type']='songkick'
    elif "our_db" in request.POST:
        request.session['type']='our_db'
    else:
        return render('festivalpicr/error.html',{'problem':'unable to handle due to bad request','message':'post request contained incorrect information'})
    if "refresh_token" in request.session:
        return redirect(reverse('refreshlanding'))
    state=secrets.token_urlsafe(20)
    request.session['state_token']=state
    scope='user-library-read'
    payload={'client_id':spot_client_id,'response_type':'code','redirect_uri':spot_uri,'scope':scope,'state':state}
    url_args=urlencode(payload)
    auth_url = "{}/?{}".format('https://accounts.spotify.com/authorize', url_args)
    return redirect(auth_url)

def landing(request):
    if 'error' in request.GET:
        return render('festivalpickr/error.html',{'problem':'spotify authorization failed','message':'Either you failed to give permission to the app or there was a faulty connection'})
    if request.GET['state'] != request.session['state_token']:
        return render('festivalpickr/error.html',{'problem':'Are you trying to hack me?','message':'Get that weak shit outta here'})
    spotcode=request.GET['code']
    payload={
    'grant_type':'authorization_code',
    'code':str(spotcode),
    'redirect_uri':spot_uri,
    'client_id':spot_client_id,
    'client_secret':spot_secret_id
    }
    post_request=requests.post('https://accounts.spotify.com/api/token',data=payload)
    response_data = json.loads(post_request.text)
    access_token = response_data["access_token"]
    refresh_token = response_data["refresh_token"]
    request.session['refresh_token']=refresh_token
    authorization_header = {"Authorization":"Bearer {}".format(access_token)}
    lib_request_url='https://api.spotify.com/v1/me/tracks'
    lib_request=requests.get(lib_request_url,headers=authorization_header)
    lib_data=json.loads(lib_request.text)
    artist_set=set()
    if 'items' not in lib_data:
        print(lib_data)
        return render('festivalpickr/error.html',{'problem':'Some sort of issue with the returned spotify library','message':'Check the console to see what was returned'})
    while True:
        for item in lib_data['items']:
            track=item['track']
            artist_set.add(track['artists'][0]['name'])
        if lib_data['next'] is None:
            break
        else:
            lib_request_url=lib_data['next']
            lib_request=requests.get(lib_request_url,headers=authorization_header)
            lib_data=json.loads(lib_request.text)
    if request.session['type']=='our_db':
        festivals=ourdbcall(artist_set)
    elif request.session['type']=='songkick':
        festivals=songkickcall(artist_set)
    festivals_order=sorted(festivals,key=lambda k:festivals[k]['score'],reverse=True)
    sorted_dicts=[]
    for festival in festivals_order:
        sorted_dicts.append(festivals[festival])
    combo_list=zip(festivals_order,sorted_dicts)
    context={
    'festivals':combo_list,
    }
    return render(request,'festivalpickr/searchresults.html',context)

def refreshlanding(request):
    if 'refresh_token' not in request.session:
        return render('festivalpickr/error.html',{'problem':'you have not yet been authorized through spotify','message':'Im not even sure how you got here'})
    refresh_token=request.session['refresh_token']
    payload={'grant_type':'refresh_token','refresh_token':refresh_token,'client_id':spot_client_id,'client_secret':spot_secret_id}
    refresh_request=requests.post('https://accounts.spotify.com/api/token',data=payload)
    response_data = json.loads(refresh_request.text)
    access_token = response_data["access_token"]
    authorization_header = {"Authorization":"Bearer {}".format(access_token)}
    lib_request_url='https://api.spotify.com/v1/me/tracks'
    lib_request=requests.get(lib_request_url,headers=authorization_header)
    lib_data=json.loads(lib_request.text)
    artist_set=set()
    while True:
        for item in lib_data['items']:
            track=item['track']
            artist_set.add(track['artists'][0]['name'])
        if lib_data['next'] is None:
            break
        else:
            lib_request_url=lib_data['next']
            lib_request=requests.get(lib_request_url,headers=authorization_header)
            lib_data=json.loads(lib_request.text)
    if request.session['type']=='our_db':
        festivals=ourdbcall(artist_set)
    elif request.session['type']=='songkick':
        festivals=songkickcall(artist_set)
    festivals_order=sorted(festivals,key=lambda k:festivals[k]['score'],reverse=True)
    sorted_dicts=[]
    for festival in festivals_order:
        sorted_dicts.append(festivals[festival])
    combo_list=zip(festivals_order,sorted_dicts)
    context={
    'festivals':combo_list,
    }
    if 'past_searches' not in request.session:
        q=Queue()
        if len(combo_list)>=5:
            q.put(combo_list[0:5])
        else:
            q.put(combo_list)
        request.session['past_searches']=q
    elif len(request.session['past_searches'])<5:
        if len(combo_list)>=5:
            request.session['past_searches'].put(combo_list[0:5])
        else:
            request.session['past_searches'].put(combo_list)
    else:
        request.session['past_searches'].pop()
        if len(combo_list)>=5:
            request.session['past_searches'].put(combo_list[0:5])
        else:
            request.session['past_searches'].put(combo_list)
    return render(request,'festivalpickr/searchresults.html',context)

def create_tx(request, payment, email):
    context = {}
    try:
        tx = payment.create_tx(buyer_email = email)
        payment.status = Payment.PAYMENT_STATUS_PENDING
        payment.save()
        context['object'] = payment
    except CoinPaymentsProviderError as e:
        context['error'] = e
    return render(request, 'festivalpickr/result.html', context)

class PaymentDetail(DetailView):
    model = Payment
    template_name = 'festivalpickr/result.html'
    context_object_name = 'object'

class PaymentSetupView(FormView):
    template_name = 'festivalpickr/payment.html'
    form_class = PaymentForm
    festival_dict = {}

    def dispatch(self, request, *args, **kwargs):
        try:
            self.festival_dict['festival'] = self.request.POST['festivalname']
            if self.request.session['festival_purchases']:
                list.append(self.request.session['festival_purchases'], self.request.POST['festivalname'])
            else:
                self.request.session['festival_purchases'] = [self.request.POST['festivalname']]
            return super(PaymentSetupView, self).dispatch(request, *args, **kwargs)
        except:
            return super(PaymentSetupView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        cl = form.cleaned_data
        festival = self.festival_dict['festival']
        price = Festival.objects.get(name=festival).price
        payment = Payment(currency_original='USD',
                          currency_paid=cl['currency_paid'],
                          amount=Decimal(price),
                          amount_paid=Decimal(0),
                          status=Payment.PAYMENT_STATUS_PROVIDER_PENDING)

        email = form.cleaned_data.get('email')
        return create_tx(self.request, payment, email)

def create_new_payment(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    if payment.status in [Payment.PAYMENT_STATUS_PROVIDER_PENDING, Payment.PAYMENT_STATUS_TIMEOUT]:
        pass
    elif payment.status in [Payment.PAYMENT_STATUS_PENDING]:
        payment.provider_tx.delete()
    else:
        error = "Invalid status - {}".format(payment.get_status_display())
        return render(request, 'festivalpickrs/result.html', {'error': error})
    return create_tx(request, payment)
