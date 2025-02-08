# importing libraries

import os
from datetime import datetime
import pandas as pd
import numpy as np
import sys

###################################
# dataframe processing

# utility method to compute date for the given Satellite dataset
def compute_date(csv_file_path):
  date = datetime.strptime(csv_file_path.split("/")[-1][13:23], '%Y-%m-%d')
  df = pd.read_csv(csv_file_path)
  date_col = [date] * df.shape[0]
  df["Date"] = date_col
  return df

# method to process Satellite data
def satellite_domains(path):
  datasets = os.listdir(path) 
  
  # changing CSV file names with the appropriate path for pandas to read them
  datasets = [path + "/" + dataset for dataset in datasets]

  # iterating through all datasets (csv files) and compiling one dataframe
  satellite_df = pd.concat(map(compute_date, datasets), ignore_index = True)

  # filtering compiled dataset and removing any Error measurements from the count
  satellite_df['Measurements'] = satellite_df['Measurements'] - satellite_df['Errors']
  
  # dropping unnecessary columns
  satellite_df.drop(['Vantage Point', 'Errors', 'Confirmations'], axis=1, inplace=True)

  # grouping data by date and then domain, getting aggregate of measurements and anomalies
  _ = satellite_df.groupby(['Date', 'Domain'], as_index=False).sum('Measurements')
  satellite_df = _.apply(lambda x: x) 

  return satellite_df

# utility method to remove rows in a dataframe which contain certain values
def remove_rows_by_values(df, col, values):
    return df[~df[col].isin(values)]

# method to process OONI data
def ooni_domains(path):
  datasets = os.listdir(path) 

  # changing CSV file names with the appropriate path for pandas to read them
  datasets = [path + "/" + dataset for dataset in datasets]

  # iterating through all datasets (csv files) and compiling one dataframe
  ooni_df = pd.concat(map(pd.read_csv, datasets), ignore_index = True)

  # selecting necessary columns and dropping the rest, renaming columns
  ooni_df = ooni_df[['input', 'measurement_start_time', 'blocking_recalc']]
  ooni_df.rename(columns = {"measurement_start_time":"Date", "input":"Domain", "blocking_recalc":"Anomalies"}, inplace=True)

  # changing datatype of Date column to datetime
  ooni_df["Date"] = pd.to_datetime(ooni_df["Date"])
  ooni_df['Date'] = ooni_df['Date'].dt.date.astype('datetime64[ns]')

  # selecting rows with 'Anomalies' value that is not an error, i.e., only removing rows with values 'control_failure' and 'invalid'
  ooni_df = remove_rows_by_values(ooni_df, "Anomalies", ["control failure","invalid"])

  # replacing Anomalies values with 1, signifying the detection of an anomaly, and 'ok' values with 0
  replace_values_dict = dict.fromkeys(list(ooni_df['Anomalies'].unique()), 1)
  replace_values_dict["ok"] = 0
  ooni_df["Anomalies"].replace(replace_values_dict, inplace=True)

  # grouping by date and domain, aggregating all anomalies and adding a column to signify measurements
  # each row is a measurement in the dataframe
  # Rows where blocking_recalc == 'ok' should be summed up to provide the Measurements value but not summed for the Anomalies value
  # If blocking_recalc equals anything else the row should be added to the Measurements value for the given domain as well as the Anomalies value
  ooni_df["Measurements"] = [1 for x in range(ooni_df.shape[0])]
  ooni_df = ooni_df.groupby(['Date', 'Domain'], as_index=False).sum("Measurements")

  return ooni_df

###################################
# database construction for extracted domains

# method to slice dataframes
def slice_and_process(df, start_date, end_date):
  # picking rows on the start date that do not have an anomaly
  mask1 = (df['Date'] == start_date) & (df['Anomalies'] == 0)
  slice1 = df.loc[mask1]
  sliced_domains = list(slice1['Domain'])

  # picking rows that have anomalies on dates after the given start date, until the end date
  # this mask is applied to the data for the domains contained in slice1
  mask2 = (df['Date'] > start_date) & (df['Date'] <= end_date) & (df['Anomalies'] >= 1) & (df['Domain'].isin(sliced_domains))
  slice2 = df.loc[mask2]
  
  return slice2

# method to construct database (merged from Satellite and OONI database)
def construct_database(satellite_path, ooni_path, start_date, end_date):
   # reading CSV files
   satellite_df = satellite_domains(satellite_path)
   ooni_df = ooni_domains(ooni_path)
   
   # for Satellite data
   print('Satellite')
   sliced_satellite_df = slice_and_process(satellite_df, start_date, end_date)
   #print("Sliced dataframe dimensions: {}".format(sliced_satellite_df.shape))
   
   # for OONI data
   print('OONI')
   sliced_ooni_df = slice_and_process(ooni_df, start_date, end_date)
   #print("Sliced dataframe dimensions: {}".format(sliced_ooni_df.shape))
   
   # joining both Satellite and OONI data based on date and domain
   result_df = pd.merge(satellite_df, ooni_df, on='Domain', how='outer', suffixes=('_Satellite', '_OONI'))
   
   return result_df

###################################
# main method

# Obtaining start dates and end dates from user

#print("Enter start date in YYYY-MM-DD:")
start_date = datetime.strptime(sys.argv[1], '%Y-%m-%d')
#print("\n\nEnter end date in YYYY-MM-DD:")
end_date = datetime.strptime(sys.argv[2], '%Y-%m-%d')

# preliminary check
if(start_date > end_date):
  print("Start date cannot be after end date")

else:
  print("\n\nGetting dates from {} to {}".format(start_date.date(), end_date.date()))

  country = sys.argv[3]

  print("Processing censorship data for " + country + ":\n")
  df =  construct_database('../satellite/' + country, '../ooni/' + country, start_date, end_date)
  df.to_csv(country + "-results.csv")

  df['Ratio_OONI'] = df['Anomalies_OONI']/df['Measurements_OONI']
  df['Ratio_Satellite'] = df['Anomalies_Satellite']/df['Measurements_Satellite']

  censored_OONI = df.loc[df['Ratio_OONI'] > 0.5]
  censored_Satellite = df.loc[df['Ratio_Satellite'] > 0.5]

  censored_list = censored_OONI['Domain'].unique()
  combined_censored_list = np.append(censored_list, censored_Satellite['Domain'].unique())

  with open(country + '_censored_domains.txt', 'w') as fp:
    for item in combined_censored_list:
        fp.write("%s\n" % item)