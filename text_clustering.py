# forming dataset
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# reading csv file
text_df = pd.read_csv('India_censored_domains.csv', header = None)

# the first column is of the form 'domain': 'keyphrase'; extracting keyphrase from this into a separate column and changing the first column
keyphrase_column = [keyphrase.split(':')[1].strip() for keyphrase in text_df.iloc[:, 0].to_list()]
text_df[text_df.shape[1]] = keyphrase_column
text_df[0] = text_df[0].map(lambda x : x.split(':')[0].strip())

# concatenating all keyphrases
keyphrase_column = []
for i, row in text_df.iterrows():
  keyphrases = ' '.join(str(x) for x in row[1:].values.flatten() if x is not np.nan)
  keyphrase_column.append(keyphrases)

# forming final dataframe
cluster_df = pd.DataFrame()
cluster_df['Domain'] = text_df.iloc[:, 0]
cluster_df['Keyphrases'] = keyphrase_column
cluster_df.set_index('Domain', inplace=True)

# clustering similar domains based on their keyphrases

# Convert the phrases to a matrix of TF-IDF features
vectorizer = TfidfVectorizer(stop_words='english')
X = vectorizer.fit_transform(cluster_df['Keyphrases'])

# Determine the optimal number of clusters using silhouette score
scores = []
for k in range(2, 10):
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(X)
    score = silhouette_score(X, kmeans.labels_)
    scores.append(score)
optimal_k = scores.index(max(scores)) + 2  # add 2 because range starts from 2

# Perform clustering with optimal number of clusters
kmeans = KMeans(n_clusters=optimal_k, random_state=42)
kmeans.fit(X)

# Add the cluster labels to the DataFrame
cluster_df['Cluster'] = kmeans.labels_

cluster_df.to_csv('India_clusters.csv')

#f = open('clusters.csv', 'a')

gb = cluster_df.groupby('Cluster')
for key, values in gb:
  print(key, values)