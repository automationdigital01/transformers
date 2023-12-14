#extract web links using beautiful soup
import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib3, urllib
from urllib.parse import urlparse

urllib3.disable_warnings()
headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"}

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


def main():
    header_container = st.container()
    with header_container:
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            st.write("")
        with col2:
            st.write("")
            st.markdown("<span style='color: #1E90FF'>Scouting</span> "   " <span style='color: #92D293'></span>", unsafe_allow_html=True)
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


    option=st.sidebar.multiselect('Select the Company',
                                   ['Agilyx',
                                    'BASF',
                                    'Brightmark',
                                    'Carbios',
                                    'Citeo',
                                    'Eastman',
                                    'Enerkem',
                                    'Gr3n',
                                    'INEOS',
                                    'Styrolution',
                                    'LyondellBasell',
                                    'Plastic Energy',
                                    'Pyrowave',
                                    'Recycling Technologies',
                                    'SABIC',
                                    'chemical recycling industry',
                                    'textil'
                                    ])
                                
    #keywords to search
    keywords_to_search=[
        'Hydrocarbons',
        'Mass balance',
        'Polymerization',
        'Pyrolysis',
        'activity report',    
        'Methanolysis',
        'Catalyst',
        'Ethylene glycol',
        'Zinc acetate',
        'Manganese/antimony acetate',
        'BHET',
        'DMT',
        'Recycled content',
        'Virgin material',
        'Feedstock',
        'Resin',
        'Cracking',
        'Post-consumer waste',
        'Circular economy',
        'Carbon footprint',
        'Energy efficiency',
        'Environmental externalities',
        'Steam cracker',
        'Chemical recycling',
        'Mechanical recycling',
        'Polyester',
        'PET',
        'Fair Trade agriculture',
        'Electricity marketing',
        'International Sustainability and Carbon Certification (ISCC)',
        'RedCert',
        'rEG',
        'Catalytically active',
        'Reactor concept',
        'Hydrocarbons',
        'Monomers',
        'Solvent-based dissolution',
        'Polymers',
        'Depolymerization',
        'Repolymerization',
        'Re-monomerization',
        'Building block processing plant',
        'Compounding',
        'Advanced chemical recycling',
        'Thermal conversion',
        'PTA',
        'Polyolefins',
        'Pyrolysis',
        'Methanolysis',
        'Ethylene glycol',
        'Zinc acetate',
        'Manganese/antimony acetate',
        'Superheated methanol vapor'
        ]

    morekeywords_to_search=[
        'Recycled content',
        'Virgin material',
        'Post-consumer waste',
        'Steam cracker',
        'Carbon footprint',
        'Energy efficiency',
        'Plastic pollution',
        'Rectifier',
        'Dissolver',
        'Transesterification',
        'Chemical recycling',
        'Mechanical recycling',
        'Circular economy',
        'Value chain',
        'Innovation',
        'Sustainability',
        'Carbon certification',
        'Recycling',
        'Upcycling',
        'Downcycling',
        'Plastic recycling',
        'Hazardous waste recycling',
        'Circular economy',
        'Renewable energy',
        'Carbon footprint',
        'Zero waste',
        'Sustainable agriculture',
        'Eco-friendly',
        'Green energy',
        'Biodiversity',
        'Climate change'
        'Sustainable development',
        'Energy efficiency',
        'Carbon offsetting',
        'Sustainable transportation',
        'Greenhouse gas emissions',
        'Sustainable packaging',
        'Fair trade',
        'Organic farming',
        'Water conservation',
        'Sustainable forestry',
        'Life cycle assessment'
        ]

    def words_in_string(word_list, a_string):
        return set(word_list).intersection(a_string.split())

    links_list = []

    if option and st.sidebar.button("Submit"):
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

        
        for URL in valid_urls:
            st.write(URL)
            r = requests.get(url=URL,verify=False, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            #title=soup.find('title')
            #st.write(title)
            text = soup.get_text()
            if words_in_string(keywords_to_search, text) or words_in_string(morekeywords_to_search, text):
                
                st.write('One or more keywords found!')
                #st.write(URL)
                #descriptions=summary(text)
                descriptions = [item['content'] for item in soup.select('[name=Description][content], [name=description][content]')]
                if descriptions:
                    st.write("Description:", descriptions[0])

        
        
        
if __name__ == "__main__":
    
    main()

