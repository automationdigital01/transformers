
import requests
from bs4 import BeautifulSoup
import torch
from textsum.summarize import Summarizer
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

#removing ads from text
def is_ad_element(tag):
    # To check if the tag has any of the ad-related classes
    ad_classes = ['ad', 'advertisement', 'sidebar', 'popup']
    return tag.get('class') and any(cls in tag.get('class') for cls in ad_classes)

def relevant_news(url):
    headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"}

    # Remove ad-related elements
    response = requests.get(url,verify=False, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    if soup.body:
        ad_elements = soup.find_all(is_ad_element)
        for element in ad_elements:
            element.extract()

            # Extract relevant information about the company
        relevant_info = soup.find_all('p')  # You can customize this to target specific tags
        # Process and print relevant information
        for info in relevant_info:
            text=' '.join(info.get_text())
            return text
        
    return None    

    

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
        for data in soup(['style', 'script']):# Remove tags
            data.decompose()
 
        # return data by retrieving the tag content
        cleaned_text= ' '.join(soup.stripped_strings)
        #full_text=soup.get_text()
        #cleaned_text = re.sub(r'\s+', ' ', full_text)  # Replace multiple spaces with a single space
        #cleaned_text = re.sub(r'[^\w\s]', '', cleaned_text)  # Remove special characters
        if pattern.search(cleaned_text):
            st.write(URL)
            st.write("Title:", title)
            return cleaned_text
              
    return None  # Return None if there is no body tag


##summarize using T5
def summarize(text):
    tokenizer = AutoTokenizer.from_pretrained('t5-base')
    model = AutoModelWithLMHead.from_pretrained('t5-base', return_dict=True)
    inputs = tokenizer.encode("summarize: " + text,
    return_tensors='pt',
    max_length=512,
    truncation=True)
    summary_ids = model.generate(inputs, max_length=100, min_length=50, length_penalty=5., num_beams=2) 
    summary = tokenizer.decode(summary_ids[0])
    summary=summary.replace('<pad>','')
    summary=summary.replace('</s>','')
    return summary


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
    header_container = st.container()


    with header_container:
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            st.write("")
        with col2:
            st.write("")
            st.markdown("<span style='color: #1E90FF'>Vendor's Credit Analysis</span> "   " <span style='color: #92D293'></span>", unsafe_allow_html=True)
        with col3:
            st.image("logo/USER LOGin.png", width=70)
            st.markdown("<span style='color: #1E90FF'>Welcome User !</span>", unsafe_allow_html=True)

    st.markdown("""
        <style>
            [data-testid=stSidebar] {
                background: linear-gradient(to bottom, #1E90FF, #92D293);
            }
        </style>
    """, unsafe_allow_html=True)



    st.sidebar.image("logo/TECHNIP_ENERGIES_LOGO.png", width=100)

    dataframe_data=[]
    links_list=[]
    #st.title("Credit Analysis of Vendors")
    options=st.sidebar.multiselect('Select the Suppliers',
                          ['Halliburton Company',
                           'Sick AG',
                           'Sofinter S.p.a',
                           'Chiyoda Corporation',
                           'Hamad Bin Khaled Contracting',
                           'Atlas Copco Group',
                           'Burckhardt Compression',
                           'BALFOUR BEATTY PLC',
                           ])
    
    

    # List of URLs to block
    blocked_urls = [
        "https://finance.yahoo.com/news/halliburton-under-scrutiny-7-1m-165827349.html",
        "https://finance.yahoo.com/news/halliburton-company-nyse-hal-passed-100756122.html",
        "https://www.directorstalkinterviews.com/halliburton-company-consensus-buy-rating-and-11.2-upside-potential/4121127874",
        "https://www.benzinga.com/pressreleases/23/09/34752102/2023-2030-pick-to-light-market-analysis-research-report-and-cagr-at-9-98-percent",
        "https://www.marketscreener.com/quote/stock/CHIYODA-CORPORATION-6492047/news/Chiyoda-Awarded-an-Engineering-Procurement-and-Construction-Contract-for-a-1-Barrel-per-Day-synth-44463665/",
        "https://www.marketscreener.com/quote/stock/ATLAS-COPCO-AB-43306890/news/Financial-reporting-days-for-Atlas-Copco-44862651/",
        "https://www.rivieramm.com/news-content-hub/news-content-hub/long-term-service-agreement-smooths-dry-docking-of-four-lng-carriers-77089",
        "https://www.balfourbeatty.com/news/balfour-beatty-communities-appoints-chief-compliance-officer/",
        "https://www.balfourbeatty.com/news/balfour-beatty-2022-full-year-results/"
    ]

    ##summarization using long-T5 summarizer, using huggingface
    #summarizer = pipeline("summarization", "pszemraj/long-t5-tglobal-base-16384-book-summary")

    #sentiment analysis using FinBert
    finbert = BertForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone',num_labels=3)
    tokenizer_sentiment = BertTokenizer.from_pretrained('yiyanghkust/finbert-tone')
    nlp = pipeline("sentiment-analysis", model=finbert, tokenizer=tokenizer_sentiment)

    if st.sidebar.button("Submit"):
        st.write("Selected Suppliers:", options[0])
        links_list= web_links(options[0]) #getting web links using beautiful soup and google news.
        if links_list is None:
            links_list=weblink_news_api(options[0])
     
        for link in links_list:
            if link not in blocked_urls:
                text= web_scraping(link,options[0])
                    #text=relevant_news(link)
                if text:
                    #st.write(text)
                    #result = summarizer(text)
                    # Extract the summary text from the result
                    #summary = result[0]["summary_text"]
                    summary=summarize(text)
                    st.write("Summary:",summary)
                    results = nlp(summary)
                    sentiment=results[0]["label"]
                    st.write("Analysis:", sentiment)                
                                    
                    dataframe_data.append({
                            "Supplier Name" : options[0],
                            "News_link": link, 
                            "News Summary" : summary,
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
