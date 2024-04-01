import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk

nltk.download('stopwords')
nltk.download('wordnet')

def load_and_preprocess(filepath):
    df = pd.read_csv(filepath)
    df['processed_facts'] = df['facts'].apply(preprocess_text)
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

def perform_topic_modeling(df, num_topics=30):
    vectorizer = TfidfVectorizer(max_features=5000)
    tfidf = vectorizer.fit_transform(df['processed_facts'])
    lda = LatentDirichletAllocation(n_components=num_topics, random_state=0)
    lda.fit(tfidf)
    topic_results = lda.transform(tfidf)
    df['themes'] = topic_results.argmax(axis=1)
    return df

def save_results(df, output_filepath):
    df[['casename', 'themes']].to_csv(output_filepath, index=False)

def main(input_filepath, output_filepath):
    df = load_and_preprocess(input_filepath)
    df = perform_topic_modeling(df)
    save_results(df, output_filepath)

main('facts.csv', 'fact_themes.csv')
