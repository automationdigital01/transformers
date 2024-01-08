#extract web links using beautiful soup
import streamlit as st
import requests
from bs4 import BeautifulSoup
import datetime
import urllib3, urllib
from urllib.parse import urlparse

urllib3.disable_warnings()
headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"}

import torch
from transformers import AutoTokenizer, AutoModelWithLMHead


# Function to convert search query to Google News search URL
def generate_google_news_url(query):
    # get the current date
    today = datetime.date.today()

    # format the date as required by Google News URL
    date = today.strftime("%m/%d/%Y")
    encoded_query = urllib.parse.quote(query)
    return f"https://www.google.com/search?q={query}&tbm=nws&hl=en&gl=US&as_drrb=b&authuser=0&source=lnt&tbs=cdr%3A1%2Ccd_min%3A{date}%2Ccd_max%3A{date}&tbm=nws"


# Function to filter out unwanted links
def filter_links(link):
    unwanted_domains = ['support.google.com', 'accounts.google.com']
    for domain in unwanted_domains:
        if domain in link:
            return False
    return True

def remove_invalid_urls(url_lists):
    valid_urls= [url for url in url_lists if urlparse(url).scheme]
    return valid_urls

##summarize using T5
@st.cache
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


def main():
    header_container = st.container()
    with header_container:
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            st.write("")
        with col2:
            st.write("")
            st.markdown("<span style='color: #1E90FF'>Webscrapping</span> "   " <span style='color: #92D293'></span>", unsafe_allow_html=True)
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

    
   
    #st.title("Scouting")


    blocked_urls=["https://carbonherald.com/the-price-of-aker-carbon-capture-stock-jumps-27/","https://www.bannergraphic.com/story/3023439.html"]
    latest_links=[]
    links_list = []
    
    st.write("Peer News-")
    keywords=["Aker Carbon Capture","JGC","Chiyoda ","McDermott","Petrofac","Saipem"]
                                    
    
    

    links_list = []

    for keyword in keywords:
        st.write(f"~{keyword}:")
    #company_name="Eastman"
        search_query = f"{keyword} news"
        #news_url = next(search(search_query, tld="com", num=1, stop=1, pause=2))[0]
        google_news_url = generate_google_news_url(search_query)
        data = requests.get(google_news_url)
        soup = BeautifulSoup(data.text, 'html.parser')

    
        for links in soup.find_all('a'):
            link = links.get('href')
            if link and link.startswith('/url?q=') and filter_links(link):
                # Extract the actual URL from the Google search results link
                actual_link = link.split('/url?q=')[1].split('&sa=')[0]
                links_list.append(actual_link)
                valid_urls=remove_invalid_urls(links_list)
                
        latest_links.append(valid_urls[:5])
        
        #print(f"links for {keyword} is :", latest_links)
        for link in valid_urls[:5]:
            if link not in blocked_urls:
                
                r = requests.get(url=link,verify=False, headers=headers, timeout=10)
                soup = BeautifulSoup(r.text, "html.parser")
                # Identify HTML tags or classes that contain the main article content
                main_content_tags = soup.find_all('p')  # Adjust based on your HTML structure

                # Extract and print the main article content
                main_article = "\n".join([tag.get_text() for tag in main_content_tags])

                title=soup.title.string
                text = soup.get_text()
                #print("Title:", title)
                descriptions = [item['content'] for item in soup.select('[name=Description][content], [name=description][content]')]
                for desc in descriptions:
                    clean_desc=desc.replace('['," ").replace(']'," ")
                #print(descriptions)
                #summary=summarize(main_article)
                #print("summary of the text:",summary)
                if title:
                    st.write(f"- {title}. {clean_desc}. for more information check {link} ")
                else:
                    st.write(f"-  {clean_desc}. for more information check {link} ")
        links_list=[]
            
        
        
if __name__ == "__main__":
    
    main()#extract web links using beautiful soup
import streamlit as st
import requests
from bs4 import BeautifulSoup

import urllib3, urllib
from urllib.parse import urlparse

urllib3.disable_warnings()
headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"}

import torch
from transformers import AutoTokenizer, AutoModelWithLMHead


# Function to convert search query to Google News search URL
def generate_google_news_url(query):
    encoded_query = urllib.parse.quote(query)
    return f"https://www.google.com/search?q={encoded_query}&tbm=nws"


# Function to filter out unwanted links
def filter_links(link):
    unwanted_domains = ['support.google.com', 'accounts.google.com']
    for domain in unwanted_domains:
        if domain in link:
            return False
    return True

def remove_invalid_urls(url_lists):
    valid_urls= [url for url in url_lists if urlparse(url).scheme]
    return valid_urls

##summarize using T5
@st.cache
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


def main():
    header_container = st.container()
    with header_container:
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            st.write("")
        with col2:
            st.write("")
            st.markdown("<span style='color: #1E90FF'>Webscrapping</span> "   " <span style='color: #92D293'></span>", unsafe_allow_html=True)
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

    
   
    #st.title("Scouting")


    option=st.sidebar.multiselect('Select the company',
                                   ['Agilyx',
                                    'Brightmark',
                                    'Carbios',
                                    'loop industries',
                                    'Eastman'                                                                                                 
                                    ])
                                
    #keywords to search
    keywords_to_search=['recycling','textile']
    #keywords_to_search = st.sidebar.text_input('Enter the keyword')
    #st.write("Keyword given:",keywords_to_search) 
    def words_in_string(word_list, a_string):
        return set(word_list).intersection(a_string.split())

    links_list = []

    if option and keywords_to_search and st.sidebar.button("Submit"):
        st.write("Selected Company:", option[0])
        # Specify the search query with the company name
        # Generate the Google News search URL using the function
        google_news_url = generate_google_news_url(f"{option[0]} news")

        # Fetch the Google News search results page
        data = requests.get(google_news_url)
        soup = BeautifulSoup(data.text, 'html.parser')
        

        for links in soup.find_all('a'):
            link = links.get('href')
            if link and link.startswith('/url?q=') and filter_links(link):
                # Extract the actual URL from the Google search results link
                actual_link = link.split('/url?q=')[1].split('&sa=')[0]
                links_list.append(actual_link)
                #print(links_list)

                valid_urls=remove_invalid_urls(links_list)
                

        #st.write(f"Total {len(valid_urls)} news article links for {option[0]}.")
        for URL in valid_urls:
            r = requests.get(url=URL,verify=False, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            # Identify HTML tags or classes that contain the main article content
            main_content_tags = soup.find_all('p')  # Adjust based on your HTML structure

            # Extract and print the main article content
            main_article = "\n".join([tag.get_text() for tag in main_content_tags])
            title_tag=soup.find('title')
            if title_tag:
                title=title_tag.text.strip()                
         
            #text = soup.get_text()
            if words_in_string(keywords_to_search, main_article) or words_in_string(keywords_to_search, title):
                st.write(URL)
                #st.write('One or more keywords found!')
                st.write("Title :",title)
                #descriptions=summary(text)
                #descriptions = [item['content'] for item in soup.select('[name=Description][content], [name=description][content]')]
                #if descriptions:
                  #  st.write("Description :", descriptions[0])
                summary=summarize(main_article)
                st.write("summary of the text:",summary)
            #else:
                #st.write("No Keywords matched")

        
        
        
if __name__ == "__main__":
    
    main()
