import json, requests
from django.conf import settings

SONGKICK_KEY=settings.SONGKICK_KEY

def songkickcall(artist_iterable):
    artist_ids={}
    api_key=SONGKICK_KEY
    for artist in artist_iterable:
        request_url="https://api.songkick.com/api/3.0/search/artists.json?apikey={}&query={}".format(api_key,artist)
        songkickrequest=requests.get(request_url)
        artist_data=json.loads(songkickrequest.text)
        if artist_data["resultsPage"]["status"]=="ok" and artist_data["resultsPage"]["totalEntries"]>0:
            artist_ids[artist]=artist_data["resultsPage"]["results"]['artist'][0]['id']
    return artist_ids
