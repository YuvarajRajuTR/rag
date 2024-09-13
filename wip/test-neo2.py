from llama_index.graph_stores.neo4j import Neo4jGraphStore
from llama_index.core import StorageContext
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter

# Load text data
text = "data.txt"
loader = TextLoader(text)
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=200, chunk_overlap=20)
texts = text_splitter.split_documents(documents)

from langchain_community.llms import Ollama
from langchain_experimental.graph_transformers.llm import LLMGraphTransformer
import getpass
import os
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    KnowledgeGraphIndex,
)

import logging
import sys

from IPython.display import Markdown, display

logging.basicConfig(
    stream=sys.stdout, level=logging.INFO
)  # logging.DEBUG for more verbose output
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))



# Initialize LLM
llm = Ollama(model="mistral",temperature=0)


# Extract Knowledge Graph
llm_transformer = LLMGraphTransformer(llm=llm)
graph_documents = llm_transformer.convert_to_graph_documents(texts)

# Store Knowledge Graph in Neo4j
graph_store = Neo4jGraphStore(url="bolt://localhost:7687", username="neo4j", password="admin001")
# graph_store.write_graph(graph_documents)
storage_context = StorageContext.from_defaults(graph_store=graph_store)


from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import KnowledgeGraphRAGRetriever
# from llama_index.core.response_synthesis import ResponseSynthesizer

# Retrieve Knowledge for RAG
graph_rag_retriever = KnowledgeGraphRAGRetriever(storage_context=storage_context, verbose=True)
query_engine = RetrieverQueryEngine.from_args(graph_rag_retriever)

def query_and_synthesize(query):
    retrieved_context = query_engine.query(query)
    response = response_synthesizer.synthesize(query, retrieved_context)
    print(f"Query: {query}")
    print(f"Answer: {response}\n")

# Initialize the ResponseSynthesizer instance
response_synthesizer = ResponseSynthesizer(llm)

# Query 1
query_and_synthesize("Where does Sarah work?")

# Query 2
query_and_synthesize("Who works for prismaticAI?")

# Query 3
query_and_synthesize("Does Michael work for the same company as Sarah?")