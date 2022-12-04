class Category:
    # Playlist represents a spotify playlist

    def __init__(self, name, id):

        self.name = name
        self.id = id

    def __str__(self):
        return f"Category: {self.name}"
