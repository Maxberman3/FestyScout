import json, repquests
from django.conf import settings

SONGKICK_KEY=settings.SONGKICK_KEY

def songkickcall(artist_iterable):
    artist_ids={}
    for artist in artist_iterable:
        payload={
        "apikey":SONGKICK_KEY,
        "query":artist,
        }
        songkickrequest=requests.get("https://api.songkick.com/api/3.0/search/artists.json",data=payload)
        artist_data=json.loads(songkickrequest.text)
        artist_ids[artist]=artist_data["artist"]["id"]
    return artist_ids
