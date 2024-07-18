import tweepy, os, json, random, re, time, argparse
from tweepy.errors import (BadRequest, 
                           Forbidden,
                           Unauthorized,
                           NotFound,
                           TooManyRequests,
                           TwitterServerError)
from lyricsgenius import Genius 

# tokens for tweepy
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

# token for lyricsgenius
LYRICS_TOKEN = os.getenv("LYRICS_TOKEN")

LYRICS_PATH = os.getenv("LYRICS_PATH")

# details for the command-line arguments
DESCRIPTION = "A command-line program that posts random lyrics of BINI songs to Twitter (X)."
ADD_HELP = "Fetch lyrics of a song by Bini online and stores it to a json file. Make sure to enclose the\
    song title in quotes."
SONG_HELP = "Get random lyrics from a specific song. Make sure to enclose the song title in quotes."


def main():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("--add", metavar='"Song Title"', help=ADD_HELP)
    parser.add_argument("--song", metavar='"Song Title"', help=SONG_HELP)
    args = parser.parse_args()

    if args.add:
        fetch_lyrics_online(args.add, "BINI", Genius(LYRICS_TOKEN), LYRICS_PATH)
        return
    
    client = tweepy.Client(BEARER_TOKEN, CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    
    while True:
        try:
            songs: list[str] = [f"BINI - {args.song}"] if args.song else scan_songs()
            tweet: str = get_randomized_lyrics(songs)
            client.create_tweet(text=tweet)
            print(f"Tweet:\n\n{tweet}")
            print("Tweeted successfully!")
            break

        except (BadRequest, Unauthorized, NotFound, TooManyRequests, 
                TwitterServerError, FileNotFoundError) as err:
            print(f"Failed to post tweet. Error: {err}.")
            break

        except Forbidden as err:
            print(f"Failed to post tweet. Error: {err}.")
            print(f"Retrying...")
            time.sleep(1)


def scan_songs(songs_dir: str=LYRICS_PATH) -> list[str]:
    '''
    Find files formatted with "Artist - Song Title.json"
    and returns the list of songs found.
    '''
    songs_found = []

    for song in os.listdir(songs_dir):
        if (pattern := re.match(r"(.+ - .+).json", song)):
            songs_found.append(pattern.group(1))

    return songs_found


def get_randomized_lyrics(songs: list[str], path_to_songs: str=LYRICS_PATH) -> str:
    """
    The songs must be in the format:
    Artist - Song Title.json
    Or this function might return odd results
    (like artist and lyrics switching places or failing to open file)

    raises IndexError if songs list is empty
    and FIleNotFoundError if path_to_songs is invalid
    """

    try:
        chosen_song = random.choice(songs)

        with open(f"{path_to_songs}\\{chosen_song}.json", encoding="utf-8") as f:
            lyrics = json.load(f)
            song_title = chosen_song.split("-")[-1].title().strip()
            return f'From "{song_title}":\n\n{lyrics[random.randint(0, len(lyrics)-1)]}' 
    
    except FileNotFoundError:
        raise FileNotFoundError(f"{path_to_songs} directory not found.")
    
    except IndexError:
        raise IndexError("The songs list is probably empty.")


def fetch_lyrics_online(song_title: str, song_artist: str, genius_api: Genius, write_path: str=LYRICS_PATH) -> int:
    '''
    Fetches lyrics from Genius.com via lyricsgenius API, and writes it to a json file
    in a specified directory (default = current working dir/lyrics).

    genius_api = Genius(access_token)
    Get your access_token at https://genius.com/api-clients/new
    '''
    # verbose set to true to get a detailed message if ever search_song fails
    genius_api.verbose=True
    song = genius_api.search_song(song_title, song_artist)
    song_title = song_title.title()

    try:
        with open(f"{write_path}\\{song_artist} - {song_title}.json", "w", encoding="utf-8") as file:
            lyrics = clean_lyrics(song.lyrics)
            json.dump(lyrics, file)

        print("Writing json file...")
        time.sleep(1)
        print(f"Success! {song_artist} - {song_title}.json can be found in {write_path}.")
    
    except FileNotFoundError:
        raise FileNotFoundError(f"{write_path} directory not found.")      


def clean_lyrics(lyrics: str) -> list[str]:
    temp_lyrics = lyrics.replace("You might also like", "").replace("Embed", "").replace("\n\n", "\n") 
    temp_lyrics = re.split(r"\[.+\]", temp_lyrics)[1:]

    # remove the \n at the beginning of every line if present
    cleaned_lyrics = [line.removeprefix("\n") for line in temp_lyrics]

    return cleaned_lyrics


if __name__ == "__main__":
    main()

    