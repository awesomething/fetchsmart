import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content("Hello, test!")
    print("✅ Google AI API working!")
    print(f"Response: {response.text[:100]}...")
except Exception as e:
    print(f"❌ Google AI API failed: {e}")