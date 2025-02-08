import yake
import os
import fnmatch
import re
import sys

language = "en"
max_ngram_size = 3
deduplication_threshold = 0.9
deduplication_algo = 'seqm'
windowSize = 1
numOfKeywords = 10

custom_kw_extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, dedupLim=deduplication_threshold, dedupFunc=deduplication_algo, windowsSize=windowSize, top=numOfKeywords, features=None)

country = sys.argv[1]
start_date = sys.argv[2]

reg = re.compile(r'[a-zA-Z]')

for file in os.listdir(country + '-content'):
    if fnmatch.fnmatch(file, '*.txt'):
        
        #Check if content exists for domain
        if os.path.getsize(country + '-content/' + file) != 0:

            print("Extracting keyphrases from " + file)
            
            #Open file with content
            with open(country + '-content/' + file) as f:
                doc = f.read()
            
            #Extract keyphrases
            keywords = custom_kw_extractor.extract_keywords(doc)
            keywords_list = []

            for kw in keywords:
                if reg.match(kw[0]):
                    keywords_list.append(kw[0])
            if len(keywords_list) > 0:
                with open(country + '_' + start_date + '_ censored_domains.csv', 'a') as fp:
                    fp.write(file[:-13] + ': ')
                    for item in keywords_list:
                        fp.write(item + ', ')
                    fp.write('\n')