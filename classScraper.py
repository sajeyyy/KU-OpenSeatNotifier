import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import logging
import time

openClass = False;

# KU's Class Search API URL
apiURL = "https://classes.ku.edu/Classes/CourseSearch.action"

# POST Request Payload (NEEDS TO BE ADJUSTABLE)
payload = {
    "classesSearchText": "EECS 443",
    "searchCareer": "UndergraduateGraduate",
    "searchTerm": "4252",  # Spring 2025 term
    "searchClosed": "false",
    "searchCourseNumberMin": "001",
    "searchCourseNumberMax": "999",
    "searchIncludeExcludeDays": "include",
}


# Encryption key management
def get_or_create_key():
    key_file = "key.key"
    if os.path.exists(key_file):
        with open(key_file, "rb") as keyfile:
            return keyfile.read()
    key = Fernet.generate_key()
    with open(key_file, "wb") as keyfile:
        keyfile.write(key)
    return key


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

if __name__ == "__main__":
    while not openClass:
        checkClass()  # Check number of open seats
        print("Checked. Waiting for 7 minutes...")
        time.sleep(7 * 60)  # Sleep for 7 minutes (7 * 60 seconds)

        if openClass == True:
            break

logging.basicConfig(filename="class_scraper.log", level=logging.INFO)
logging.info(f"Checked at {datetime.now()}: {[(90, 90)]}")
