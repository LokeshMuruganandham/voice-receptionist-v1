from openpyxl import load_workbook
from pathlib import Path

# Excel file
file_path = Path("appointments-v1.xlsx")

# Dummy appointment data
appointment = {
    "Customer Name": "Rahul",
    "Pet Name": "Bruno",
    "Breed": "Golden Retriever",
    "WhatsApp": "9876543210",
    "Appointment Date": "2026-09-05",
    "Appointment Time": "17:00"
}

# Open existing Excel file
workbook = load_workbook(file_path)
sheet = workbook.active

# Add the appointment as a new row
sheet.append([
    appointment["Customer Name"],
    appointment["Pet Name"],
    appointment["Breed"],
    appointment["WhatsApp"],
    appointment["Appointment Date"],
    appointment["Appointment Time"]
])

# Save
workbook.save(file_path)

print("Appointment successfully added!")