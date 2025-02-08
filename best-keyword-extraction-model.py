# code that picks the best keyword extraction model for analyzing censorship data

#################################
# importing libraries
from google.colab import auth
import gspread
from google.auth import default
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer, util

#################################
# authenticating drive access
auth.authenticate_user()
creds, _ = default()
gc = gspread.authorize(creds)

#################################
# forming dataframe
# input is of the form domain : keywords extracted from manual inspection : keywords extracted from each model

# reading the sheets file
worksheet = gc.open('Domain Keyword Extraction').sheet1
# get_all_values gives a list of rows, getting header row from it
rows = worksheet.get_all_values()
header_row = rows[0]
# Convert to a DataFrame and render.
keyword_df = pd.DataFrame.from_records(rows[1:], columns=header_row)

#################################
# data preprocessing

# dropping unnecessary columns 
# picking columns with models that go up until 15 links and dropping the rest
keyword_df.drop(['Number of Links Followed', 'Manual Inspection Completed By', 'YAKE Keywords Web Crawler set to 5','YAKE Keywords Web Crawler set to 10','Multipartite Rank Keywords with Web Crawler set to 5','Multipartite Rank Keywords with Web Crawler set to 10','EmbedRank Keywords with Web Crawler set to 5','EmbedRank Keywords with Web Crawler set to 10','PatternRank Keywords with Web Crawler set to 5 ','PatternRank Keywords with Web Crawler set to 10'], axis=1, inplace=True, errors='ignore')
# rename columns
keyword_df.rename(columns = {'YAKE Keywords Web Crawler set to 15':'YAKE', 'Multipartite Rank Keywords with Web Crawler set to 15':'Multipartite Rank', 'EmbedRank Keywords with Web Crawler set to 15':'EmbedRank', 'PatternRank Keywords with Web Crawler set to 15':'PatternRank'}, inplace=True)
# setting domain as index
keyword_df.reset_index()
keyword_df.set_index('Domain', inplace=True)

#################################
# sentence encoding

# loading pre-trained sentence transformermodels which encodes sentences
sentence_model = SentenceTransformer('distilbert-base-nli-stsb-mean-tokens')
# method to compute similarity between a list of phrases
def compute_similarities(list1, list2):
  # Get the embeddings of each list of phrases
  embeddings1 = sentence_model.encode(list1, convert_to_tensor=True)
  embeddings2 = sentence_model.encode(list2, convert_to_tensor=True)
  # Compute the cosine similarity between the two sets of embeddings
  return np.mean(util.pytorch_cos_sim(embeddings1, embeddings2).detach().cpu().numpy())

#################################
# method to iterate over all the results given by the models and select the best model
def best_model_selector(input_list, model_result_lists):
  max_similarity = -1
  best_model = []
  for model in model_result_lists.keys():
    similarity = compute_similarities(input_list, model_result_lists[model])
    if max_similarity <= similarity:
      max_similarity = similarity
      best_model.append(model)
  return best_model

# iterating over each dataframe and finding similar list
# each column containing the result of each keyword extraction model that is to be compared with the keywords picked manually
columns_to_be_compared = ['YAKE','Multipartite Rank','EmbedRank','PatternRank']
# declaring a result dataframe which picks the best keyword extraction model for each domain
result_df = {}
# iterating over each row in the dataframe
for domain, row in keyword_df.iterrows():
  # a dictionary of the form {model : keywords}
  data_with_columns = {}
  # creating a list of the 10 keyword phrases picked upon manual inspection
  if(row['10 Keyword phrases'] is not np.NaN):
    input_list = row['10 Keyword phrases'].split(', ')    
    # for each of the keyword extraction model results, we create a list of all the words picked and add it to the dictionary
    dict_values = []
    for column in columns_to_be_compared:
      if(row[column] is not np.NaN):
        dict_values = row[column].split(', ')
        if(dict_values is not None and len(dict_values) > 1):
          data_with_columns[column] = dict_values
          result_df[domain] = best_model_selector(input_list, data_with_columns)
# forming resulting dataframe
result_df = pd.DataFrame({"Domain": list(result_df.keys()), "Best Keyword Extraction Model" : list(result_df.values())})
result_df.set_index('Domain', inplace=True)

#################################
# plotting a bar graph showing the number of times a keyword extraction model has been picked for a domain
yake_count = 0
multipartite_rank_count = 0
embed_rank_count = 0
pattern_rank_count = 0

for domain, row in result_df.iterrows():
  models = row['Best Keyword Extraction Model']
  if columns_to_be_compared[0] in models:
    yake_count += 1
  if columns_to_be_compared[1] in models:
    multipartite_rank_count += 1
  if columns_to_be_compared[2] in models:
    embed_rank_count += 1
  if columns_to_be_compared[3] in models:
    pattern_rank_count += 1

graph_df = pd.DataFrame({"Model" : columns_to_be_compared, "Count" : [yake_count, multipartite_rank_count, embed_rank_count, pattern_rank_count]})

# plot pie chart
plt.pie(graph_df["Count"], labels = graph_df["Model"], autopct='%1.2f%%')
plt.axis('equal')
plt.tight_layout()
plt.show()