import openai
from openai import OpenAI
import wikipedia
import os


# pass the api key
client = OpenAI(
    api_key=os.environ.get('OPENAI_API_KEY')
)

# get user input
title = input('title of the page: ')

# get the wikipedia content
page = wikipedia.page(title=title, auto_suggest=False)

# define prompt
prompt = 'Write a summary of the following article: ' + page.content[:10000]
messages = []
messages.append({'role': 'user', 'content': prompt})

try:
    # make an api call
    response = client.chat.completions.create(messages=messages, model="gpt-3.5-turbo")
    # print the response
    print(response.choices[0].message.content)
  
# authentication issue
except openai.AuthenticationError:
    print('no valid token / authentication error')
  
except openai.BadRequestError as e:
    print('invalid request, read the manual!')
    print(e)
