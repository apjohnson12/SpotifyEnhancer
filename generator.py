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


class ui_main(QMainWindow):
    def __init__(self, recent_tracks, categories):
        super().__init__()
  
        self.top_level_screen()
    
        self.recent_tracks = recent_tracks
        self.categories = categories



    def top_level_screen(self):

        with open("login.yaml", "r") as f:
            loginInfo = yaml.safe_load(f)
        self.sp_client = SpotifyClient(loginInfo["client_id"], loginInfo["username"], loginInfo["client_secret"], loginInfo["redirect_uri"])

        self.resize(400, 200)
        self.main_wid = QWidget()
        self.setCentralWidget(self.main_wid)
        self.main_vbox = QVBoxLayout()
        self.main_wid.setLayout(self.main_vbox)

        self.welcome_label = QLabel("## Spotify Enhancer Application")
        self.welcome_label.setTextFormat(QtCore.Qt.MarkdownText)
        self.welcome_label.setStyleSheet("color: green;"
                                        "font: bold 20px;"
                                        
                                        )
        
        self.welcome_label.setAlignment(QtCore.Qt.AlignCenter)
        self.create_playlist_btn = QPushButton("Create Recommended Playlist")
        self.get_categories_btn = QPushButton("Get Categories")

        self.main_vbox.addStretch()
        self.main_vbox.addWidget(self.welcome_label)
        self.main_vbox.addStretch()
        self.main_vbox.addWidget(self.create_playlist_btn)
        self.main_vbox.addWidget(self.get_categories_btn)
        

        self.create_playlist_btn.clicked.connect(lambda: self.create_playlist_btn_click())
        self.get_categories_btn.clicked.connect(lambda: self.get_categories_btn_clicked(categories=self.categories))

    def create_playlist_btn_click(self):
        self.main_screen()

    def get_categories_btn_clicked(self, categories):
        self.cat_window = choose_category_window(categories, self.sp_client)
        self.cat_window.show()

    def main_screen(self):

        self.resize(300, 150)
        self.main_wid = QWidget()
        self.setCentralWidget(self.main_wid)

        self.song_amount_edit = QLineEdit()     
        self.label_amount = QLabel("How many songs do you want to grab? (1-5)", self)
        
        self.get_songs_btn = QPushButton("Get Songs")

        self.vbox = QVBoxLayout()
        self.form_layout = QFormLayout()
        self.vbox.addLayout(self.form_layout)
        self.form_layout.addRow(self.label_amount, self.song_amount_edit)

        self.label_recent_songs = QLabel("")

        self.form_layout_lower = QFormLayout()
        self.vbox.addLayout(self.form_layout_lower)
        self.form_layout_lower.addRow(self.get_songs_btn, self.label_recent_songs)

        self.main_wid.setLayout(self.vbox)

        # On button click, call get_recent_tracks function in client object and update label on screen 
        self.get_songs_btn.clicked.connect(lambda: self.get_songs_btn_click(str_amount=self.song_amount_edit.text(), recent_tracks=self.recent_tracks))


    def get_songs_btn_click(self, str_amount, recent_tracks):
        
        recent_tracks = self.sp_client.get_recent_tracks(str_amount)
    
        self.str_label = ""
        for index, track in enumerate(recent_tracks):
            self.str_label += (f"{index+1} - {track}\n")
        self.label_recent_songs.setText(self.str_label)

        self.seed_tracks_uri = []
        for seed_track in recent_tracks:
            self.seed_tracks_uri.append(seed_track.uri)


        self.vbox.removeWidget(self.get_songs_btn)
        self.get_songs_btn.deleteLater()
        self.get_songs_btn = None

        self.prompt_playlist = QLabel("Do you want to create a new playlist based on these songs?")
        self.create_btn = QPushButton("Create Playlist")
        self.vbox.addWidget(self.prompt_playlist)
        self.vbox.addWidget(self.create_btn)

        self.create_btn.clicked.connect(lambda: self.create_btn_click(seed_tracks=recent_tracks))

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

        self.input_playlist_length = QLineEdit()
        self.input_playlist_name = QLineEdit()
        self.submit_btn = QPushButton("Submit")
        self.final_message = QLabel("Your new playlist is created and should be \n playing in your Spotify client now!")

        self.setLayout(QFormLayout())
        self.layout().addRow("How many songs would you like the playlist to be? (1-100)", self.input_playlist_length)
        self.layout().addRow("What would you like to name the playlist?", self.input_playlist_name)

        self.layout().addRow("Press to create your new playlist!", self.submit_btn)

        self.submit_btn.clicked.connect(lambda: self.submit_btn_click(seed_tracks=self.seed_tracks, song_amount=self.input_playlist_length.text(), playlist_name=self.input_playlist_name.text()))
        
    # Function that uses the passed in recently played songs as seed songs for a recommended song playlist
    def submit_btn_click(self, seed_tracks, song_amount, playlist_name):
        recommended_tracks = self.sp_client.get_recommendations(seed_tracks, limit=song_amount)
        
        playlist = self.sp_client.create_playlist(playlist_name)

        self.sp_client.fill_playlist(recommended_tracks, playlist)

        self.layout().addWidget(self.final_message)

        
        
class choose_category_window(QWidget):
    def __init__(self, categories, sp_client):
        super().__init__()
        self.categories = sp_client.get_categories()
        self.resize(1000, 1000)
        self.sp_client = sp_client

        self.main_vbox = QVBoxLayout()
        self.setLayout(self.main_vbox)

        for cat in self.categories:
            current_btn = QPushButton(cat.name)
            current_btn.clicked.connect(lambda checked, id=cat.id: self.category_btn_click(id))
            self.main_vbox.addWidget(current_btn)

    

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

    