import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk
import json
from gensim import corpora, models

nltk.download('stopwords')
nltk.download('wordnet')

def load_and_preprocess_csv(filepath):
    df = pd.read_csv(filepath)
    df['processed_facts'] = df['facts'].apply(preprocess_text)
    df.drop(columns=['facts'], inplace=True)
    return df

def load_and_preprocess_json(filepath):
    data = []
    with open(filepath, 'r') as file:
        for line in file:
            data.append(json.loads(line))

    df = pd.DataFrame(data)
    df = df[['casename', 'facts']]    
    df['processed_facts'] = df['facts'].apply(preprocess_text)
    df.drop(columns=['facts'], inplace=True)
    return df

def preprocess_text(text):
    text = str(text).lower()
    text = re.sub(r'\W', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    words = text.split()
    words = [lemmatizer.lemmatize(word) for word in words if word not in stop_words]
    return ' '.join(words)

def perform_topic_modeling(df, num_topics=20):
    texts = [doc.split() for doc in df['processed_facts']]
    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]

    lsa_model = models.LsiModel(corpus, num_topics=num_topics, id2word=dictionary)
    topics_matrix = lsa_model[corpus]

    topics = [max(prob, key=lambda y: y[1])[0] for prob in topics_matrix]
    df['themes'] = topics
    df.drop(columns=['processed_facts'], inplace=True)
    return df

def save_results(df, output_filepath):
    df[['casename', 'themes']].to_csv(output_filepath, index=False)

def main(input_filepath, output_filepath):
    df = load_and_preprocess_json(input_filepath)
    df = perform_topic_modeling(df)
    save_results(df, output_filepath)

main('facts.json', 'fact_themes.csv')
