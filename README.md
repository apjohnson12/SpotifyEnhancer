# SpotifyEnhancer
A python application utilizing the Spotipy API for a class project in SWE 6623

## Install
This application was developed with Python 3.10.8. Please make sure you have a recent version of python and pip installed. Install the necessary Python packages by running:

```sh
$ python -m pip install -r requirements.txt
```

## Run
Run the entry-point script and follow pop-up window prompts

```sh
$ python generator.py
```

By default, the yaml file has dummy data. The program has limited functionality with the dummy data. It will not be able to hit any endpoints without valid data. If you know your client ID, client Secret, and Username, you can replace the contents with those and the program should be fully functional.