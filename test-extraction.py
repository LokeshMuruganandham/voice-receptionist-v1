import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

conversation = """
Customer: Hi, I want to book an appointment for my dog.

Receptionist: Sure! I'd be happy to help. May I have your name?

Customer: My name is Rahul.

Receptionist: What's your pet's name?

Customer: Bruno.

Receptionist: And what breed is Bruno?

Customer: He's a Golden Retriever.

Receptionist: Could I have your WhatsApp number?

Customer: 9876543210.

Receptionist: When would you like the appointment?

Customer: Tomorrow at 5 PM.
"""

prompt = f"""
You are an appointment data extraction system.

Extract the appointment information from the conversation below.

Return ONLY valid JSON in exactly this structure:

{{
    "customer_name": "",
    "pet_name": "",
    "breed": "",
    "whatsapp": "",
    "appointment_date": "",
    "appointment_time": ""
}}

If information is missing, leave that field empty.

Conversation:
{conversation}
"""

response = client.interactions.create(
    model="gemini-3.6-flash",
    input=prompt
)

print("Gemini response:")
print(response.output_text)