from django.shortcuts import render,reverse,redirect
from django.conf import settings
import requests
import json
import base64
from urllib.parse import urlencode

spot_client_id=settings.SPOT_CLIENT_ID
spot_secret_id=settings.SPOT_SECRET_ID
spot_uri=settings.SPOT_CALLBACK
# Create your views here.
def index(request):
    return render(request,'festivalpickr/index.html')
def getspotify(request):
    if "refresh_token" in request.session:
        return redirect(reverse('refreshlanding'))
    scope='user-library-read'
    payload={'client_id':spot_client_id,'response_type':'code','redirect_uri':spot_uri,'scope':scope}
    url_args=urlencode(payload)
    auth_url = "{}/?{}".format('https://accounts.spotify.com/authorize', url_args)
    return redirect(auth_url)
def landing(request):
    if 'error' in request.GET:
        return render('festivalpickr/error.html',{'problem':'spotify authorization failed','message':'Either you failed to give permission to the app or there was a faulty connection'})
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
