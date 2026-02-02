import os
import base64
from email.message import EmailMessage

from fastmcp import FastMCP

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# ------------------------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------------------------

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CREDENTIALS_FILE = os.path.join(BASE_DIR, "credentials.json")
TOKEN_FILE = os.path.join(BASE_DIR, "token.json")



# ------------------------------------------------------------------------------
# AUTHENTICATION
# ------------------------------------------------------------------------------

def get_gmail_service():
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


# ------------------------------------------------------------------------------
# MCP SERVER
# ------------------------------------------------------------------------------

mcp = FastMCP(name="gmail-mcp-server")


# ------------------------------------------------------------------------------
# TOOLS
# ------------------------------------------------------------------------------

@mcp.tool()
def health_check() -> dict:
    """Check whether the Gmail MCP server is running."""
    return {"status": "ok", "service": "gmail-mcp-server"}


@mcp.tool()
def send_email(to: str, subject: str, body: str) -> dict:
    """Send an email using Gmail."""
    service = get_gmail_service()

    message = EmailMessage()
    message.set_content(body)
    message["To"] = to
    message["Subject"] = subject

    encoded_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    result = service.users().messages().send(
        userId="me",
        body={"raw": encoded_message}
    ).execute()

    return {
        "status": "sent",
        "message_id": result["id"]
    }


@mcp.tool()
def search_emails(query: str, max_results: int = 5) -> dict:
    """Search emails using Gmail search syntax."""
    service = get_gmail_service()

    response = service.users().messages().list(
        userId="me",
        q=query,
        maxResults=max_results
    ).execute()

    messages = response.get("messages", [])

    return {
        "query": query,
        "count": len(messages),
        "messages": messages
    }


@mcp.tool()
def read_email(message_id: str) -> dict:
    """Read a specific email by message ID."""
    service = get_gmail_service()

    msg = service.users().messages().get(
        userId="me",
        id=message_id,
        format="full"
    ).execute()

    headers = msg["payload"].get("headers", [])

    subject = sender = None
    for h in headers:
        if h["name"] == "Subject":
            subject = h["value"]
        if h["name"] == "From":
            sender = h["value"]

    snippet = msg.get("snippet", "")

    return {
        "message_id": message_id,
        "from": sender,
        "subject": subject,
        "snippet": snippet
    }


# ------------------------------------------------------------------------------
# ENTRY POINT
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
