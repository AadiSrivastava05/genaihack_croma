import os
import pandas as pd
import re

# Path to the folder containing the .txt files
folder_path = 'C:/Users/Marsman/genaihack_croma-main/getting_data_set/promotional_emails'

# Initialize an empty list to store file contents and file names
data = []

# Loop through all .txt files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith('.txt'):
        file_path = os.path.join(folder_path, filename)
        
        # Open the file and read its contents
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            br = 0
            for i in range(len(content)):
                if content[i]=='\n':
                    br = i
                    break
            content = content[br+1:]
            content+"$$"
            discount_present = 'NULL'
            product_present = 'NULL'
            MSP_present = 'NULL'
            if re.match('[PRODUCT_NAME]', content):
                product_present = 'PRESENT'
            if re.match('[DISCOUNT]', content):
                discount_present = 'PRESENT'
            if re.match('[MSP]', content):
                MSP_present = 'PRESENT'
            

        
        # Append the content and the file name (without extension) to the data list
        data.append({'disount': discount_present, 'product': product_present, 'msp': MSP_present, 'text': content})

# Create a DataFrame from the data list
df = pd.DataFrame(data)

# Save the DataFrame to a CSV file (optional)
df.to_csv('email_dataset.csv', index=False)

# Show the first few rows of the DataFrame
print(df.head())
