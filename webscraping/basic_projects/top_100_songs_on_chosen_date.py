from bs4 import BeautifulSoup
import requests


date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")

URL = f'https://www.billboard.com/charts/hot-100/{date}'

response = requests.get(URL)
website_html = response.text

soup = BeautifulSoup(website_html, "html.parser")

# creating lists with song titles and artists
songs = soup.select("li ul li h3")
song_titles = [song.get_text(strip=True) for song in songs]
artists = soup.find_all(name='span', class_='a-truncate-ellipsis-2line')
artists_list = [artist.getText(strip=True) for artist in artists]

# creating dictionary with top 100 songs
top_songs = dict(zip(song_titles, artists_list))
