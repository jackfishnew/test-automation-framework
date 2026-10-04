import requests
import re

def get_email_text(recipient: str, subject_query: str = "") -> str:
    """Finds the most recent email for a recipient and returns its plain text body."""
    # Search messages
    query = f"to:{recipient} {subject_query}".strip()
    response = requests.get("http://localhost:8025/api/v1/messages", params={"query": query})
    data = response.json()
    
    messages = data.get("messages", [])
    assert len(messages) > 0, f"No email found for query: {query}"
    
    # Get the ID of the most recent message
    latest_id = messages[0]["ID"]
    
    # Fetch full message details
    msg_response = requests.get(f"http://localhost:8025/api/v1/message/{latest_id}")
    return msg_response.json().get("Text", "")

def get_activation_token_from_email_body(recipient: str):
    email_body = get_email_text(recipient=recipient)

    # 2. Match everything after 'activate/' until a space, quote, or closing bracket
    pattern = r"api/user_management/activate/([^\s\"'>/]+)"
    match = re.search(pattern, email_body)

    assert match, f"Could not find activation URL pattern in email:\n{email_body}"

    # Return the captured token string
    return match.group(1)

def get_password_reset_confirm_token_from_email_body(recipient: str):
    email_body = get_email_text(recipient=recipient)

    # 2. Match everything after 'activate/' until a space, quote, or closing bracket
    pattern = r"password_reset_confirm/([^\s\"'>/]+)"
    match = re.search(pattern, email_body)

    assert match, f"Could not find activation URL pattern in email:\n{email_body}"

    # Return the captured token string
    return match.group(1)

def get_url_from_email_body(recipient: str):
    email_body = get_email_text(recipient=recipient)
    pattern = r"https?://[^\s]+"
    match = re.search(pattern, email_body)

    assert match, f"Could not find activation URL pattern in email:\n{email_body}"

    # Return the captured token string
    return match.group(0)


def clear_emails_mailpit(mailpit_host):
    response = requests.delete(f"{mailpit_host}/api/v1/messages")
    response.raise_for_status()
