from gmail import authenticate_gmail, get_email, send_email
from ai_response import generate_reply

def main():
    creds = authenticate_gmail()
    email_body, sender_email, message_id, thread_id, subject = get_email(creds)
    message = generate_reply(email_body)
    print(message_id)
    send_email(creds, message, subject, sender_email, message_id, thread_id)


if __name__ == '__main__':
    main()