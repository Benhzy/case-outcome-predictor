from openai import OpenAI
import pandas as pd
import tiktoken
import os
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def get_embedding(text, model="text-embedding-3-large"):
   text = text.replace("\n", " ")
   return client.embeddings.create(input = [text], model=model).data[0].embedding


embedding_model = "text-embedding-3-large"
embedding_encoding = "cl100k_base"
max_tokens = 8000  # the maximum for text-embedding-3-small is 8191

# load & inspect dataset
input_datapath = "facts.csv" 
df = pd.read_csv(input_datapath)
df = df.dropna()

# embed
encoding = tiktoken.get_encoding(embedding_encoding)
df["embedding"] = df.facts.apply(lambda x: get_embedding(x, model=embedding_model))
df.to_csv("facts_embedded.csv")


