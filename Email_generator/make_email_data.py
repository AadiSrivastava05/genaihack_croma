import os
import pandas as pd
import re

folder_path = '' # Path to the folder containing the .txt files foe emails

data = []

for filename in os.listdir(folder_path):
    if filename.endswith('.txt'):
        file_path = os.path.join(folder_path, filename)
        
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
            

        
        data.append({'disount': discount_present, 'product': product_present, 'msp': MSP_present, 'text': content})

df = pd.DataFrame(data)

df.to_csv('email_dataset.csv', index=False)

print(df.head())
