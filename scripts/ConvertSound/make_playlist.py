from glob import glob
from pydub import AudioSegment

playlist_songs = [AudioSegment.from_wav(file) for file in glob("input/*.wav")]

first_song = playlist_songs.pop(0)

beginning_of_song = first_song
playlist = beginning_of_song
for song in playlist_songs:
    playlist = playlist.append(song, crossfade=(5 * 1000))

playlist = playlist.fade_out(20)
with open("output/playlist.wav", 'wb') as out_f:
    playlist.export(out_f, format='wav')
