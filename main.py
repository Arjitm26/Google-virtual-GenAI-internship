from dotenv import load_dotenv
import streamlit as st 
from streamlit_extras import add_vertical_space as avs 
import google.generativeai as genai
import os 
import PyPDF2 
from PIL import Image
import json


load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")


if api_key:
    genai.configure(api_key=api_key)
else:
    raise ValueError("API key not found. Ensure GOOGLE_API_KEY is set in your .env file.")

model = genai.GenerativeModel('gemini-pro')

def gen_response(text):
    response = model.generate_content(text)
    return response.text

def pdfreader(file):
    reader = PyPDF2.PdfReader(file)
    text = " "
    for num in range(len(reader.pages)):
        page = reader.pages[num]
        text += str(page.extract_text())
    return text   

with open('cv.json','r') as file:
    resume = json.load(file)

def input(user_query):
    context = f"""
    You are a chatbot designed to answer questions about my resume. Here are the details:
    {json.dumps(resume, indent=2)}
    """
    prompt = f"{context}\n\nUser: {user_query}\nChatbot:"
    response = model.generate_content([prompt])
    return response.text


print(input("Whats his education ?"))
