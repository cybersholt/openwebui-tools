import os

from datetime import datetime
from pydantic import BaseModel, Field
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly", "https://www.googleapis.com/auth/gmail.readonly"]

"""
title: Google Tools
author: Markus Karileet
author_url: https://website.com
git_url: https://github.com/Shmarkus/openwebui-tools.git
description: This tool provides functionalities to interact with Google Calendar and Gmail using the Google API. It allows you to fetch upcoming events from your calendar and retrieve emails from your inbox.
required_open_webui_version: 0.5.7
requirements: google-api-python-client, google-auth-httplib2, google-auth-oauthlib, requests
version: 0.0.1
licence: MIT
"""


class Tools:
    def __init__(self):
        """Initialize the Tool."""
        self.valves = self.Valves()
        self.citation = True

    class Valves(BaseModel):
        default_calendar_entries: int = Field(
                default=10, description="The default number of calendar entries to fetch"
        )
        default_email_entries: int = Field(
            default=10, description="The default number of email entries to fetch"
        )
        path_to_credentials: str = Field(
            default="credentials.json", description="The absolute path to the credentials file"
        )
        pass

    def get_user_emails(self, number_of_emails: int = -1) -> str:
        """
        Retrieves and displays the latest emails from the user's Gmail inbox.

        This function fetches the specified number of emails (default is 10 if not provided)
        and returns a formatted string containing the email details such as date, sender,
        subject, body snippet, and whether it's unread or not. If no messages are found,
        it returns "No messages found."

        :param number_of_emails: The maximum number of emails to fetch from the inbox.
            If set to -1 (default), it uses the default value configured in the tool
            settings.

        :return: A formatted string containing the email details or an error message if
        there's a problem fetching the emails.
        """
        if number_of_emails == -1:
            number_of_emails = self.valves.default_email_entries
        creds = self.get_google_creds()
        out = "Messages:\n"
        try:
            service = build("gmail", "v1", credentials=creds)
            results = service.users().messages().list(
                userId="me",
                maxResults=number_of_emails,
                includeSpamTrash=False
            ).execute()
            messages = results.get("messages", [])

            if not messages:
                return "No messages found."

            for msg in messages:
                mail = service.users().messages().get(userId="me", id=msg["id"]).execute()
                from_field = next((field for field in mail["payload"]["headers"] if field["name"] == "From"), None)
                subject_field = next((field for field in mail["payload"]["headers"] if field["name"] == "Subject"), None)
                date_field = next((field for field in mail["payload"]["headers"] if field["name"] == "Date"), None)
                unread = "UNREAD" in mail["labelIds"]
                snippet = mail["snippet"]
                date = date_field["value"]
                sender = from_field["value"]
                subject = subject_field["value"]
                out += f"Date: {date}, From: {sender}, Subject: {subject}, Body: {snippet}, Unread: {unread}\n"

        except HttpError as error:
            print(f"An error occurred: {error}")

        return out

    def get_user_events(self, number_of_events: int = -1) -> str:
        """
        Retrieves and displays upcoming events from the user's Google Calendar.

        This function fetches the specified number of upcoming events (default is 10 if not provided)
        and returns a formatted string containing event details such as start time,
        summary, and creator email. If no events are found, it returns "No upcoming events found."

        The method retrieves all user calendar IDs first, then fetches events from each calendar.
        Events are sorted by their start time before being returned.

        :param number_of_events: The maximum number of upcoming events to fetch from the calendars.
            If set to -1 (default), it uses the default value configured in the tool settings.

        :return: Upcoming events as a formatted string, or an error message if fetching fails.
        """
        if number_of_events == -1:
            number_of_events = self.valves.default_calendar_entries
        creds = self.get_google_creds()

        try:
            service = build("calendar", "v3", credentials=creds)
            from_time = datetime.utcnow().isoformat() + "Z"
            out = f"Today is {from_time}\n"
            calendar_ids = self.get_calendar_ids(service)
            event_list = []
            for calendar_id in calendar_ids:
                events = self.get_cal_evts(service, calendar_id, number_of_events, from_time)
                event_list += events
            event_list.sort(key=lambda x: x["start"])
            for i in range(number_of_events):
                out += f"Start: {event_list[i]['start']}, Summary: {event_list[i]['summary']}, Creator: {event_list[i]['creator']}\n"
            return out

        except HttpError as error:
            return f"Error fetching calendar data: {str(error)}"

    def get_google_creds(self):
        """
        Get the Google credentials
        :return:
        """
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.

        # If necessary, uncomment the following line to remove generated token.json on re-authenticate
        # os.remove("token.json")
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
            # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.valves.path_to_credentials, SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        return creds

    @staticmethod
    def get_calendar_ids(service) -> list:
        """
        Get all user calendar ids
        :return List of Calendar IDs
        """
        out = []
        calendars = (service.calendarList().list().execute())
        cals = calendars.get("items", [])
        for cal in cals:
            out.append(cal["id"])

        return out


    @staticmethod
    def get_cal_evts(service, calendarId, number_of_events, from_time) -> list:
        """
        Get the events from user calendar
        :param service:
        :param calendarId:
        :param number_of_events:
        :return: list of events with start time and creator ID
        """
        out = []
        events_result = (
            service.events()
            .list(
                calendarId=calendarId,
                timeMin=from_time,
                maxResults=number_of_events,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])
        for event in events:
            out.append({
                "start": event["start"].get("dateTime", event["start"].get("date")),
                "summary": event["summary"],
                "creator": event["creator"]["email"]
            })

        return out