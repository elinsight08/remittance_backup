import requests
import frappe

def get_access_token(client_id, client_secret, tenant_id):
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://graph.microsoft.com/.default'
    }
    response = requests.post(url, data=payload)
    if response.status_code != 200:
        raise Exception(f"Failed to get access token: {response.text}")
    return response.json().get('access_token')

def send_email(access_token, subject, html_content, recipient, sender_email):
    url = f"https://graph.microsoft.com/v1.0/users/{sender_email}/sendMail"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    email_data = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "HTML",
                "content": html_content
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": recipient
                    }
                }
            ]
        },
        "saveToSentItems": "true"
    }
    response = requests.post(url, headers=headers, json=email_data)
    return response.status_code, response.json() if response.content else {}

def custom_send_mail(recipient, subject, content):
    settings = frappe.get_doc(
						"Ms365 Configuration", "Ms365 Configuration",
					)

    sender_email = settings.sender_email
    client_id = settings.client_id
    client_secret = settings.get_password("client_secret")
    tenant_id = settings.tenant_id

    try:
        access_token = get_access_token(client_id, client_secret, tenant_id)
        status_code, response = send_email(access_token, subject, content, recipient, sender_email)

        if status_code == 202:
            print("✅ Email sent successfully")
        else:
            print(f"❌ Failed to send email: {status_code} - {response}")
    except Exception as e:
        print(f"❌ Error: {e}")


