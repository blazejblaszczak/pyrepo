from openai import OpenAI
import gradio as gr
import os


client = OpenAI(
    api_key=os.environ.get('OPENAI_API_KEY')
)

messages = []
messages.append({'role': 'system', 'content': 'You are a quiz. Present the user with a multiple-choice question to practice for a python interview, they have to respond by typing a, b, c, d or e. Only one question at a time. Wait until the user responds before presenting a new question or the answer to the previous question'})


def respond(history, new_message):
    # add the user input to the messages
    messages.append({'role': 'user', 'content': new_message})
    # send the api call
    response = client.chat.completions.create(messages=messages, model="gpt-3.5-turbo")
    # obtain response
    assistant_message = response.choices[0].message
    messages.append(assistant_message)
    return history + [[new_message, assistant_message.content]]


with gr.Blocks() as my_bot:
    chatbot = gr.Chatbot()
    user_input = gr.Text()
    user_input.submit(respond, [chatbot, user_input], chatbot)
  
    
my_bot.launch()
