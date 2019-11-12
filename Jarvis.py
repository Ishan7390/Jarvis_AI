from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import pyttsx3
import os
import time
import speech_recognition as sr
import pytz
import subprocess
# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly'] 
MONTHS = ["January", "February", "March", "April", "May", "June","July", "August", "September","October", " November", "December"]
DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
DAY_EXTENSIONS = ["rd","th","st","nd"]

def speak(text):
	engine = pyttsx3.init()
	engine.say(text)
	engine.runAndWait()

def get_audio():
	r = sr.Recognizer()
	with sr.Microphone() as source:
		audio = r.listen(source)
		said = ""

		try:
			said = r.recognize_google(audio)
			print(said)
		except Exception as e:
			print("Exception: " + str(e))
	return said.lower()		
			
'''text = get_audio()

if "hello" in text:
	speak("hello, how are you?")

if "what is your name" in text:
	speak("I am Jarvis")

if "who are you" in text:
	speak("I am Jarvis, Ishan's Personal Assistant")
'''



def authenticate_google():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    return service

def get_events(day, service):    

    # Call the Calendar API
    date = datetime.datetime.combine(day,datetime.datetime.min.time())
    end_date = datetime.datetime.combine(day,datetime.datetime.max.time())
    utc = pytz.UTC
    day = date.astimezone(utc)
    end_date = end_date.astimezone(utc)

    events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(), timeMax=end_date.isoformat(),
                                        singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    else:
        speak(f'You have {len(events)} events on this day. ')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
            start_time = str(start.split("T")[1].split("-")[0]
            if int(start_time.split(":")[0]) < 12:
                start_time += "am"
            else:
                start_time = str(int(start_time.split(":")[0]) - 12) + start_time.split(":")[1])
                start_time += "pm"	
                speak(event["sumary"] + " at " + start_time)

'''
if __name__ == '__main__':
    main()
'''

def get_date(text):
	text = text.lower()
	today = datetime.date.today()
	if text.count("today") > 0:
		return today

	day = -1
	day_of_week = -1
	month = -1
	year = today.year

	for word in text.split():
		if word in MONTHS:
			month = MONTHS.index(word) + 1
		elif word in DAYS:
			day_of_week = DAYS.index(word)
		elif word.isdigits():
			day = int(word)
		else:
			for ext in DAY_EXTENSIONS:
				found = word.find(ext)
				if found>0:
					try:
						day = int(word[:found])
					except:
						pass		
	if month < today.month and month != -1:
		year += 1
	if day<today.day and month == -1 and day != -1:
		month += 1
	if month == -1 and day == -1 and day_of_week != -1:
		current_day_of_week = today.weekday()
		diff = day_of_week - current_day_of_week

		if diff <0:
			diff += 7
			if text.count("text") >= 1:
				diff += 7
		return today + datetime.timedelta(diff)
	if month == -1 or day == -1:
		return None	
	return datetime.date(month=month, day=day, year=year)				

def note(text):
	date = datetime.datetime.now()
	file_name = str(date).replace(":","-") + "-note.txt"
	with open(filename, "w") as f:
		f.write(text)
	subprocess.Popen(["notepad.exe", file_name])

WAKE = "Jarvis"

SERVICE = authenticate_google()
print("At your service!!")

while True:
	print("Listening...")
	text = get_audio()

	if text.count(WAKE) > 0:
		speak("Yes Sir")
		text = get_audio()

		CALENDAR_STRS = ["what do i have", "do i have plans", "am i busy", "do i have any plans", ""]
		for phrase in CALENDAR_STRS:
			if phrase in text:
				date = get_date(text)
				if date:
					get_events(date, SERVICE)
				else:
					speak("I don't understand")

		NOTE_STRS = ["make a note", "write this down","remember this"]
		for phrase in NOTE_STRS:
			if phrase in text:
				speak("What would you like me to make a note of?")
				note_text = get_audio()
				note(note_text)
				speak("I've made a note of that.")