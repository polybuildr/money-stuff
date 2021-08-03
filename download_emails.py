import base64
import os.path
import os
import re
import time
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
DOWNLOAD_DIRECTORY_RELATIVE = "data/emails/"

# Interact with the Google Workspace APIs following the quickstart
# guide at https://developers.google.com/gmail/api/quickstart/python.
def make_creds():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(
                    "Refreshing credentials did not seem to work for me, I got a bad "
                    "request error..."
                )
                raise e
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds


def main():
    service = build("gmail", "v1", credentials=make_creds())

    # Get emails (messages). The responses contain the id we can use to fetch the full message.
    results = (
        service.users()
        .messages()
        .list(
            userId="me",
            q="from:Matt Levine <noreply@mail.bloombergview.com>",
            # Cap to maximum allowed value.
            maxResults=500,
        )
        .execute()
    )
    emails = results.get("messages", [])

    if not emails:
        print("No emails found.")
    else:
        print(f"Found {len(emails)} emails.")
        # Ensure download directory is present.
        os.makedirs(DOWNLOAD_DIRECTORY_RELATIVE, exist_ok=True)
        for email in emails:
            # Short sleep to reduce chances of rate limiting.
            time.sleep(0.2)
            print(f"Downloading email '{email['id']}'... ", end="")
            msg = (
                service.users()
                .messages()
                .get(userId="me", id=email["id"], format="full")
                .execute()
            )
            print("Done.")
            subject = next(
                h for h in msg["payload"]["headers"] if h["name"] == "Subject"
            )["value"]
            received_date = datetime.fromtimestamp(int(msg["internalDate"]) / 1000)
            # NOTE: The HTML body seems to always be the second part.
            html_body = base64.urlsafe_b64decode(
                msg["payload"]["parts"][1]["body"]["data"]
            )
            clean_subject = re.sub("[^a-zA-Z0-9]+", "-", subject.replace('’', ''))
            file_name = (
                f"{DOWNLOAD_DIRECTORY_RELATIVE}{received_date.strftime('%Y-%m-%d')}-"
                f"{clean_subject}.html"
            )
            print(f"Writing {file_name} ... ", end="")
            with open(file_name, "w") as f:
                f.write(html_body.decode("utf-8"))
            print("Done.")


if __name__ == "__main__":
    main()
