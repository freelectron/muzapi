# Try to get music from the first website (yandex.ru) when entered 'listen music online free'

import requests
import logging as logger
from bs4 import BeautifulSoup
import os
from collections import defaultdict
import warnings


# Filter bs4 Warnings
warnings.filterwarnings("ignore", category=UserWarning, append=True)


def parse_html_search_list(content):
    """
  Parse html to retrieve songs returned by the search.

  Args:
	content (string): content of the request retrieved from z1.fm document starting with <html> and ending with </html>

  Returns:
	BeautifulSoup instance, holding in html from of the search results from z1.fm
  """
    soup = BeautifulSoup(content, "html.parser")

    # Index list for song search results
    soup_search_songs_list = BeautifulSoup(
        str(soup.find_all("div", class_="songs-list")[1])
    )
    soup_search_songs = BeautifulSoup(
        str(soup_search_songs_list.find_all("div", class_="songs-list-item"))
    )

    return soup_search_songs


def parse_songs_info(soup_songs_list, n=1):
    """
    Given the search list produced by z1.fm, get all n-th song's artist, name and download link.

    Args:
	    n (int): get info of the first n songs.
	    soup_songs_list (BeautifulSoup object): bt4 instance with html of the div with the tag
    Returns:
	    dictionary, where keys are song ids adn value is a dictionary with the information.
    """
    songs_info = defaultdict()

    for n in range(n):
        # Main tag of first song in the list
        div_search_song = soup_songs_list.find_all(
            "div", class_="song-wrap song-wrap-xl"
        )[n]
        # div_name_first_search_song = div_search_song.find_all('div', class_='song-name')
        # html_song_info = str(div_search_song)

        # Find/record song artist
        song_artist = div_search_song.find_all("div", class_="song-artist")[0].text

        # Find/record song's name
        song_name = div_search_song.find_all("div", class_="song-name")[0].text

        # Find download id
        ul_tag = str(div_search_song.find_all("ul"))
        # FIXME: use regex here instead of searching like this
        data_url = ul_tag[ul_tag.find("data-url") : ul_tag.find("data-url") + 45].split(
            " "
        )[0]
        download_route = data_url.split('"')[1]

        # Parsing check: download_route should be of the following format "/download/12345678"
        assert download_route.split("/")[1] == "download"
        assert download_route.split("/")[2].isdigit()

        songs_info[download_route.split("/")[2]] = dict(
            song_artist=song_artist, song_name=song_name, download_route=download_route
        )

    return songs_info


def download_mp3(download_url, s, path_filename):
    """
    Download a song from z1.fm.

    Args:
    download_url (str): url to load the mp3 from
    s (requests.Session): session with already stored headers for z1.fm

    Returns:
    flag, if the down load was successful
    """
    # Download and save mp3

    # Get the link
    try:
        song_request_response = s.get(download_url)
    except Exception as e:
        logger.error(f"The following error was encountered: {e}")
        logger.CRITICAL(download_url)

    with open(os.path.join(path_filename), "wb") as f:
        f.write(song_request_response.content)


def run(search_entry):
    """
    Run z1.fm scaper to retrieve a song given by search_sting
    Args:
    search_string (string): what song to search in z1.fm
    """

    # Send GET request
    url_main = "https://z1.fm"

    # See how to send a 'search request' aka search for some song
    search_url = "https://z1.fm/mp3/search?keywords="

    # Try with Sessions
    s = requests.Session()

    # Get a cookie and some other parameters which will be used in the session
    s.get(url_main)
    r = s.get(search_url + search_entry)

    # Select the first song in the search list. Do not choose the first tag
    content = r.text[15:][:-2]

    soup_songs_list = parse_html_search_list(content)
    songs_info = parse_songs_info(soup_songs_list, n=5)

    # Choose a song and download it
    random_song_idx = 3
    song_id = list(songs_info.keys())[random_song_idx]
    download_route = songs_info[song_id]["download_route"]
    path = "./"
    path_filename = os.path.join(
        path,
        songs_info[song_id]["song_artist"] + "_" + songs_info[song_id]["song_name"],
    )
    download_url = url_main + download_route
    download_mp3(download_url, s, path_filename=path_filename)


if __name__ == "__main__":
    # Testing
    search_entry_monethochka = "/монеточка"
    search_entry_BIG = "/biggie+smalls"
    run(search_entry_BIG)
