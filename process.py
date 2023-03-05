from utils import _download_song, make_artist_folders

def get_tracks(spotify, request):
    return [spotify.track(request)]

def get_artist(spotify, request, session, quality):
    print("Downloading Artist info")
    artist = spotify.artist(request)
    artist_name = artist.get('name')
    make_artist_folders(artist_name)

    albums_page = spotify.artist_albums(artist.get('id'))
    print("Getting artist albums", artist_name)

    while True:
        items = albums_page.get('items')
        for album in items:
            uri = album.get('uri')
            album_name = album.get('name')
            dir_album_name = album_name + f" ({album.get('release_date')})"
            tracks = get_albums(spotify, uri)
            total_tracks_num = len(tracks)
            for i, track in enumerate(tracks):
                print(f"Downloading file {i} out of {total_tracks_num}.")
                _download_song(session, track, quality, artist_name, dir_album_name)
        next_page = albums_page.get('next')
        if next_page is None:
            break
        albums_page = spotify._get(next_page)
    return

def get_playlist(spotify, request):
    tracks = []
    playlist = spotify.playlist(request)
    while playlist:
        playlist_tracks = playlist.get("tracks")

        if playlist_tracks is not None:
            playlist_tracks = playlist_tracks.get("items")

            if len(playlist_tracks) > 0:
                tracks.extend(
                    [
                        track["track"]
                        for track in playlist_tracks
                        if "track" in track
                    ]
                )
            if playlist["tracks"]["next"]:
                playlist = spotify.next(playlist["tracks"])
            else:
                playlist = None
        else:
            playlist = None 
    return tracks

def get_albums(spotify, request):
    tracks = []
    album = spotify.album(request)
    print("Getting album tracks for album", album.get("name"))
    while album:
        album_tracks = album.get("tracks")
        if album_tracks is not None:
            album_tracks = album_tracks.get("items")
            if len(album_tracks) > 0:
                for track in album_tracks:
                    track.update(
                        {
                            "album": {
                                "images": album["images"],
                                "release_date": album["release_date"],
                                "name": album["name"],
                            }
                        }
                    )
                tracks.extend(album_tracks)
            if album["tracks"]["next"]:
                album = spotify.next(album["tracks"])
            else:
                album = None
        else:
            album = None
    return tracks