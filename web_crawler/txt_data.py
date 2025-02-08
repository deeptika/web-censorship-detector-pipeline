from urllib.request import urlopen
from bs4 import BeautifulSoup
import os
import glob
import shutil
import requests
import re
import sys

country = sys.argv[1]

# Customize path as the file's address on your system
# text_file = open('E://UF//CIS//Censorship_Project//Web_Crawler//test//crawled.txt','r', encoding="utf8")
text_file_crawled = open(os.path.join(os.getcwd(), 'test//crawled.txt'),'r+', encoding="utf8")
# Read the file line by line using .readlines(), so that each line will be a continuous long string in the "file_lines" list
links = [x.strip() for x in text_file_crawled.readlines()]

#Remove duplicate links from crawled
for link in links:
    link_extended = link + '/'
    if link_extended in links:
        links.remove(link)

#Open queued file
text_file_q = open('test/queue.txt','r', encoding="utf8")
# Read the file line by line using .readlines(), so that each line will be a continuous long string in the "file_lines" list
q_links = [x.strip() for x in text_file_q.readlines()]

#Add links from the queue to crawled to reach the desired number of links
if len(q_links) > 0:
    i = 0
    while len(links) < 15:
        links.append(q_links[i])
        i += 1

domain = links[0]
replace_http = re.sub(r'(https://)|(http://)', "", domain)
replaced_domain = re.sub(r'^www\.', "", replace_http)
replaced_domain = replaced_domain.replace('/', '')
replaced_domain = replaced_domain.split('.')[0]

#Open text file for results. Named based on the url being crawled
text_file_name = country + '-content/' + replaced_domain + '-combined.txt' #os.path.join(os.getcwd(), f'text//data_{i}.txt')
text_file = open(text_file_name, "w", encoding = "utf-8")
#Clear file
text_file.write("")
# close file
text_file.close()

user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers = {'User-Agent': user_agent, }

for i in range(len(links)):
    print("Total: " + str(len(links)) + " || Current: " + str(i))
    url = links[i]

    response = requests.get(url, headers = headers)
    # print("response.content", response.content)
    soup = BeautifulSoup(response.content, "html.parser")

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()    # rip it out

    # get text
    text = soup.get_text()

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)

    # text_file_name = f"E://UF//CIS//Censorship_Project//Web_Crawler//text//data_{i}.txt"
    text_file_name = country + '-content/' + replaced_domain + '-combined.txt' #os.path.join(os.getcwd(), f'text//data_{i}.txt')
    text_file = open(text_file_name, "a", encoding = "utf-8")
    # write string to file
    text_file.write(text)
    # close file
    text_file.close()

    # print(text)

#outfilename = os.path.join(os.getcwd(), 'text//combined.txt')
#with open(outfilename, 'wb') as outfile:
#    for filename in glob.glob(os.path.join(os.getcwd(), 'text//*.txt')):
#        if filename == outfilename:
#            # don't want to copy the output into the output
#            continue
#        with open(filename, 'rb') as readfile:
#            shutil.copyfileobj(readfile, outfile)
