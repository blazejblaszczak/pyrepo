from bs4 import BeautifulSoup
import requests


URL = 'https://web.archive.org/web/20200518073855/https://www.empireonline.com/movies/features/best-movies-2/'

response = requests.get(URL)
website_html = response.text

soup = BeautifulSoup(website_html, "html.parser")

# creating list with top 100 movies from empire site
all_movies = soup.find_all(name="h3", class_="title")
movie_titles = [movie.getText() for movie in all_movies]
movies = movie_titles[::-1]
