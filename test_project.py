import pytest, os, project
from lyricsgenius import Genius
from project import LYRICS_TOKEN


LYRICS_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "lyrics_test")

def test_fetch_lyrics_online():
    with pytest.raises(FileNotFoundError):
        project.fetch_lyrics_online("not a song", "not an artist", Genius(LYRICS_TOKEN), "test")


def test_clean_lyrics():
    lyrics = "You might also like the [test] test Embed"
    assert project.clean_lyrics(lyrics) == [" test "]


def test_get_randomized_songs():
    with pytest.raises(FileNotFoundError):
        project.get_randomized_lyrics(["test"], "test")
    
    # IndexError is raised first because random.choice gets
    # executed first before opening the file
    with pytest.raises(IndexError):
        project.get_randomized_lyrics([], "test")

    with pytest.raises(IndexError):
        project.get_randomized_lyrics([], LYRICS_PATH)


def test_scan_songs():
    assert project.scan_songs(LYRICS_PATH) == ["BINI - Salamin, Salamin"]
    # os.path.dirname(os.path.realpath(__file__)) is the dir where the python project file is located
    assert project.scan_songs(os.path.dirname(os.path.realpath(__file__))) == []