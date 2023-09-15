
import requests
from bs4 import BeautifulSoup
import torch
from transformers import AutoTokenizer, AutoModelWithLMHead
from transformers import BertTokenizer, BertForSequenceClassification
from transformers import pipeline
import streamlit as st
import pandas as pd
import urllib.parse
import re
import urllib3

urllib3.disable_warnings()


# Function to convert search query to Google News search URL
def generate_google_news_url(query):
    encoded_query = urllib.parse.quote(query)
    return f"https://www.google.com/search?q={encoded_query}&tbm=nws"


##web scraping usin BeautifulSoup
def web_scraping(URL,company_name):
    headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"}
    # Here the user agent is for Edge browser on windows 10. You can find your browser user agent from the above given link.
    #URL="https://www.investorsobserver.com/news/stock-update/is-halliburton-company-hal-the-right-choice-in-oil-gas-equipment-services"
    r = requests.get(url=URL,verify=False, headers=headers)
    
    soup = BeautifulSoup(r.text, "html.parser")
    pattern = re.compile(rf'\b{re.escape(company_name)}\b', re.IGNORECASE)
    if soup.body:
        title=soup.title.text
        
        full_text=soup.get_text()
        if pattern.search(full_text):
            st.write(URL)
            st.write("Title:", title)
            return full_text
              
    return None  # Return None if there is no body tag


##summarization using T5 summarizer, using huggingface
def summarize(text):
    tokenizer_summarize = AutoTokenizer.from_pretrained('t5-base')
    model_summarize = AutoModelWithLMHead.from_pretrained('t5-base', return_dict=True)
    #text=full_text
    if text:
        inputs = tokenizer_summarize.encode("summarize: " + text,
        return_tensors='pt',
        max_length=512,
        truncation=True)
        summary_ids = model_summarize.generate(inputs, max_length=150, min_length=80, length_penalty=5., num_beams=2) 
        summary = tokenizer_summarize.decode(summary_ids[0])
        summary=summary.replace('<pad>','')
        summary=summary.replace('</s>','')
        return summary
    else:
        return None #if text is none

#sentiment analysis using FinBert
def sent_analysis(summary):
    finbert = BertForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone',num_labels=3)
    tokenizer_sentiment = BertTokenizer.from_pretrained('yiyanghkust/finbert-tone')
    if summary:
        nlp = pipeline("sentiment-analysis", model=finbert, tokenizer=tokenizer_sentiment)
        sentences = summary
        results = nlp(sentences)
        results=results[0]["label"]
        return results  #LABEL_0: neutral; LABEL_1: positive; LABEL_2: negative

#get weblinks using news api
def weblink_news_api(company_name):
    # Replace 'YOUR_API_KEY' with your actual NewsAPI key
    api_key = '4e086fbfe2bc48eea914d5b05a79d498'
    proxy = None  # Set to None if you don't want to use a proxy

    try:
        # Create the URL for the NewsAPI request
        url = f'https://newsapi.org/v2/everything?q={company_name}&apiKey={api_key}&pageSize=10'

        # Send a GET request to NewsAPI with SSL verification disabled
        response = requests.get(url, verify=False)

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])

            # Create a set to store the unique websites that mention the company name
            company_websites = set()

            # Iterate through the articles and extract the source URLs
            for article in articles:
                source_url = article.get('url')
                

                # Check if the source URL is not None and not already in the set
                if source_url and source_url not in company_websites:
                    company_websites.add(source_url)

            return list(company_websites)
        else:
            print(f'Error: Unable to fetch news for {company_name}. Status code: {response.status_code}')
            return None
    except requests.exceptions.RequestException as e:
        print(f'Error: An error occurred during the request: {str(e)}')
        return None


# Function to filter out unwanted links
def filter_links(link):
    unwanted_domains = ['support.google.com', 'accounts.google.com']
    for domain in unwanted_domains:
        if domain in link:
            return False
    return True

def web_links(supplier):
    # Specify the search query with the company name
    search_query = f"{supplier} news"  # Modify this as needed

    # Generate the Google News search URL using the function
    google_news_url = generate_google_news_url(search_query)

    # Fetch the Google News search results page
    data = requests.get(google_news_url)
    soup = BeautifulSoup(data.text, 'html.parser')
    links_list = []

    for links in soup.find_all('a'):
        link = links.get('href')
        if link and link.startswith('/url?q=') and filter_links(link):
            # Extract the actual URL from the Google search results link
            actual_link = link.split('/url?q=')[1].split('&sa=')[0]
            links_list.append(actual_link)
    return links_list


def main():
    dataframe_data=[]
    links_list=[]
    st.title("Credit Analysis of Vendors")
    options=st.multiselect('Select the Suppliers',
                         ['Halliburton Company',
                           'Chennai Petroleum Corporation Limited',
                           'Sick AG',
                           'Godrej & Boyce Manufacturing Company Limited',
                           'Sofinter SpA',
                           'Chiyoda Corporation',
                           'Hamad Bin Khaled Contracting'              
                        
                           
                           
                           ])
    
    if st.button("Submit"):
        st.write("Selected Suppliers:", options[0])
        links_list= web_links(options[0]) #getting web links using beautiful soup and google news.
        if links_list is None:
            links_list=weblink_news_api(options[0])

        for link in links_list:
            text= web_scraping(link,options[0])
            if text:
                
                #st.write(text)
                summary=summarize(text)
                st.write("Summary:",summary)
                sentiment=sent_analysis(summary)
                st.write("Analysis:", sentiment)                
                            
                dataframe_data.append({
                        "Supplier Name" : options[0],
                        "News_link": link, 
                        "News" : summary,
                        "Result" : sentiment
                        })

        df= pd.DataFrame(dataframe_data)
        st.dataframe(df)
        csv = df.to_csv().encode('utf-8')

        st.download_button(label="Download data as CSV",
                            data=csv,
                            file_name='supplier_df.csv',
                            mime='text/csv',)

if __name__ == "__main__":
    main()
