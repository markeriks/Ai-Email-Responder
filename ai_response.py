import requests

API_ENDPOINT = 'http://localhost:1234/v1/chat/completions'

def generate_reply(email_body):
    data = {
        'model': 'mistral-7b-instruct-v0.2',
        "messages": [{
            "role": "assistant",
            "content": "You are an AI email assistant named Nova. Your job is to read emails and generate polite, professional responses."
        },
        {
            "role": "user",
            "content": f"Here is the email body: {email_body}"
        }]
    }
    response = requests.post(url=API_ENDPOINT, json=data)
    result = response.json()
    content = result['choices'][0]['message']['content']
    #subject = content.split("\n", 1)[0]
    message = content.split("\n", 1)[1]
    #subject = subject.replace(" Subject: ", "")
    return message
