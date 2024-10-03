import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import re
from supabase import create_client, Client

API_KEY = ""                                     # Enter your API key here
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

def generate_email_gemini(discount, product, msp, instruction, words):
    response = model.generate_content(f'''
                                      1) You are supposed to generate a mass email for a product/products of a company
                                      2) It should be attractive and should make the email recipient want to click on it.
                                      3) Here are the contraints: Product_Name = {product}, Minumum_selling_price = {msp}, Discount = {discount}.
                                      4) Here are some additional instructions to follow: {instruction}.
                                      5) Word limit for the email content part is {words}.
                                      5) The output should be such that the first line is, 'Subject: ' followed by the subject, and then the email content following it. No words should be bold in the output.
                                      6) There should not be any placeholders in the output for links etc. unless specified in the additional instructions.
                                      ''')

    output2 = response.text

    return output2

def email_generation():
    product = input("Product: ")
    msp = input("msp: ")
    discount = input("discount: ")
    words = input("Word limit: ")
    instructions = input("instructions: ")
    if product=='NULL':
        product = "No specific product"
    if msp=='NULL':
        msp = "DONT MENTION MSP"
    if discount=='NULL':
        discount = "DONT MENTION DISCOUNT"
    if instructions=='NULL':
        instructions = "NO ADDITIONAL INSTRUCTIONS"
    
    return generate_email_gemini(discount, product, msp, instructions, words)

print(email_generation())
