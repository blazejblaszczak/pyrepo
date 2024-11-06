from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

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
