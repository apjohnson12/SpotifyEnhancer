class Track:
    #Track represents a piece of music on Spotify

    def __init__(self, name, uri, artist):

        self.name = name
        self.uri = uri
        self.artist = artist

    # def create_track_uri(self):
    #     return f"spotify:track:{self.uri}"

    def __str__(self):
        return f"{self.name} by {self.artist}"