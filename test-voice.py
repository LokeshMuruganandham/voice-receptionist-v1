import pyttsx3

engine = pyttsx3.init()

engine.setProperty("rate", 150)

engine.say("Hello, this is the Pawz Styling receptionist. How can I help you?")
engine.runAndWait()