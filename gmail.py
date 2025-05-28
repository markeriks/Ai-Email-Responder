import os.path
import base64
from email.message import EmailMessage

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


def authenticate_gmail():
  creds = None
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    with open("token.json", "w") as token:
      token.write(creds.to_json())
  return creds



def get_email(creds):
  try:
    service = build("gmail", "v1", credentials=creds)
    results = service.users().messages().list(userId="me", labelIds=["UNREAD"], maxResults=1).execute()
    messages = results.get("messages", [])

    if not messages:
      print("No unread messages")
      return None, None
    else:
      for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        body_data = msg['payload'].get('body', {}).get('data')
        if not body_data:
          parts = msg['payload'].get('parts', [])
          for part in parts:
            if part['mimeType'] == 'text/plain':
              body_data = part['body'].get('data')
              break

        decoded_bytes = base64.urlsafe_b64decode(body_data)
        email_body = decoded_bytes.decode('utf-8')

        sender_email = None
        for header in msg['payload']['headers']:
          if header['name'] == 'From':
            sender_email = header['value']
            break
        message_id = None
        for header in msg['payload']['headers']:
          if header['name'] == 'Message-ID':
              message_id = header['value']
        subject = None
        for header in msg['payload']['headers']:
            if header['name'] == 'Subject':
                subject = header['value']
        thread_id = msg['threadId']
        print(email_body)
      return email_body, sender_email, message_id, thread_id, "Re: " + subject

  except HttpError as error:
    print(f"An error occurred: {error}")


def send_email(creds, content, subject, sender_email, message_id, thread_id):
  try:
    service = build("gmail", "v1", credentials=creds)
    message = EmailMessage()

    message.set_content(content)

    message["To"] = sender_email
    message["From"] = "me"
    message["Subject"] = subject
    message["In-Reply-To"] = message_id
    message["References"] = message_id

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    create_message = {
    "raw": encoded_message,
    "threadId": thread_id
    }
    send_message = (
        service.users()
        .messages()
        .send(userId="me", body=create_message)
        .execute()
    )
    print(f'Message sent successfully! Message Id: {send_message["id"]}')
  except HttpError as error:
    print(f"An error occurred: {error}")
