from django.shortcuts import render,reverse,redirect
from django.contrib.auth import login,authenticate
#from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
import requests
import json
import secrets
from urllib.parse import urlencode
from django.core.mail import send_mail
from .forms import SignUpForm

spot_client_id=settings.SPOT_CLIENT_ID
spot_secret_id=settings.SPOT_SECRET_ID
spot_uri=settings.SPOT_CALLBACK
# Create your views here.
def index(request):
    return render(request,'festivalpickr/index.html')
def whatisthis(request):
    return render(request,'festivalpickr/whatisthis.html')
def contactus(request):
    return render(request,'festivalpickr/contact.html')
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'festivalpickr/signup.html', {'form': form})
def toemail(request):
    if request.method != 'POST':
        return render('festivalpicr/error.html',{'problem':'unable to handle the message due to bad request','message':'This url should only be accessed through a post request'})
    name=request.POST['name']
    theirmail=request.POST['email']
    contents=request.POST['message']
    send_mail(
    name,
    contents,
    theirmail,
    ['festivalpickr@gmail.com'],
    fail_silently=False,
    )
    return redirect('index')

def getspotify(request):
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
    context={
    'artists':artist_set
    }
    return render(request,'festivalpickr/festivals.html',context)
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
    context={
    'artists':artist_set
    }
    return render(request,'festivalpickr/festivals.html',context)
