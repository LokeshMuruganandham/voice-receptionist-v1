import os
import json
import re
import speech_recognition as sr
import pyttsx3
from openpyxl import load_workbook
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

recognizer = sr.Recognizer()

# Text-to-speech
def speak(text):
    engine = pyttsx3.init()
    engine.setProperty("rate", 150)
    engine.say(text)
    engine.runAndWait()
    engine.stop()


# Excel file
EXCEL_FILE = "appointments-v1.xlsx"


# Save appointment to Excel
def save_appointment(appointment):
    workbook = load_workbook(EXCEL_FILE)
    sheet = workbook.active

    sheet.append([
        appointment["customer_name"],
        appointment["pet_name"],
        appointment["breed"],
        appointment["whatsapp"],
        appointment["appointment_date"],
        appointment["appointment_time"]
    ])

    workbook.save(EXCEL_FILE)

    print("\nAppointment saved to Excel successfully!")


SYSTEM_PROMPT = """
You are a friendly AI receptionist for Pawz Styling, a pet grooming business.

Have a natural conversation with the customer.

Your job is to help the customer book a pet grooming appointment.

You need to collect these six pieces of information:

1. customer_name
2. pet_name
3. breed
4. whatsapp
5. appointment_date
6. appointment_time

Do NOT ask for all information at once.

Ask naturally for one missing piece of information at a time.

If the customer gives multiple pieces of information in one sentence,
remember all of them.

Do not ask for information that the customer has already provided.

When all six pieces of information have been collected, confirm the
appointment details with the customer.

IMPORTANT:
At the END of every response, output a JSON object on a separate line.

The JSON must have exactly this structure:

{
    "customer_name": "",
    "pet_name": "",
    "breed": "",
    "whatsapp": "",
    "appointment_date": "",
    "appointment_time": "",
    "appointment_complete": false
}

Put the information collected so far into the JSON.

If a field has not been provided yet, leave it as an empty string.

Only set "appointment_complete" to true when ALL six pieces of information
have been collected and the customer has confirmed the appointment.

The normal receptionist message must come BEFORE the JSON.

Keep the receptionist message short and natural because it will be spoken aloud.
"""


def extract_json(text):
    """
    Find the JSON object at the end of Gemini's response.
    """
    matches = re.findall(r'\{[\s\S]*\}', text)

    if not matches:
        return None

    try:
        return json.loads(matches[-1])
    except json.JSONDecodeError:
        return None


# def clean_response(text):
    """
    Remove the JSON from the response before speaking it.
    """
    matches = re.findall(r'\{[\s\S]*\}', text)

    if matches:
        text = text.replace(matches[-1], "")

    return text.strip()

def clean_response(text):
    """
    Remove JSON and Markdown code fences before sending
    the response to text-to-speech.
    """

    # Remove JSON code block
    text = re.sub(
        r'```json[\s\S]*?```',
        '',
        text,
        flags=re.IGNORECASE
    )

    # Remove any remaining JSON object
    text = re.sub(
        r'\{[\s\S]*\}',
        '',
        text
    )

    # Remove leftover Markdown code fences
    text = text.replace("```json", "")
    text = text.replace("```", "")

    return text.strip()

print("Voice Receptionist V1")
print("---------------------")
print("Starting Gemini...")


# Initial greeting
response = client.interactions.create(
    model="gemini-3.6-flash",
    input=SYSTEM_PROMPT + """

Start the conversation.

Greet the customer naturally and ask how you can help them.
"""
)

raw_response = response.output_text

data = extract_json(raw_response)
reply = clean_response(raw_response)

print("Receptionist:", reply)
speak(reply)

previous_id = response.id


while True:

    print("\nListening...")

    try:

        with sr.Microphone() as source:

            recognizer.adjust_for_ambient_noise(
                source,
                duration=0.5
            )

            audio = recognizer.listen(source)

        print("Processing...")

        user_text = recognizer.recognize_google(audio)

        print("You:", user_text)


        # Exit phrases
        exit_phrases = [
            "exit",
            "quit",
            "goodbye",
            "bye",
            "hang up",
            "end the call"
        ]

        if any(
            phrase in user_text.lower()
            for phrase in exit_phrases
        ):

            print(
                "Receptionist: Thank you! Have a great day."
            )

            speak(
                "Thank you! Have a great day."
            )

            break


        # Send conversation to Gemini
        response = client.interactions.create(

            model="gemini-3.6-flash",

            input=user_text,

            previous_interaction_id=previous_id
        )


        raw_response = response.output_text

        print("\nGemini raw response:")
        print(raw_response)


        # Extract structured appointment data
        data = extract_json(raw_response)

        # Remove JSON before speaking
        reply = clean_response(raw_response)


        print("\nReceptionist:", reply)

        speak(reply)


        previous_id = response.id


        # Check whether appointment is complete
        if data and data.get("appointment_complete") is True:

            print("\nAppointment information collected:")
            print(json.dumps(data, indent=4))


            # Save to Excel
            save_appointment(data)


            speak(
                "Your appointment has been booked successfully. "
                "Thank you for choosing Pawz Styling. Have a great day."
            )

            break


    except sr.UnknownValueError:

        print(
            "Sorry, I couldn't understand what you said."
        )


    except sr.RequestError as e:

        print(
            "Speech recognition error:",
            e
        )


    except Exception as e:

        print(
            "Error:",
            e
        )

        break