from bs4 import BeautifulSoup
import pandas as pd
import requests
import re

HEADERS = ({'User-Agent':
           'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5'})

file = open("links.txt", "r")

df = pd.DataFrame(columns=['Title', 'Price', 'Link',
                  'Rating', 'Category', 'Image', 'Manufacturer'])

for line in file:
    webpage = requests.get(line, headers=HEADERS)
    soup = BeautifulSoup(webpage.content, "lxml")

    # Extracting the title
    try:
        title = soup.find(
            "span", attrs={"id": 'productTitle'}).get_text().strip()
    except Exception as e:
        print(e)
        with open('error.txt', 'a') as f:
            f.write(line)
        title = ''

    # Extracting the price
    try:
        price = soup.find(
            "span", attrs={"class": 'a-price-whole'}).get_text().strip()
        # print(price)
        price = int(re.sub(r'[^0-9]', '', price))
    except Exception as e:
        print(e)
        with open('error.txt', 'a') as f:
            f.write(line)
        price = ''

    # Extracting the rating
    try:
        rating = soup.find(
            "span", attrs={"data-hook": "rating-out-of-text"}).get_text().strip()
        rating = float(rating.split(" ")[0])
    except Exception as e:
        print(e)
        with open('error.txt', 'a') as f:
            f.write(line)
        rating = ''

    # Extracting the category and subcategory
    try:
        category = []
        for i in soup.find_all("a", attrs={"class": "a-link-normal a-color-tertiary"}):
            category.append(i.get_text().strip())
        category.reverse()
    except Exception as e:
        print(e)
        with open('error.txt', 'a') as f:
            f.write(line)
        category = []

    # Extracting the image
    try:
        img_div = soup.find("div", attrs={"id": "imgTagWrapperId"})
        img = img_div.find("img")['src']
    except Exception as e:
        print(e)
        with open('error.txt', 'a') as f:
            f.write(line)
        img = ''

    # Extracting the manufacturer
    try:
        manufacturer = ''
        feature_list = soup.find(
            "div", attrs={"id": "detailBullets_feature_div"})
        if feature_list is not None:
            for i in feature_list.find_all("li"):
                if i.find("span", attrs={"class": "a-text-bold"}) is not None:
                    if "Manufacturer" in i.find("span", attrs={"class": "a-text-bold"}).get_text().strip():
                        m_str = i.find("span").get_text().strip()
                        m_str = m_str.split(":")[1]
                        manufacturer = re.sub(
                            r'[^a-zA-Z0-9\s]', '', m_str).strip()

        if manufacturer == '':
            table = soup.find(
                "table", attrs={"id": "productDetails_detailBullets_sections1"})
            for i in table.find_all("tr"):
                if "Manufacturer" in i.find("th").get_text().strip():
                    m_str = i.find("td").get_text().strip()
                    manufacturer = re.sub(
                        r'[^a-zA-Z0-9\s]', '', m_str).strip()

        if manufacturer == '':
            table = soup.find(
                    "table", attrs={"id": "productDetails_techSpec_section_1"})
            for i in table.find_all("tr"):
                if "Manufacturer" in i.find("th").get_text().strip():
                    m_str = i.find("td").get_text().strip()
                    manufacturer = re.sub(
                        r'[^a-zA-Z0-9\s]', '', m_str).strip()
        if manufacturer == '':
            raise Exception("Manufacturer not found")

    except Exception as e:
        print(e)
        with open('error.txt', 'a') as f:
            f.write(line)
        manufacturer = ''

    data = {'Title': title, 'Price': price, 'Link': line.strip(
    ), 'Rating': rating, 'Category': category, 'Image': img, 'Manufacturer': manufacturer}
    df = df.append(data, ignore_index=True)

    print(data)

df.to_json('all_products.json', orient='records')
