# Gmail MCP Server 📧

A powerful Model Context Protocol (MCP) server that enables AI assistants like Claude to interact with Gmail. This server provides seamless integration for sending emails, searching messages, and reading email content directly through Claude.

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Compatible-orange.svg)](https://modelcontextprotocol.io/)

## ✨ Features

- **Send Emails**: Compose and send emails directly through Claude
- **Search Emails**: Use Gmail's powerful search syntax to find specific messages
- **Read Emails**: Retrieve and read email content by message ID
- **OAuth2 Authentication**: Secure authentication using Google OAuth2
- **Health Check**: Built-in health monitoring endpoint

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- A Google Cloud Platform account
- Claude Desktop App or any MCP-compatible client

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Arpit-saxena-2004/gmail_mcp_server.git
   cd gmail_mcp_server
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   
   # On Windows
   .venv\Scripts\activate
   
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 🔑 Setting Up Google OAuth2 Credentials

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **Gmail API** for your project:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"

### Step 2: Configure OAuth Consent Screen

1. Go to "APIs & Services" > "OAuth consent screen"
2. Choose "External" user type (or "Internal" if you have a Google Workspace)
3. Fill in the required information:
   - App name
   - User support email
   - Developer contact information
4. Add scopes: `https://www.googleapis.com/auth/gmail.modify`
5. Add test users (your email address)

### Step 3: Create OAuth2 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Choose "Desktop app" as the application type
4. Name it (e.g., "Gmail MCP Server")
5. Click "Create"
6. Download the JSON file
7. **Rename it to `credentials.json`** and place it in the project root directory

## ⚙️ Configuration

### Connecting to Claude Desktop

1. **Locate your Claude Desktop configuration file:**

   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

2. **Add the MCP server configuration:**

   ```json
   {
     "mcpServers": {
       "gmail": {
         "command": "python",
         "args": [
           "C:\\path\\to\\your\\gmail_mcp_server\\main.py"
         ]
       }
     }
   }
   ```

   **Note**: Replace `C:\\path\\to\\your\\gmail_mcp_server\\main.py` with the actual path to your `main.py` file.

3. **Restart Claude Desktop**

### First-Time Authentication

1. When you first use the server, it will open a browser window
2. Sign in with your Google account
3. Grant the requested permissions
4. The server will save a `token.json` file for future use
5. You won't need to authenticate again unless you revoke access

## 📖 Usage Examples

Once connected to Claude, you can use natural language to interact with Gmail:

### Sending Emails
```
"Send an email to john@example.com with subject 'Meeting Tomorrow' and tell him about the 2pm meeting"
```

### Searching Emails
```
"Search my emails for messages from Sarah in the last week"
```

### Reading Emails
```
"What's the latest email in my inbox?"
```

## 🛠️ Available Tools

### `health_check()`
Check if the Gmail MCP server is running properly.

### `send_email(to: str, subject: str, body: str)`
Send an email via Gmail.
- **to**: Recipient email address
- **subject**: Email subject line
- **body**: Email content

### `search_emails(query: str, max_results: int = 5)`
Search emails using Gmail's search syntax.
- **query**: Gmail search query (e.g., "from:john@example.com", "subject:meeting")
- **max_results**: Maximum number of results to return (default: 5)

### `read_email(message_id: str)`
Read a specific email by its message ID.
- **message_id**: The unique identifier of the email

## 🔒 Security Notes

- **Never commit** `credentials.json` or `token.json` to version control
- These files are already included in `.gitignore`
- Store credentials securely and rotate them periodically
- Only grant necessary scopes (currently: `gmail.modify`)

## 📁 Project Structure

```
gmail_mcp_server/
├── main.py              # Main MCP server implementation
├── credentials.json     # OAuth2 credentials (not in repo)
├── token.json          # OAuth2 token (auto-generated)
├── requirements.txt    # Python dependencies
├── pyproject.toml      # Project metadata
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

## 🐛 Troubleshooting

### "credentials.json not found"
- Make sure you've downloaded the OAuth2 credentials from Google Cloud Console
- Rename the file to exactly `credentials.json`
- Place it in the project root directory

### Authentication window doesn't open
- Check if port 0 (random available port) is not blocked by firewall
- Try running the server manually first: `python main.py`

### "Invalid credentials" error
- Delete `token.json` and authenticate again
- Verify your OAuth2 consent screen is properly configured
- Ensure you've added your email as a test user

### Claude can't connect to the server
- Verify the path in `claude_desktop_config.json` is correct
- Make sure you're using absolute paths
- Restart Claude Desktop after configuration changes

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [FastMCP](https://github.com/jlowin/fastmcp) - A fast, simple framework for building MCP servers
- Uses [Google Gmail API](https://developers.google.com/gmail/api)
- Designed for [Claude](https://claude.ai) by Anthropic

## 📞 Support

If you encounter any issues or have questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review the [MCP documentation](https://modelcontextprotocol.io/)

## 🌟 Star History

If you find this project useful, please consider giving it a star! ⭐

---

**Made with ❤️ for the Claude community**
