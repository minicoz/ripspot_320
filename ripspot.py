import sys
import argparse
import os
import pathlib
import subprocess

from librespot.core import Session
from dotenv import load_dotenv

load_dotenv()

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from utils import _download_song, make_folders
from process import (
    get_tracks,
    get_albums,
    get_artist,
    get_playlist
)

try:
    subprocess.Popen(
        ["ffmpeg", "-version"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
    )
except FileNotFoundError:
    print("install ffmpeg", file=sys.stderr)
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Simple spotify ripper, that converts downloaded songs to mp3 and tags them with spotify metadata",
        prog="ripspot",
    )
    parser.add_argument("url", type=str, nargs="+", help="URL to a song/album/playlist")
    parser.add_argument("-u", "--username", help="Your spotify username", default=os.getenv('USERNAME')) 
    parser.add_argument("-p", "--password", help="Your spotify password", default=os.getenv('PASSWORD'))
    parser.add_argument(
        "-q",
        "--quality",
        help="Select your prefered quality",
        choices={"normal", "high", "veryhigh"},
        default="veryhigh",
    )

    arguments = parser.parse_args()

    spotify = spotipy.Spotify(
        client_credentials_manager=SpotifyClientCredentials(
            client_id="efda7d91569a4df89c9862a54b04d6c5",
            client_secret="e53ec07ea6224e48a8b32813cb55c08c",
        )
    )

    session = (
        Session.Builder()
        .user_pass(username=arguments.username, password=arguments.password)
        .create()
    )
    make_folders()

    tracks = []
    for request in arguments.url:
        if "open.spotify.com" in request and "track" in request:
            ret = get_tracks(spotify, request)
        elif "open.spotify.com" in request and "artist" in request:
            ret = get_artist(spotify, request, session, arguments.quality)
            return
        elif "open.spotify.com" in request and "playlist" in request:
            ret = get_playlist(spotify, request)
        elif "open.spotify.com" in request and "album" in request:
            tracks = get_albums(spotify, request)

        tracks.extend(ret)       

    total_tracks_num = len(tracks)
    print(f"Found {total_tracks_num} tracks to download. Downloading each one now")

    for i, track in enumerate(tracks):
        print(f"Downloading file {i} out of {total_tracks_num}.")
        _download_song(session, track, arguments.quality)


main()