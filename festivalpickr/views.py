from django.shortcuts import render,reverse,redirect
from django.conf import settings
import requests
import json
from urllib.parse import urlencode

spot_client_id=settings.SPOT_CLIENT_ID
spot_secret_id=settings.SPOT_SECRET_ID
spot_uri=settings.SPOT_CALLBACK
# Create your views here.
def index(request):
    return render(request,'festivalpickr/index.html')
def getspotify(request):
    scope='user-library-read'
    payload={'client_id':spot_client_id,'response_type':'code','redirect_uri':spot_uri,'scope':scope}
    url_args=urlencode(payload)
    auth_url = "{}/?{}".format('https://accounts.spotify.com/authorize', url_args)
    return redirect(auth_url)
def landing(request):
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
    token_type = response_data["token_type"]
    expires_in = response_data["expires_in"]
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
