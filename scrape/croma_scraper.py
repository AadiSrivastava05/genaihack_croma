from bs4 import BeautifulSoup
import pandas as pd

# Open and read the HTML file
with open('/Users/mahakmehra/Product Recommendation Chatbot/phonewear.html', 'r') as f:
    content = f.read()

# Parse the HTML with BeautifulSoup
soup = BeautifulSoup(content, 'html.parser')

# Prepare lists to store data
product_names = []
product_prices = []
product_links = []

# Find all divs with the specific class
divs = soup.find_all('div', class_='cp-product typ-plp plp-srp-typ')

# Iterate through all the product divs
for div in divs:
    # Try to find the product name and link
    try:
        name_div = div.find('div', class_='plp-prod-title-rating-cont')
        product_name = name_div.find('a').text.strip() if name_div else " "
        product_link = name_div.find('a')['href'] if name_div else " "
    except:
        product_name = " "
        product_link = " "

    # Try to find the product price
    try:
        price_span = div.find('span', class_='amount plp-srp-new-amount')
        product_price = price_span.text.strip() if price_span else " "
    except:
        product_price = " "

    # Append the results to the lists
    product_names.append(product_name)
    product_prices.append(product_price)
    product_links.append(product_link)

# Create a DataFrame to store the data
df = pd.DataFrame({
    'Product Name': product_names,
    'Product Price': product_prices,
    'Product Link': product_links
})
df.to_excel('/Users/mahakmehra/Documents/product_data.xlsx', index=False)


print("Data successfully written to product_data.xlsx")
