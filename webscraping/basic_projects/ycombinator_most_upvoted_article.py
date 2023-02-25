from bs4 import BeautifulSoup
import requests


response = requests.get("https://news.ycombinator.com/news")
yc_web_page = response.text
soup = BeautifulSoup(yc_web_page, 'html.parser')

# checking if correct values are extracted from html
article_tag = soup.find(name="span", class_="titleline")
article_text = article_tag.getText()
article_link = article_tag.find(name="a").get("href")
article_upvote = soup.find(name="span", class_="score").getText()

# creating lists with data from all articles on site
articles = soup.find_all(name="span", class_="titleline")

article_texts = []
article_links = []
for article_tag in articles:
    text = article_tag.getText()
    article_texts.append(text)
    link = article_tag.find(name="a").get("href")
    article_links.append(link)
    
article_upvotes = [int(score.getText().split()[0]) for score in soup.find_all(name="span", class_="score")]

# checking which artcle has the highest number of upvotes
max_index = article_upvotes.index(max(article_upvotes))
print(f'Highest number of upvotes has "{article_texts[max_index]}" article.\nLink to it: {article_links[max_index]}')
