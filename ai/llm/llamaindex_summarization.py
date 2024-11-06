from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, SummaryIndex

# load documents
docs = SimpleDirectoryReader(input_files=['./docs1/doc.csv']).load_data()
docs[0].metadata['category'] = 'customer support'

# create index
index = VectorStoreIndex.from_documents(docs)

# save index
index.storage_context.persist()

# query
query_engine = index.as_query_engine(verbose=True, similarity_top_k = 6, response_mode='tree_summarize')
response = query_engine.query('summarize our customer support content')
print(response)
print(response.get_formatted_sources())
#print(response.source_nodes)
