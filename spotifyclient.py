import json
import requests
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth
from track import Track
from playlist import Playlist
from category import Category
import random


class SpotifyClient:
    def __init__(self, client_id, user_id, client_secret, redirect_uri):

        self.user_id = user_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.spotipyObject = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                scope="user-library-read app-remote-control user-read-playback-state user-read-currently-playing user-modify-playback-state user-read-recently-played playlist-modify-public streaming",
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
            )
        )

    def get_recent_tracks(self, limit=10):

        res = self.spotipyObject.current_user_recently_played(limit=limit)
        print(res)
        tracks = [
            Track(
                track["track"]["name"],
                track["track"]["uri"],
                track["track"]["artists"][0]["name"],
            )
            for track in res["items"]
        ]
        return tracks

    def get_recommendations(self, seed_tracks, limit):

        seed_tracks_uri = []
        for seed_track in seed_tracks:
            seed_tracks_uri.append(seed_track.uri)

        response = self.spotipyObject.recommendations(
            seed_tracks=seed_tracks_uri, limit=limit
        )
        tracks = [
            Track(track["name"], track["uri"], track["artists"][0]["name"])
            for track in response["tracks"]
        ]
        return tracks

    def create_playlist(self, name):

        res = self.spotipyObject.user_playlist_create(user="apjohnson12", name=name)
        new_playlist_uri = res["uri"]
        new_playlist_id = res["id"]

        playlist = Playlist(name, new_playlist_uri, new_playlist_id)
        return playlist

    def fill_playlist(self, tracks, playlist):
        tracks_uri = []
        for track in tracks:
            tracks_uri.append(track.uri)
        prePlaylist = self.spotipyObject.user_playlists(user="apjohnson12")

        self.spotipyObject.user_playlist_add_tracks(
            user="apjohnson12", playlist_id=playlist.id, tracks=tracks_uri
        )

        self.spotipyObject.start_playback(context_uri=playlist.uri)

    def get_categories(self):

        results = self.spotipyObject.categories(limit="20", offset="0")

        categories = results["categories"]["items"]

        while results["categories"]["next"]:
            results = self.spotipyObject.next(results["categories"])
            categories.extend(results["categories"]["items"])

        categories = [
            Category(category["name"], category["id"]) for category in categories
        ]

        return categories

    def get_category_playlists(self, category_id):

        results = self.spotipyObject.category_playlists(
            category_id, limit="5", offset=str(random.randint(1, 4))
        )["playlists"]["items"]

        return results

    def grab_playlist_songs(self, playlist_id):

        results = self.spotipyObject.playlist(playlist_id)

        all_tracks = []
        for mega_track in results["tracks"]["items"]:
            try:
                all_tracks.append(
                    Track(
                        mega_track["track"]["name"],
                        mega_track["track"]["uri"],
                        mega_track["track"]["artists"][0]["name"],
                    )
                )
            except Exception as e:
                print(e)
        seed_track = all_tracks[random.randint(0, len(all_tracks) - 1)]

        return seed_track

    def get_current_playback(self):

        result = self.spotipyObject.current_playback()

        track = Track(
            result["item"]["name"],
            result["item"]["uri"],
            result["item"]["artists"][0]["name"],
        )

        return track

    def add_songs_to_queue(self, track_list):
        for track in track_list:
            self.spotipyObject.add_to_queue(track.uri)

    def previous_song(self):
        self.spotipyObject.previous_track()

    def next_song(self):
        self.spotipyObject.next_track()

    def play_pause_song(self):
        playback = self.spotipyObject.current_playback()

        if playback["is_playing"] == True:
            self.spotipyObject.pause_playback()
        else:
            self.spotipyObject.start_playback()
