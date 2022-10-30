class Playlist:
    #Playlist represents a spotify playlist

    def __init__(self, name, uri, id):

        self.name = name
        self.uri = uri
        self.id = id
        
    
    def __str__(self):
        return f"Playlist: {self.name}"