from bs4 import BeautifulSoup
import pandas as pd
import requests

HEADERS = ({'User-Agent':
           'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5'})

file = open("links.txt", "r")

df = pd.DataFrame(columns=['Title', 'Price', 'Link', 'Rating', 'Category', 'Image', 'Manufacturer'])

for line in file:
    webpage = requests.get(line, headers=HEADERS)
    soup = BeautifulSoup(webpage.content, "lxml")

    # Extracting the title
    try:
        title = soup.find("span", attrs={"id": 'productTitle'}).get_text().strip()
    except:
        title = ''

    # Extracting the price
    try:
        price = soup.find("span", attrs={"class": 'a-price-whole'}).get_text().strip()
        price = int(price.replace(',', ''))
    except:
        price = ''
        
    # Extracting the rating
    try:
        rating = soup.find("span", attrs={"data-hook": "rating-out-of-text"}).get_text().strip()
        rating = float(rating.split(" ")[0])
    except:
        rating = ''
    
    # Extracting the category and subcategory
    try:
        category = []
        for i in soup.find_all("a", attrs={"class": "a-link-normal a-color-tertiary"}):
            category.append(i.get_text().strip())
        category.reverse()
    except:
        category = []
        
    # Extracting the image
    try:
        img_div = soup.find("div", attrs={"id": "imgTagWrapperId"})
        img = img_div.find("img")['src']
    except:
        img = ''
    
    # Extracting the manufacturer
    try:
        feature_list = soup.find("div", attrs={"id": "detailBullets_feature_div"})
        for i in feature_list.find_all("li"):
            if "Manufacturer" in i.find("span", attrs={"class": "a-text-bold"}).get_text().strip():
                m_list = i.find("span").get_text().strip().split(" ")
                manufacturer = m_list[-1].lower()
    except:
        manufacturer = ''
    
    df = df.append({'Title': title, 'Price': price, 'Link': line.strip(), 'Rating': rating, 'Category': category, 'Image': img, 'Manufacturer': manufacturer}, ignore_index=True)
    
    print(df.tail(1))
    
df.to_json('data.json', orient='records')