#!/bin/bash

start_date="2022-08-07"
end_date="2022-08-23"
country="Russia"

#python3 censorship-domain-extraction-ac.py $start_date $end_date $country

#if [ ! -d '$country-content' ];
#then
#    mkdir ${country}-content
#fi

while read -r line
do 
    echo "$line"
    python3 main.py $line
    python3 txt_data.py $country
    
done < ${country}_censored_domains.txt

python3 keyword_extraction.py $country $start_date
