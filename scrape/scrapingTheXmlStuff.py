'''
import re
with open('srp_warehouse_godown.xml', 'r') as fp:
	links = fp.readlines()

stripped = [i.strip() for i in links]
print(len(stripped))

warehouse_links = [_[5:-6] for _ in stripped if re.match("^<loc>.*", _)]

with open("warehouse_links.txt", 'w') as gp:
    gp.write("\n".join(warehouse_links) + "\n")
'''
'''
import requests
from bs4 import BeautifulSoup
import re

fp = open('warehouse_links.txt', "r")
links = fp.readlines()

print(len(links))

headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36"
}

city = input(">>> ")
matching_links = [s for s in links if re.search(city, s)]

for url in matching_links:
	try:
		webpage = requests.get(url.strip(), headers=headers).content
		soup = BeautifulSoup(webpage, 'html.parser')
		json_scripts = soup.find_all("script", type='application/ld+json')
		namesAndPrice = [i.split(":")[1] for i in str(json_scripts[:-2][0]).split(',') if "name" in i or "price" in i]
		mainInfo = [namesAndPrice[0][1:-2].strip(), namesAndPrice[1][1:-2].strip(), namesAndPrice[3].strip() + " " +namesAndPrice[4][1:-12].strip()]
		print(mainInfo)
	except IndexError:
		pass
'''

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

# city = input("Enter the city name: ").strip()
# matching_links = [s for s in links if re.search(city, s, re.IGNORECASE)] 

for url in links:

'''
    try:
        webpage = requests.get(url.strip(), headers=headers).content
        soup = BeautifulSoup(webpage, 'html.parser')
        json_scripts = soup.find_all("script", type='application/ld+json')
        namesAndPrice = [i.split(":")[1] for i in str(json_scripts[:-2][0]).split(',') if "name" in i or "price" in i]
        mainInfo = [namesAndPrice[0][1:-2].strip(), namesAndPrice[1][1:-2].strip(), namesAndPrice[3].strip() + " " +namesAndPrice[4][1:-12].strip()]
        print(mainInfo)
    except IndexError:
        pass
'''

    try:
        webpage = requests.get(url.strip(), headers=headers).content
        soup = BeautifulSoup(webpage, 'html.parser')
        json_scripts = soup.find_all("script", type='application/ld+json')
        namesAndPrice = [i.split(":")[1] for i in str(json_scripts[:-2][0]).split(',') if "name" in i or "price" in i]
        
        mainInfo = {
            'owner_name': namesAndPrice[0][1:-2].strip(),
            'plot_name': namesAndPrice[1][1:-2].strip(),
            'price': namesAndPrice[3].strip() + " " + namesAndPrice[4][1:-12].strip()
        }
        
        print(mainInfo)

        # Store data in Firestore
        # db.collection('plots').add(mainInfo)

    except IndexError:
        print(f"Data extraction failed for URL: {url}")
    except Exception as e:
        print(f"An error occurred: {e}")

print("Scraping and storing completed.")
	
