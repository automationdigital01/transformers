
import requests
from bs4 import BeautifulSoup
from transformers import AutoTokenizer, AutoModelWithLMHead
from transformers import BertTokenizer, BertForSequenceClassification
from transformers import pipeline
import streamlit as st
import pandas as pd
import urllib.parse

##web scraping usin BeautifulSoup
def web_scraping(URL):
    headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"}
    # Here the user agent is for Edge browser on windows 10. You can find your browser user agent from the above given link.
    #URL="https://www.investorsobserver.com/news/stock-update/is-halliburton-company-hal-the-right-choice-in-oil-gas-equipment-services"
    r = requests.get(url=URL,verify=False, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    # Get the whole body tag
    tag = soup.body
    full_text=""
    # Print each string recursively
    for string in tag.strings:
        full_text=full_text+string
    full_text=full_text.replace("\n"," ")    
    return full_text


##summarization using T5 summarizer, using huggingface
def summarize(text):
    tokenizer = AutoTokenizer.from_pretrained('t5-base')
    model = AutoModelWithLMHead.from_pretrained('t5-base', return_dict=True)
    #text=full_text
    inputs = tokenizer.encode("summarize: " + text,
    return_tensors='pt',
    max_length=512,
    truncation=True)
    summary_ids = model.generate(inputs, max_length=80, min_length=50, length_penalty=5., num_beams=2) 
    summary = tokenizer.decode(summary_ids[0])
    summary=summary.replace('<pad>','')
    summary=summary.replace('</s>','')
    return summary

#sentiment analysis using FinBert
def sent_analysis(summary):
    finbert = BertForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone',num_labels=3)
    tokenizer = BertTokenizer.from_pretrained('yiyanghkust/finbert-tone')
    nlp = pipeline("sentiment-analysis", model=finbert, tokenizer=tokenizer)
    sentences = summary
    results = nlp(sentences)
    results=results[0]["label"]
    return results  #LABEL_0: neutral; LABEL_1: positive; LABEL_2: negative

def generate_google_news_url(query):
    encoded_query = urllib.parse.quote(query)
    return f"https://www.google.com/search?q={encoded_query}&tbm=nws"

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
        if link and link.startswith('/url?q='):
            # Extract the actual URL from the Google search results link
            actual_link = link.split('/url?q=')[1].split('&sa=')[0]
            links_list.append(actual_link)
    return links_list


def main():
    dataframe_data=[]
    links_list=[]
    st.title("Credit Worthiness Check")
    options=st.multiselect('Select the Suppliers',
                          ['Icarus SA','Qatar International Cables Trading Co.',
                           'Halliburton Company','Chennai Petroleum Corporation Limited',
                           'Larsen & Toubro Limited'])
    
    if st.button("Submit"):
        st.write("Selected Suppliers:", options[0])
        links_list= web_links(options[0])

        for link in links_list:
            text= web_scraping(link)
            summary=summarize(text)
            sentiment=sent_analysis(summary)
                            
                        
        dataframe_data.append({
                "Supplier Name" : options[0],
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
