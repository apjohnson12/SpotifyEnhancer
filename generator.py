import json
import requests
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth
from track import Track
from playlist import Playlist
import os
from spotifyclient import SpotifyClient
import yaml
import qdarktheme
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtCore
import time
import webbrowser


class ui_main(QMainWindow):
    def __init__(self, recent_tracks, categories):
        super().__init__()

        self.top_level_screen()

        self.recent_tracks = recent_tracks
        self.categories = categories
        self.setWindowTitle("SWE 6623 Project")

    def top_level_screen(self):

        with open("login.yaml", "r") as f:
            loginInfo = yaml.safe_load(f)
        self.sp_client = SpotifyClient(
            loginInfo["client_id"],
            loginInfo["username"],
            loginInfo["client_secret"],
            loginInfo["redirect_uri"],
        )

        self.resize(400, 200)
        self.main_wid = QWidget()
        self.setCentralWidget(self.main_wid)
        self.main_vbox = QVBoxLayout()
        self.main_wid.setLayout(self.main_vbox)

        self.welcome_label = QLabel("## Spotify Enhancer Application")
        self.welcome_label.setTextFormat(QtCore.Qt.MarkdownText)
        self.welcome_label.setStyleSheet("color: green;" "font: bold 20px;")

        self.welcome_label.setAlignment(QtCore.Qt.AlignCenter)
        self.create_playlist_btn = QPushButton("Create Recommended Playlist")
        self.get_categories_btn = QPushButton("Get Categories")
        self.playback_btn = QPushButton("Playback")
        self.launch_btn = QPushButton("Launch Spotify")

        self.main_vbox.addStretch()
        self.main_vbox.addWidget(self.welcome_label)
        self.main_vbox.addStretch()
        self.main_vbox.addWidget(self.launch_btn)
        self.main_vbox.addWidget(self.create_playlist_btn)
        self.main_vbox.addWidget(self.get_categories_btn)
        self.main_vbox.addWidget(self.playback_btn)

        self.launch_btn.clicked.connect(lambda: self.launch_btn_click())
        self.create_playlist_btn.clicked.connect(
            lambda: self.create_playlist_btn_click()
        )
        self.get_categories_btn.clicked.connect(
            lambda: self.get_categories_btn_clicked(categories=self.categories)
        )
        self.playback_btn.clicked.connect(lambda: self.playlist_btn_click())

    def launch_btn_click(self):
        webbrowser.open("https://spotify.com")

    def playlist_btn_click(self):
        self.playback_screen()

    def playback_screen(self):
        self.resize(400, 200)
        self.main_wid = QWidget()
        self.setCentralWidget(self.main_wid)

        self.main_vbox = QVBoxLayout()
        self.main_wid.setLayout(self.main_vbox)

        self.top_wid = QWidget(self)
        self.bottom_wid = QWidget(self)

        self.top_hbox = QHBoxLayout()
        self.bottom_hbox = QHBoxLayout()

        self.top_wid.setLayout(self.top_hbox)
        self.bottom_wid.setLayout(self.bottom_hbox)

        self.main_vbox.addWidget(self.top_wid)
        self.main_vbox.addWidget(self.bottom_wid)

        self.prev_btn = QPushButton("Prev")
        self.pause_play_btn = QPushButton("Play/Pause")
        self.next_btn = QPushButton("Next")
        self.back_btn = QPushButton("Back")

        try:
            track = self.sp_client.get_current_playback()
        except Exception as e:
            em = QErrorMessage(self)
            em.showMessage(
                f"No Players available\nExact Python error was: {str(e)}; Start Spotify player on desired device"
            )
            self.top_level_screen()
            return

        self.song_label = QLabel(
            "Currently Playing: " + track.name + " by " + track.artist
        )

        self.bottom_hbox.addWidget(self.prev_btn)
        self.bottom_hbox.addWidget(self.pause_play_btn)
        self.bottom_hbox.addWidget(self.next_btn)

        self.top_hbox.addWidget(self.song_label)
        self.top_hbox.addStretch()
        self.top_hbox.addWidget(self.back_btn)

        self.back_btn.clicked.connect(lambda: self.back_btn_click())
        self.prev_btn.clicked.connect(lambda: self.prev_btn_click())
        self.pause_play_btn.clicked.connect(lambda: self.pause_play_btn_click())
        self.next_btn.clicked.connect(lambda: self.next_btn_click())

    def pause_play_btn_click(self):
        self.sp_client.play_pause_song()

    def prev_btn_click(self):
        self.sp_client.previous_song()
        time.sleep(0.5)
        track = self.sp_client.get_current_playback()
        self.song_label.setText(
            "Currently Playing: " + track.name + " by " + track.artist
        )

    def next_btn_click(self):
        self.sp_client.next_song()
        time.sleep(0.5)
        track = self.sp_client.get_current_playback()
        self.song_label.setText(
            "Currently Playing: " + track.name + " by " + track.artist
        )

    def create_playlist_btn_click(self):
        self.main_screen()

    def get_categories_btn_clicked(self, categories):
        self.cat_window = choose_category_window(categories, self.sp_client)
        self.cat_window.show()

    def main_screen(self):

        self.resize(400, 150)
        self.main_wid = QWidget()
        self.setCentralWidget(self.main_wid)

        self.spin_song_amount = QSpinBox(self)
        self.spin_song_amount.setMinimum(1)
        self.spin_song_amount.setMaximum(5)
        self.label_amount = QLabel("How many songs do you want to grab? (1-5)", self)

        self.get_songs_btn = QPushButton("Get Songs")

        self.vbox = QVBoxLayout()
        self.form_layout = QFormLayout()
        self.vbox.addLayout(self.form_layout)
        self.form_layout.addRow(self.label_amount, self.spin_song_amount)

        self.label_recent_songs = QLabel("")

        self.form_layout_lower = QFormLayout()
        self.vbox.addLayout(self.form_layout_lower)
        self.form_layout_lower.addRow(self.get_songs_btn, self.label_recent_songs)

        self.prompt_playlist = QLabel(
            "Do you want to create a new playlist based on these songs?"
        )
        self.create_btn = QPushButton("Create Playlist")
        self.vbox.addWidget(self.prompt_playlist)
        self.vbox.addWidget(self.create_btn)
        self.prompt_playlist.hide()
        self.create_btn.hide()

        self.back_btn = QPushButton("Back")
        # self.form_layout_lower.addRow(self.back_btn)
        self.vbox.addWidget(self.back_btn)

        self.main_wid.setLayout(self.vbox)

        # On button click, call get_recent_tracks function in client object and update label on screen
        self.get_songs_btn.clicked.connect(
            lambda: self.get_songs_btn_click(
                str_amount=self.spin_song_amount.value(),
                recent_tracks=self.recent_tracks,
            )
        )
        self.back_btn.clicked.connect(lambda: self.back_btn_click())

    def back_btn_click(self):
        self.top_level_screen()

    def get_songs_btn_click(self, str_amount, recent_tracks):

        recent_tracks = self.sp_client.get_recent_tracks(str_amount)

        self.str_label = ""
        for index, track in enumerate(recent_tracks):
            self.str_label += f"{index+1} - {track}\n"
        self.label_recent_songs.setText(self.str_label)

        self.seed_tracks_uri = []
        for seed_track in recent_tracks:
            self.seed_tracks_uri.append(seed_track.uri)

        self.vbox.removeWidget(self.get_songs_btn)
        # self.get_songs_btn.deleteLater()
        # self.get_songs_btn = None

        self.prompt_playlist.show()
        self.create_btn.show()

        self.create_btn.clicked.connect(
            lambda: self.create_btn_click(seed_tracks=recent_tracks)
        )

    def create_btn_click(self, seed_tracks):
        self.new_window = create_playlist_window(seed_tracks, self.sp_client)
        self.new_window.show()
        self.main_screen()


