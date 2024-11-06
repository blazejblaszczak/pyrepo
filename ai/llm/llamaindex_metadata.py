from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

"""
This code imports classes from a llama_index module,
loads and categorizes two types of documents for customer support and marketing respectively.
It generates a combined index from these categorized documents and saves it.
Finally, a chat engine is created using this index and a chat session is started.
"""

# load documents
docs1 = SimpleDirectoryReader(input_files=['./docs1/doc.csv']).load_data()
docs2 = SimpleDirectoryReader('docs2').load_data()
docs1[0].metadata['category'] = 'customer support'

for doc in docs2:
    doc.metadata['category'] = 'marketing'
all_docs = docs1 + docs2

# create index
index = VectorStoreIndex.from_documents(all_docs)

# save index
index.storage_context.persist()

# create chatbot
chat_engine = index.as_chat_engine(verbose=True, chat_mode='react')
chat_engine.chat_repl()
