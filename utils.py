import sys
import argparse
import os
from os.path import exists
import pathlib
import subprocess
import asyncio

from urllib.request import urlopen
from asyncio.subprocess import create_subprocess_exec

from typing import List

from librespot.audio.decoders import AudioQuality, VorbisOnlyAudioQuality
from librespot.core import Session
from librespot.metadata import TrackId

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from mutagen.easyid3 import EasyID3, ID3
from mutagen.id3 import APIC as AlbumCover, USLT

AUDIO_QUALITY = {
    "normal": AudioQuality.NORMAL,
    "high": AudioQuality.HIGH,
    "veryhigh": AudioQuality.VERY_HIGH,
}

def make_folders(path=None):
    riptemp = f'riptemp/"{path}"' if path else "riptemp"
    output = f'output/"{path}"' if path else "output"

    temp_folder = pathlib.Path(".", riptemp)
    converted_folder = pathlib.Path(".", output)
    if not temp_folder.exists():
        temp_folder.mkdir()

    if not converted_folder.exists():
        converted_folder.mkdir()

def make_artist_folders(artist):
    temp_folder = pathlib.Path(f"./riptemp/", artist)
    converted_folder = pathlib.Path(f"./output", artist)
    if not temp_folder.exists():
        temp_folder.mkdir()

    if not converted_folder.exists():
        converted_folder.mkdir()


def make_album_folder(artist, album):
    temp_folder = pathlib.Path(f"./riptemp/{artist}", album)
    converted_folder = pathlib.Path(f"./output/{artist}", album)
    if not temp_folder.exists():
        temp_folder.mkdir()

    if not converted_folder.exists():
        converted_folder.mkdir()


def is_song_from_artist(song_name, artist_name):
    # Only download songs that are from the artist
    artist_tokens = artist_name.lower().split()
    for token in artist_tokens:
        if token in song_name.lower():
            return True
    return False

def _create_display_name(song_name, song_artists):
    artists_names = [artist["name"] for artist in song_artists if "name" in artist]
    artist_string = ", ".join(artists_names)
    return f"{artist_string} - {song_name}"


def _get_song_bytes(session, id, quality):

    track_id = TrackId.from_base62(id)

    stream = session.content_feeder().load(
        track_id,
        VorbisOnlyAudioQuality(AUDIO_QUALITY[quality]),
        False,
        None,
    )

    data = []

    while True:
        byte = stream.input_stream.stream().read()
        if byte == -1 or not byte:
            break
        data.append(byte)
    return data


def _set_id3_data(converted_file, resp):
    audioFile = EasyID3(converted_file)

    audioFile.delete()

    audioFile["title"] = resp["name"]

    audioFile["titlesort"] = resp["name"]

    audioFile["tracknumber"] = str(resp["track_number"])

    audioFile["discnumber"] = str(resp["disc_number"])

    audioFile["artist"] = resp["artists"][0]["name"]

    audioFile["album"] = resp["album"]["name"]

    audioFile["albumartist"] = [
        artist["name"] for artist in resp["artists"] if "name" in artist
    ]

    audioFile["date"] = resp["album"]["release_date"]

    audioFile["originaldate"] = resp["album"]["release_date"]

    audioFile.save(v2_version=3)

    audioFile = ID3(converted_file)
    rawAlbumArt = urlopen(resp["album"]["images"][0]["url"]).read()
    audioFile["APIC"] = AlbumCover(
        encoding=3, mime="image/jpeg", type=3, desc="Cover", data=rawAlbumArt
    )

    audioFile.save(v2_version=3)


async def _convert_to_mp3(input_path, output_path, response):
    process = await create_subprocess_exec(
        "ffmpeg",
        "-v",
        "quiet",
        "-n",
        "-i",
        input_path.absolute(),
        "-acodec",
        "libmp3lame",
        "-b:a",
        "320k",
        output_path.absolute(),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    
    proc_out, proc_err = await process.communicate()
    output = "\n".join([proc_out.decode("utf-8"), proc_err.decode("utf-8")])
    if process.returncode != 0:
       print("=== FFMPEG ERROR ===")
       print(output, file=sys.stderr)
    else:
       print(f"Tagging {_create_display_name(response['name'], response['artists'])}")
    _set_id3_data(output_path, response)


def _download_song(session, response, quality, artist_name=None, album_name=None):
    try:
        display_name = _create_display_name(response["name"], response["artists"])

        if not is_song_from_artist(display_name, artist_name): return
        
        safe_name = "".join(i for i in display_name if i not in "/?\\*|<>")

        if album_name: make_album_folder(artist_name, album_name)

        temp_file_path = pathlib.Path(".", "riptemp", artist_name, album_name, f"{safe_name}.ogg")
        converted_file_path = pathlib.Path(".", "output", artist_name, album_name, f"{safe_name}.mp3")
        skip_download = False
        if exists(temp_file_path):
            skip_download = True
        if exists(converted_file_path):
            return
        if not skip_download:
            print(f"Downloading {display_name}")
            song_bytes = _get_song_bytes(session, response["id"], quality)
            song_bytes = b''.join(song_bytes)


            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(bytes(song_bytes))

        asyncio.run(_convert_to_mp3(temp_file_path, converted_file_path, response))
    except Exception as e:
        print(e)
