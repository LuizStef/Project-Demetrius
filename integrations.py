import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from security import logger

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/tasks.readonly",
    "https://www.googleapis.com/auth/tasks",
]

class GoogleIntegration:
    def __init__(self):
        self.__creds   = None
        self.__token   = "token.json"
        self.__creds_file = "credentials.json"
        self._authenticate()

    def _authenticate(self):
        if os.path.exists(self.__token):
            self.__creds = Credentials.from_authorized_user_file(self.__token, SCOPES)

        if not self.__creds or not self.__creds.valid:
            if self.__creds and self.__creds.expired and self.__creds.refresh_token:
                self.__creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.__creds_file, SCOPES)
                self.__creds = flow.run_local_server(port=0)
            with open(self.__token, "w") as f:
                f.write(self.__creds.to_json())

        logger.info("Google authentication successful.")

    # ─── GMAIL ────────────────────────────────────────────────────────────────

    def get_emails(self, max_results=5):
        """Returns the latest unread emails."""
        try:
            service  = build("gmail", "v1", credentials=self.__creds)
            results  = service.users().messages().list(
                userId="me", labelIds=["INBOX", "UNREAD"], maxResults=max_results
            ).execute()
            messages = results.get("messages", [])
            emails   = []

            for msg in messages:
                data    = service.users().messages().get(userId="me", id=msg["id"]).execute()
                headers = {h["name"]: h["value"] for h in data["payload"]["headers"]}
                snippet = data.get("snippet", "")
                emails.append({
                    "from":    headers.get("From", "Unknown"),
                    "subject": headers.get("Subject", "No subject"),
                    "snippet": snippet[:100]
                })

            return emails
        except Exception as e:
            logger.error(f"Gmail error: {e}")
            return []

    def send_email(self, to, subject, body):
        """Sends an email."""
        try:
            import base64
            from email.mime.text import MIMEText

            service = build("gmail", "v1", credentials=self.__creds)
            message = MIMEText(body)
            message["to"]      = to
            message["subject"] = subject
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            service.users().messages().send(userId="me", body={"raw": raw}).execute()
            logger.info(f"Email sent to {to}")
            return True
        except Exception as e:
            logger.error(f"Send email error: {e}")
            return False

    # ─── GOOGLE DRIVE ─────────────────────────────────────────────────────────

    def list_drive_files(self, max_results=10):
        """Lists recent files from Google Drive."""
        try:
            service = build("drive", "v3", credentials=self.__creds)
            results = service.files().list(
                pageSize=max_results,
                fields="files(id, name, mimeType, modifiedTime)",
                orderBy="modifiedTime desc"
            ).execute()
            return results.get("files", [])
        except Exception as e:
            logger.error(f"Drive error: {e}")
            return []

    def create_drive_file(self, name, content, mime_type="text/plain"):
        """Creates a file in Google Drive."""
        try:
            from googleapiclient.http import MediaInMemoryUpload
            service  = build("drive", "v3", credentials=self.__creds)
            metadata = {"name": name}
            media    = MediaInMemoryUpload(content.encode(), mimetype=mime_type)
            file     = service.files().create(body=metadata, media_body=media, fields="id").execute()
            logger.info(f"Drive file created: {name}")
            return file.get("id")
        except Exception as e:
            logger.error(f"Create drive file error: {e}")
            return None

    # ─── GOOGLE CALENDAR ──────────────────────────────────────────────────────

    def get_events(self, max_results=5):
        """Returns upcoming calendar events."""
        try:
            from datetime import datetime, timezone
            service  = build("calendar", "v3", credentials=self.__creds)
            now      = datetime.now(timezone.utc).isoformat()
            results  = service.events().list(
                calendarId="primary",
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime"
            ).execute()
            return results.get("items", [])
        except Exception as e:
            logger.error(f"Calendar error: {e}")
            return []

    def create_event(self, title, start, end, description=""):
        """Creates a calendar event. start/end: 'YYYY-MM-DDTHH:MM:SS'"""
        try:
            service = build("calendar", "v3", credentials=self.__creds)
            event   = {
                "summary":     title,
                "description": description,
                "start":       {"dateTime": start, "timeZone": "America/Sao_Paulo"},
                "end":         {"dateTime": end,   "timeZone": "America/Sao_Paulo"},
            }
            result = service.events().insert(calendarId="primary", body=event).execute()
            logger.info(f"Event created: {title}")
            return result.get("id")
        except Exception as e:
            logger.error(f"Create event error: {e}")
            return None

    # ─── GOOGLE TASKS ─────────────────────────────────────────────────────────

    def get_tasks(self, max_results=10):
        """Returns tasks from Google Tasks."""
        try:
            service   = build("tasks", "v1", credentials=self.__creds)
            lists     = service.tasklists().list().execute()
            all_tasks = []

            for task_list in lists.get("items", []):
                tasks = service.tasks().list(
                    tasklist=task_list["id"],
                    maxResults=max_results,
                    showCompleted=False
                ).execute()
                for t in tasks.get("items", []):
                    all_tasks.append({
                        "title":   t.get("title", ""),
                        "due":     t.get("due", "No due date"),
                        "list":    task_list["title"],
                        "status":  t.get("status", "")
                    })

            return all_tasks
        except Exception as e:
            logger.error(f"Tasks error: {e}")
            return []

    def create_task(self, title, due=None, notes=""):
        """Creates a task in Google Tasks."""
        try:
            service = build("tasks", "v1", credentials=self.__creds)
            lists   = service.tasklists().list().execute()
            list_id = lists["items"][0]["id"]
            task    = {"title": title, "notes": notes}
            if due:
                task["due"] = due
            result = service.tasks().insert(tasklist=list_id, body=task).execute()
            logger.info(f"Task created: {title}")
            return result.get("id")
        except Exception as e:
            logger.error(f"Create task error: {e}")
            return None