class create_playlist_window(QWidget):
    def __init__(self, seed_tracks, sp_client):
        super().__init__()
        self.seed_tracks = seed_tracks
        self.resize(600, 150)
        self.sp_client = sp_client

        # self.input_playlist_length = QLineEdit()
        self.spin_playlist_length = QSpinBox()
        self.spin_playlist_length.setMinimum(1)
        self.spin_playlist_length.setMaximum(100)
        self.input_playlist_name = QLineEdit()
        self.submit_btn = QPushButton("Submit")
        self.final_message = QLabel(
            "Your new playlist is created and should be \n playing in your Spotify client now!"
        )

        self.setLayout(QFormLayout())
        self.layout().addRow(
            "How many songs would you like the playlist to be? (1-100)",
            self.spin_playlist_length,
        )
        self.layout().addRow(
            "What would you like to name the playlist?", self.input_playlist_name
        )

        self.layout().addRow("Press to create your new playlist!", self.submit_btn)

        self.submit_btn.clicked.connect(
            lambda: self.submit_btn_click(
                seed_tracks=self.seed_tracks,
                song_amount=self.spin_playlist_length.value(),
                playlist_name=self.input_playlist_name.text(),
            )
        )

    # Function that uses the passed in recently played songs as seed songs for a recommended song playlist
    def submit_btn_click(self, seed_tracks, song_amount, playlist_name):
        recommended_tracks = self.sp_client.get_recommendations(
            seed_tracks, limit=song_amount
        )

        playlist = self.sp_client.create_playlist(playlist_name)

        self.sp_client.fill_playlist(recommended_tracks, playlist)

        self.layout().addWidget(self.final_message)


class choose_category_window(QWidget):
    def __init__(self, categories, sp_client):
        super().__init__()
        self.categories = sp_client.get_categories()
        self.resize(500, 500)
        self.sp_client = sp_client

        self.formLayout = QFormLayout()
        self.groupBox = QGroupBox()

        for cat in self.categories:
            current_btn = QPushButton(cat.name)
            current_btn.clicked.connect(
                lambda checked, id=cat.id: self.category_btn_click(id)
            )
            # self.main_wid.addWidget(current_btn)
            self.formLayout.addRow(current_btn)

        self.groupBox.setLayout(self.formLayout)

        self.scroll = QScrollArea()
        self.scroll.setWidget(self.groupBox)
        self.scroll.setWidgetResizable(True)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.scroll)

    def category_btn_click(self, category_id):
        results = self.sp_client.get_category_playlists(category_id)
        seed_tracks = []
        for p in results:
            id = p["id"]
            seed_tracks.append(self.sp_client.grab_playlist_songs(id))

        rec_songs = self.sp_client.get_recommendations(seed_tracks, limit="20")

        self.sp_client.add_songs_to_queue(rec_songs)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarktheme.load_stylesheet())
    win = ui_main(recent_tracks=[], categories=[])
    win.show()
    sys.exit(app.exec_())
