import json, requests
from django.conf import settings
from django import forms
from .models import Band

SONGKICK_KEY=settings.SONGKICK_KEY
def ourdbcall(artist_iterable):
    festivals={}
    for artist in artist_iterable:
        if Band.objects.filter(name__iexact=artist).exists():
            festival_tour=Band.objects.get(name=artist).festivals
            for festival in festival_tour.all():
                if festival.name not in festivals:
                    festivals[festival.name]={'score':1,'bands':[artist]}
                else:
                    festivals[festival.name]['score']+=1
                    festivals[festival.name]['bands'].append(artist)
    return festivals;

def has_name_chars(form_data):
    for character in form_data:
        if character in "!@#$%^&*()~,./?;:1234567890}{<>-+=":
            #print('{field} contains {character}')
            raise forms.ValidationError('You included a number or special character in a name or city field')
def songkickcall(artist_iterable):
    festivals={}
    api_key=SONGKICK_KEY
    for artist in artist_iterable:
        artist_in_db=False
        if Band.objects.filter(name__iexact=artist).exists():
            artist_id=Band.objects.get(name=artist).songkickid
            if (artist_id is not None) and (artist_id != ''):
                artist_in_db=True
            else:
                request_url="https://api.songkick.com/api/3.0/search/artists.json?apikey={}&query={}".format(api_key,artist)
                songkickrequest=requests.get(request_url)
                artist_data=json.loads(songkickrequest.text)
                if artist_data["resultsPage"]["status"]=="ok" and artist_data["resultsPage"]["totalEntries"]>0:
                    artist_id=artist_data["resultsPage"]["results"]['artist'][0]['id']
                    band_edit=Band.objects.get(name__iexact=artist)
                    band_edit.save()
                    artist_in_db=True
        if not artist_in_db:
            request_url="https://api.songkick.com/api/3.0/search/artists.json?apikey={}&query={}".format(api_key,artist)
            songkickrequest=requests.get(request_url)
            artist_data=json.loads(songkickrequest.text)
            if artist_data["resultsPage"]["status"]=="ok" and artist_data["resultsPage"]["totalEntries"]>0:
                artist_id=artist_data["resultsPage"]["results"]['artist'][0]['id']
                new_band_entry=Band(name=artist,songkickid=artist_id)
                new_band_entry.save()
                artist_in_db=True
        if artist_in_db:
            request_url="https://api.songkick.com/api/3.0/artists/{}/calendar.json?apikey={}&page=1".format(artist_id,api_key)
            songkickrequest=requests.get(request_url)
            tour_data=json.loads(songkickrequest.text)
            if tour_data["resultsPage"]["status"]=="ok" and tour_data["resultsPage"]["totalEntries"]>0:
                #print(tour_data)
                if tour_data["resultsPage"]["totalEntries"]<50:
                    for event in tour_data["resultsPage"]["results"]["event"]:
                        #print(event)
                        if event["type"] == "Festival":
                            festivalname=event["displayName"]
                            if festivalname not in festivals:
                                festivals[festivalname]={"score":1,"bands":[artist]}
                            else:
                                if artist not in festivals[festivalname]["bands"]:
                                    festivals[festivalname]["score"]+=1
                                    festivals[festivalname]["bands"].append(artist)
                else:
                    page=2;
                    while(tour_data["resultsPage"]["status"]=="ok" and tour_data["resultsPage"]["results"]):
                        #print(tour_data)
                        for event in tour_data["resultsPage"]["results"]["event"]:
                            if event["type"] == "Festival":
                                festivalname=event["displayName"]
                                if festivalname not in festivals:
                                    festivals[festivalname]={"score":1,"bands":[artist]}
                                else:
                                    if artist not in festivals[festivalname]["bands"]:
                                        festivals[festivalname]["score"]+=1
                                        festivals[festivalname]["bands"].append(artist)
                        request_url="https://api.songkick.com/api/3.0/artists/{}/calendar.json?apikey={}&page={}".format(artist_id,api_key,page)
                        songkickrequest=requests.get(request_url)
                        tour_data=json.loads(songkickrequest.text)
                        page+=1
    return festivals
