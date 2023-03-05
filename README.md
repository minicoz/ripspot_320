# ripspot
Spotify ripper

## NEW Update and reason why I forked it.
This works now. I got it to work on Nov 2022. Instructions are basically the same. 
I changed it so that the temp folder is not removed (downloaded as .oggs) and now ffmpeg converts the ogg files into `320kbps CBR` `mp3` files.
Output folder is output.

## March 2023 update
Now you can download ALL albums from one artist at a time. If you add the link to the artist page it will organize the output converted files by artist/album/track in the output folder.


# Prerequisites

- Python

# Libs

Install from `requiremets.txt` in a virtual env if you want. 
`pip install -r requiremetns` 

- librespot-python - `pip install git+https://github.com/kokarare1212/librespot-python`
- spotipy - `pip install spotipy`
- mutagen - `pip install mutagen`

# How to run

Make a copy of the `.env_example` file and rename it to `.env`. Update this file with your spotify username and password. This will be read in.

`python ripspot.py [links]`

## example:

to download album
- `python ripspot.py https://open.spotify.com/album/39gNIUdLlihrdSDu1BpzEX`

to download song
- `python ripspot.py --username "username" --password "password" https://open.spotify.com/track/62VJE7RsgsmjjmI2eHH4lx`

to download artist
- `python ripspot.py https://open.spotify.com/artist/2JfU9lZol5arnvYR11noIb`

to download song album and playlist
- `python ripspot.py --username "username" --password "password" https://open.spotify.com/track/62VJE7RsgsmjjmI2eHH4lx https://open.spotify.com/playlist/5tFLvXM5ieVn8wzCaLTuzt https://open.spotify.com/album/2SYoVgjmUEYmzwP42lROTx`


# Removing duplicates
when downloading using artist you might end up downloading a lot of compilations where the artist may have one song on it but there are another 50 artists in the compilation / playlist

To solve this I used the following bash command:

`find . -type f ! -name "*Daft Punk*" -delete`

The `!` character evaluates to filter out all the files that have `Daft Punk` in them to only remove the extra artsts ones. 
I have added a check to split the artists name into tokens and if non of the tokens are present anywhere in the song name title then it will skip it. This may cause issues for DJ mixes but hey, im trying to download discographies, not other peoples work.