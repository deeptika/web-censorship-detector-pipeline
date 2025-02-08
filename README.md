# Web Censorship Detector Pipeline

_My contribution to the group project for the class CIS 5370 - Computer Information Security, University of Florida_

This project, titled "**Classifying Newly Censored Domains to Measure the Effect of Censorship on Minority Groups**," aims to identify newly censored domains following increased censorship events and analyze their effects, particularly on minority groups.

## Project Overview

The Web Censorship Detector Pipeline is designed to process and analyze censorship data, extract newly censored domains, and classify them to understand the impact of censorship on various groups. The project utilizes multiple data sources and employs various natural language processing techniques to achieve its goals.

## Features

- Extraction of newly censored domains from Censored Planet's Satellite and OONI datasets
- Manual inspection and keyword extraction from identified domains
- Comparison and analysis of keyword extraction models
- Domain clustering using k-means algorithm
- Documentation and code comments for easy understanding and maintenance

## Project Components

### 1. Data Extraction and Preprocessing

- Reads and preprocesses data from Censored Planet's Satellite and OONI censorship datasets
- Identifies newly censored domains within specified date intervals

### 2. Manual Domain Inspection

- Manually inspects identified domains to extract key words and phrases
- Establishes a reference standard for comparing keyword extraction models

### 3. Keyword Extraction Model Analysis

- Compares four keyword extraction models: YAKE, Multipartite Rank, EmbedRank, and PatternRank (done by teammates)
- Utilizes SentenceTransformer for phrase embedding and cosine similarity calculation
- Identifies YAKE as the best-performing keyword extraction model

### 4. Domain Clustering

- Extracts keyphrases from a sample set of domains using the identified best model (YAKE)
- Implements k-means clustering to group similar domains based on their keyphrases
- Categorizes domain clusters for further analysis
