from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.openai import OpenAI
import openai

"""
This code sets up a chatbot that uses the OpenAI GPT-4 model for natural language understanding,
using the Llama-based indexing system.
It reads in a set of documents, uses them to create a knowledge index, and then allows for interactive,
real-time chat based on this index.
"""

openai.log = 'debug'

# define LLM
llm = OpenAI(model="gpt-4", temperature=0, max_tokens=1000)

# configure service context
Settings.llm = llm

# load documents
documents = SimpleDirectoryReader('documents').load_data()

# create index
index = VectorStoreIndex.from_documents(documents)

# create chatbot
chat_engine = index.as_chat_engine(verbose=True, chat_mode='react')
chat_engine.chat_repl()
