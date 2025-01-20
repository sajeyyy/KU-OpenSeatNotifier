import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import logging
import time


# Encryption key management
def getKey():
    key_file = "key.key"
    if os.path.exists(key_file):
        with open(key_file, "rb") as keyfile:
            return keyfile.read()
    key = Fernet.generate_key()
    with open(key_file, "wb") as keyfile:
        keyfile.write(key)
    return key


def loadUserData():
    key = getKey()
    f = Fernet(key)
    with open("userData.enc", "rb") as file:
        encrypted_data = file.read()
    return json.loads(f.decrypt(encrypted_data).decode())


def calculate_search_term():
    baseYear = 2024
    baseTerm = 4246
    currentYear = datetime.now().year
    currentMonth = datetime.now().month
    termOffset = (currentYear - baseYear) * 3
    if currentMonth <= 4:
        termOffset += 2
    elif currentMonth <= 7:
        termOffset += 0
    else:
        termOffset += 1
    return baseTerm + termOffset


def checkClass():
    # Send the POST request
    response = requests.post(apiURL, data=payload)

    if response.status_code != 200:
        print("Error: Unable to fetch class data")
        return

    # Parse the HTML response
    soup = BeautifulSoup(response.text, "html.parser")

    try:
        # Look for closed or open seat indicators
        seat_status = soup.find("span", {"class": ["avail_closed", "avail_open"]})
        if seat_status:
            seat_text = seat_status.text.strip()
            print(f"\nSeat Status: {seat_text}")

            # Check if the seat is available
            if "Full" not in seat_text:
                sendEmail()
                openClass = True
            else:
                print("Class is full. No seats available.")
        else:
            print("No seat status found in the response.")
    except Exception as e:
        print(f"Error parsing enrollment data: {e}")



def sendEmail():
    subject = "Class Seat Available!"
    class_name = payload["classesSearchText"]  # Get the class name from the payload
    body = f"A seat has opened in the class: {class_name}!\n\nEnroll in the class here: https://sa.ku.edu/"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = email
    msg["To"] = TO_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(email, emailPassword)
        server.sendmail(email, TO_email, msg.as_string())
        print("Notification email sent!")



# Main program
userData = loadUserData()
payload = {
    "classesSearchText": userData["classesSearchText"],
    "searchCareer": "UndergraduateGraduate",
    "searchTerm": str(calculate_search_term()),
    "searchClosed": "false",
    "searchCourseNumberMin": "001",
    "searchCourseNumberMax": "999",
    "searchIncludeExcludeDays": "include",
}

openClass = False
while not openClass:
    checkClass()
    if openClass:
        break
    print("Checked. Waiting for 7 minutes...")
    time.sleep(7 * 60)
