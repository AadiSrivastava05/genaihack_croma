import requests
from bs4 import BeautifulSoup
import re
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("apikey.json") 
firebase_admin.initialize_app(cred)
db = firestore.client()

with open('warehouse_links.txt', "r") as fp:
    links = fp.readlines()

print(f"Total links loaded: {len(links)}")

headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36"
}

# matching_links = [s for s in links if re.search(city, s, re.IGNORECASE)] 
i = 0
for url in links[i:]:
    try:
        print(i)              
        webpage = requests.get(url.strip(), headers=headers).content
        soup = BeautifulSoup(webpage, 'html.parser')
        json_scripts = soup.find_all("script", type='application/ld+json')
        namesAndPrice = [i.split(":")[1] for i in str(json_scripts[:-2][0]).split(',') if "name" in i or "price" in i]
        
        mainInfo = {
            'owner_name': namesAndPrice[0][1:-2].strip(),
            'plot_name': namesAndPrice[1][1:-2].strip(),
            'price': namesAndPrice[3].strip() + " " + namesAndPrice[4][1:-12].strip(),
            'city': namesAndPrice[1][1:-2].strip()[30:]
        }
        
        print(mainInfo)

        # Store data in Firestore
        db.collection('plots').add(mainInfo)
        i += 1
    except IndexError:
        print(f"Data extraction failed for URL: {url}")
        i += 1
    except Exception as e:
        i += 1
        print(f"An error occurred: {e}")

print("Scraping and storing completed.")
