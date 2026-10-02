import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

print("Testing Gemini...")

response = client.interactions.create(
    model="gemini-3.6-flash",
    input="Reply with exactly: Gemini is working."
)

print(response.output_text)