import os
import base64
from email.message import EmailMessage

from fastmcp import FastMCP
from pathlib import Path
from email.mime.base import MIMEBase
from email import encoders
import mimetypes


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

# Shared folder where Drive MCP drops files
# Allowed user directories
ALLOWED_BASE_DIRS = [
    Path(r"C:/Users/arpit/Desktop").resolve(),
    Path(r"C:/Users/arpit/Documents").resolve(),
    Path(r"C:/Users/arpit/Downloads").resolve(),
    Path(r"C:/Users/arpit/OneDrive").resolve(),
]

ALLOWED_EXTENSIONS = {".pdf"}
MAX_ATTACHMENT_MB = 25





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
# Helper Function
# ------------------------------------------------------------------------------
def validate_and_attach(message: EmailMessage, file_path: str):
    path = Path(file_path).expanduser().resolve()

    # 1. Must exist
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Attachment not found: {path}")

    # 2. Must be inside allowed user directories
    if not any(base in path.parents for base in ALLOWED_BASE_DIRS):
        raise PermissionError("File path is not in an allowed user directory")

    # 3. Block hidden/system files
    if path.name.startswith("."):
        raise PermissionError("Hidden/system files are not allowed")

    # 4. Extension check
    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError("Only PDF attachments are allowed")

    # 5. Size check
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > MAX_ATTACHMENT_MB:
        raise ValueError("Attachment exceeds Gmail size limit (25 MB)")

    # 6. Attach file
    mime_type, _ = mimetypes.guess_type(path)
    maintype, subtype = mime_type.split("/", 1)

    with open(path, "rb") as f:
        data = f.read()

    message.add_attachment(
        data,
        maintype=maintype,
        subtype=subtype,
        filename=path.name
    )


# ------------------------------------------------------------------------------
# TOOLS
# ------------------------------------------------------------------------------

@mcp.tool()
def health_check() -> dict:
    """Check whether the Gmail MCP server is running."""
    return {"status": "ok", "service": "gmail-mcp-server"}


@mcp.tool()
def send_email(
    to: str,
    subject: str,
    body: str,
    attachments: list[str] = []
) -> dict:
    """
    Send an email using Gmail.
    
    Args:
        to: Recipient email address
        subject: Email subject line
        body: Email body content
        attachments: List of file paths to attach (PDF files only, max 25MB each)
    
    Returns:
        dict with status, message_id, and list of attachments sent
    """
    service = get_gmail_service()

    message = EmailMessage()
    message.set_content(body)
    message["To"] = to
    message["Subject"] = subject

    # Attach files if provided
    if attachments:
        for file_path in attachments:
            validate_and_attach(message, file_path)

    encoded_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    result = service.users().messages().send(
        userId="me",
        body={"raw": encoded_message}
    ).execute()

    return {
        "status": "sent",
        "message_id": result["id"],
        "attachments": attachments or []
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
