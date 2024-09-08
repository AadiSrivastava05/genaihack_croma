import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client

url: str = "https://ajkgqdvxmueqxtuvcjho.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFqa2dxZHZ4bXVlcXh0dXZjamhvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjU1NTYyOTcsImV4cCI6MjA0MTEzMjI5N30.cwmfECvEYqu6FZXRFqcTw1zD-H6NoHkG_etfqPZ-hDw"

supabase: Client = create_client(url, key)

fp = open('warehouse_links.txt', "r")
links = fp.readlines()

print(f"Total links: {len(links)}")

headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36"
}
i = 34000
for url in links[i:]:
    try:
        try:
            webpage = requests.get(url.strip(), headers=headers).content
            soup = BeautifulSoup(webpage, 'html.parser')
            json_scripts = soup.find_all("script", type='application/ld+json')
            namesAndPrice = [i.split(":")[1] for i in str(json_scripts[:-2][0]).split(',') if "name" in i or "price" in i]
            try:
                mainInfo = {'owner_name': namesAndPrice[0][1:-2].strip(), 'city': namesAndPrice[1][1:-2].strip()[30:], 'price': int(namesAndPrice[3].strip()), 'link': url.strip()}
                print(mainInfo, i)
                response = supabase.table('PlotData').insert(mainInfo).execute()
                i += 1
            except ValueError:
                i += 1
                pass
        except IndexError:
            print(f"Error processing {url.strip()}")
            i += 1
            pass
    except Exception as E:
        print(f"Some failure, {E}")
        pass