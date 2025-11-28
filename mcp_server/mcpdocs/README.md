# MCP Purchase Agent

A comprehensive Model Context Protocol (MCP) server for automated purchase order management, processing, and workflow automation. This server provides a complete suite of tools for handling purchase orders from email monitoring to document generation and database management.

## 🏗️ Architecture Overview

**Production Deployment (Recommended):**
- **Hosting Platform**: Google Cloud Run (serverless, managed, HTTPS)
- **Database**: MongoDB Atlas (managed MongoDB database service)
- **Integration**: ADK agents call MCP tools via HTTPS

This setup provides a scalable, secure, and maintainable architecture where:
- MCP server runs as a managed Cloud Run service
- MongoDB Atlas handles all database operations
- ADK agents invoke MCP tools remotely via the Cloud Run URL


## 🚀 Features

### Core Capabilities
- **📧 Email Monitoring**: Automatically fetch and process purchase orders from Gmail
- **📄 Document Processing**: OCR and AI-powered extraction of purchase order data from PDFs
- **📝 Document Generation**: Create professional PDF purchase orders using LaTeX
- **📦 Inventory Management**: Track stock levels and identify restock needs
- **💰 Financial Validation**: Automated approval workflows and budget checking
- **🗄️ Database Management**: Store and retrieve purchase order records in MongoDB
- **✉️ Email Automation**: Send professional purchase order emails with attachments
- **📋 Queue Management**: Manage purchase request workflows
- **📊 Report Generation**: Create and save inventory and status reports

### Available Tools
1. **generate_purchase_order** - Generate PDF purchase order documents
2. **generate_latex_po** - Generate LaTeX purchase order documents
3. **validate_po_items** - Validate purchase order items format
4. **create_sample_po_data** - Create sample purchase order data for testing
5. **fetch_emails** - Fetch unread emails with attachments from Gmail
6. **parse_document** - Parse documents and extract structured purchase order data
7. **get_financial_data** - Get financial data and approval status
8. **manage_purchase_queue** - Manage purchase request queue operations
9. **manage_po_records** - Execute PO record management actions
10. **generate_po_email** - Generate and send purchase order emails to suppliers
11. **analyze_inventory** - Analyze inventory and get restock information
12. **save_report** - Save data to text files
13. **send_response_email** - Send email responses with custom subject and body

## 📋 Prerequisites

- **Python 3.11+**
- **MongoDB** (MongoDB Atlas recommended for production, or localhost:27017 for local dev)
- **LaTeX distribution** (for PDF generation)
- **Gmail account** with app-specific password
- **Google AI API key** (for document processing)

## 🛠️ Environment Configuration (Local Dev)
Create a `.env` file in the project root:

```env
# Gmail Configuration (Buyer/Company Email)
GMAIL_EMAIL=buyer@company.com
GMAIL_APP_PASSWORD=your-16-character-app-password
email=buyer@company.com
password=your-16-character-app-password

# Supplier Email Configuration
supemail=supplier@example.com
suppassword=supplier-app-password

# Google AI Configuration
GOOGLE_API_KEY=your-google-ai-api-key

# MongoDB Configuration (optional, defaults shown)
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=purchase_orders

# Server Configuration (local)
MCP_SERVER_PORT=8099
TRANSPORT_MODE=stdio  # Options: stdio, sse, streamable-http

# Company Information
COMPANY_NAME=Your Company Name
COMPANY_ADDRESS=Your Company Address
COMPANY_EMAIL=company@example.com
```

### Environment Variables Explained

#### Email Configuration
- **GMAIL_EMAIL / email**: Your company's buyer email address (Gmail account)
- **GMAIL_APP_PASSWORD / password**: Gmail app-specific password (16-character code)
- **supemail**: Supplier's email address for communications
- **suppassword**: Supplier's email app-specific password (if needed)

#### API Keys
- **GOOGLE_API_KEY**: Your Google AI/Gemini API key for document processing

#### How to Get Gmail App Password
1. Enable 2-Factor Authentication on your Gmail account
2. Go to Google Account settings → Security → 2-Step Verification
3. Select "App passwords" at the bottom
4. Generate a new app password for "Mail"
5. Use the 16-character code (no spaces) as your app password

#### How to Get Google AI API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key

### 4. External Dependencies

#### MongoDB Setup
```bash
# Install MongoDB Community Edition
# Visit: https://www.mongodb.com/try/download/community

# Start MongoDB service
# Windows: Start as Windows Service
# macOS: brew services start mongodb-community
# Linux: sudo systemctl start mongod
```

#### LaTeX Setup
```bash
# Windows (MiKTeX)
# Download from: https://miktex.org/download

# macOS (MacTeX)
brew install --cask mactex

# Ubuntu/Debian
sudo apt-get install texlive-full

# Arch Linux
sudo pacman -S texlive-most
```

---

## ☁️ Cloud Run Deployment (Recommended for Production)

This project is ready to be deployed as a managed, HTTPS MCP service on **Google Cloud Run** (the hosting platform). The MCP server will connect to **MongoDB Atlas** (the database) for data persistence.

**Architecture:**
- **Hosting Platform**: Google Cloud Run (serverless, managed, HTTPS)
- **Database**: MongoDB Atlas (managed MongoDB service, recommended)
- **Alternative**: You can use a self-hosted MongoDB, but Atlas is preferred for production

The provided `Dockerfile` exposes port 8080 and sets `PORT=8080` to comply with Cloud Run.

### 1) Set Up MongoDB Atlas (Database)

Before deploying to Cloud Run, set up your MongoDB database:

**Option A: MongoDB Atlas (Recommended)**
1. Visit [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free cluster (or paid tier for production)
3. Create a database user with read/write permissions
4. Get your connection string (e.g., `mongodb+srv://username:password@cluster.mongodb.net/purchase_orders`)
5. Whitelist Cloud Run IP addresses or use `0.0.0.0/0` (allow from anywhere) in Network Access

**Option B: Self-Hosted MongoDB**
- Set up MongoDB on a VM or container with a public IP
- Ensure it accepts connections from Cloud Run
- Use connection string like `mongodb://username:password@your-mongo-host:27017/purchase_orders`

### 2) Build and Deploy to Cloud Run (Hosting Platform)

```bash
# From repo root, navigate to recruitment_backend directory
cd mcp_server/recruitment_backend

# Build and push image
gcloud builds submit --tag gcr.io/baseshare/recruitment-backend --project baseshare

# Deploy the service with required environment variables
gcloud run deploy recruitment-backend \
  --image gcr.io/baseshare/recruitment-backend \
  --platform managed \
  --region us-central1 \
  --project baseshare \
  --allow-unauthenticated \
  --port 8100 \
  --set-env-vars "GOOGLE_API_KEY=${GOOGLE_API_KEY},GITHUB_TOKEN=${GITHUB_TOKEN},HOST=0.0.0.0,PORT=8100"

OR
### Build locally, push manually

```bash
# From mcp_server/recruitment_backend directory
# The Dockerfile is already in recruitment_backend/
docker build -t gcr.io/baseshare/recruitment-backend .

# Or use gcloud builds submit (auto-detects Dockerfile)
gcloud builds submit --tag gcr.io/baseshare/recruitment-backend --project baseshare
```
Once the build completes:

```bash
### Authenticate Docker with GCR. Run:
gcloud auth configure-docker
# Push to GCR
docker push gcr.io/baseshare/recruitment-backend

```bash
# Build and run locally
docker build -t recruitment-backend-local .
docker run -p 8100:8100 \
  -e GOOGLE_API_KEY="..." \
  -e GITHUB_TOKEN="..." \
  -e HOST=0.0.0.0 \
  -e PORT=8100 \
  recruitment-backend-local

# Test it works before pushing to GCR
curl http://localhost:8100
# Should return A2A agent card or health check response
```

# Deploy to Cloud Run - Automate with Cloud Build + CI/CD
```bash
gcloud run deploy recruitment-backend \
  --image gcr.io/baseshare/recruitment-backend \
  --region us-central1 \
  --project baseshare \
  --allow-unauthenticated \
  --port 8100 \
  --set-env-vars="GOOGLE_API_KEY=${GOOGLE_API_KEY},GITHUB_TOKEN=${GITHUB_TOKEN},HOST=0.0.0.0,PORT=8100"
```

The container will now start successfully with all OpenGL/OpenCV dependencies! 🚀

# Get the service URL
gcloud run services describe recruitment-backend \
  --region us-central1 \
  --project baseshare \
  --format='value(status.url)'
# Example: https://recruitment-backend-xyz-uc.a.run.app
```

### 3) Configure ADK Agents to Use MCP

**IMPORTANT:** The recruitment-backend uses A2A (Agent-to-Agent) protocol with MCP tools integrated. Use the base URL (no `/mcp` path needed).

Set this in your ADK environment (backend deployment or local dev):

```bash
# ✅ CORRECT - For recruitment-backend, use the base URL (A2A server with MCP tools)
MCP_SERVER_URL=https://recruitment-backend-xyz-uc.a.run.app
```

```bash
# Get your recruitment-backend server URL
MCP_URL=$(gcloud run services describe recruitment-backend --region us-central1 --project baseshare --format='value(status.url)')
echo "Recruitment Backend URL: ${MCP_URL}"
echo "Set this as MCP_SERVER_URL environment variable"
```

**Verification:**
- FastMCP responds at `/mcp` with 406 (requires proper MCP headers) - this is expected
- ADK's `MCPToolset` with `StreamableHTTPConnectionParams` will handle protocol headers automatically

The supply chain agents (Buyer/Supplier orchestrators and their sub-agents) will call MCP tools via this URL.

**Complete Architecture:**
```
┌─────────────────┐
│   Next.js UI    │  (Vercel)
│   (Frontend)    │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   ADK Agents    │  (GCP Agent Engine)
│  Buyer/Supplier │
│  Orchestrators  │
└────────┬────────┘
         │
         ↓
┌─────────────────┐       ┌──────────────────┐
│   MCP Server    │──────→│  MongoDB Atlas   │
│  (Cloud Run)    │       │   (Database)     │
└─────────────────┘       └──────────────────┘
```

### 4) Verify Deployment

```bash
curl -s https://mcp-server-xyz-uc.a.run.app/health || echo "If /health isn't implemented yet, hit the base URL or a tool endpoint."
```

If your server exposes tool endpoints under `/mcp/<tool-name>`, verify one tool with a test payload (example will vary by implementation):

```bash
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"action":"ping"}' \
  https://mcp-server-xyz-uc.a.run.app/mcp/health-check
```

---

## 🚀 Usage (Local)

### Running the MCP Server

#### Option 1: Standard I/O Transport (Default)
```bash
python mcppoagent.py
```

#### Option 2: SSE Transport (HTTP)
```bash
# Set environment variable
export TRANSPORT_MODE=sse
python mcppoagent.py
```

#### Option 3: StreamableHTTP Transport
```bash
# Set environment variable
export TRANSPORT_MODE=streamable-http
python mcppoagent.py
```

## 📖 Tool Documentation

### Email & Document Processing

#### `fetch_emails()`
Fetches unread emails with attachments from Gmail inbox.
```python
# Returns JSON with emails containing attachments
result = await fetch_emails()
```

#### `parse_document(file_path, action="extract_po_data")`
Parses documents and extracts structured purchase order data.
```python
# Extract PO data from PDF
result = await parse_document("/path/to/po.pdf", "extract_po_data")
```

### Purchase Order Generation

#### `generate_purchase_order(supplier_name, items, **kwargs)`
Generates PDF purchase order documents.
```python
items = [
    {
        "item_code": "ITM001",
        "description": "Widget A",
        "quantity": 100,
        "unit_price": 25.50,
        "uom": "pcs",
        "urgency": "high"
    }
]
result = await generate_purchase_order("ABC Suppliers", items)
```

#### `generate_latex_po(supplier_name, items, **kwargs)`
Generates LaTeX purchase order documents.
```python
result = await generate_latex_po(
    "ABC Suppliers",
    items,
    delivery_date="2025-08-15",
    contact_email="supplier@example.com"
)
```

### Inventory & Financial Management

#### `analyze_inventory(analysis_type, category="", urgency_level="all")`
Analyzes inventory and provides restock information.
```python
# Check items needing restock
result = await analyze_inventory("restock_needed", urgency_level="critical")
```

#### `get_financial_data(query_type, amount=0.0)`
Gets financial data and approval status.
```python
# Check approval limits
result = await get_financial_data("approval_limits", 5000.0)
```

### Queue & Record Management

#### `manage_purchase_queue(action, request_data=None, request_id=None)`
Manages purchase request queue operations.
```python
# Add to queue
result = await manage_purchase_queue("add_to_queue", request_data)

# Get pending requests
result = await manage_purchase_queue("get_pending")
```

#### `manage_po_records(action, **kwargs)`
Manages PO record database operations.
```python
# Record a single PO
result = await manage_po_records("record_single_po", po_data=po_data)
```

### Email Communication

#### `generate_po_email(action, supplier_email, supplier_name, **kwargs)`
Generates and sends purchase order emails.
```python
result = await generate_po_email(
    "send_po_email",
    "supplier@example.com",
    "ABC Suppliers",
    po_number="PO-001",
    po_file_path="/path/to/po.pdf"
)
```

#### `send_response_email(subject, body, recipient_email, **kwargs)`
Sends custom email responses.
```python
result = await send_response_email(
    "PO Confirmation",
    "Your purchase order has been received.",
    "supplier@example.com"
)
```

### Utilities

#### `validate_po_items(items)`
Validates purchase order items format.
```python
result = await validate_po_items(items)
```

#### `create_sample_po_data(item_count=3, supplier_name="ABC Suppliers")`
Creates sample purchase order data for testing.
```python
result = await create_sample_po_data(5, "Test Supplier")
```

#### `save_report(file_path, data, **kwargs)`
Saves data to text files.
```python
result = await save_report("/path/to/report.txt", report_data, append=True)
```

## 🔧 Configuration Options

### Server Configuration
- **Port**: 8080 on Cloud Run (Dockerfile sets `EXPOSE 8080` and `PORT=8080`). For local dev you can keep 8099.
- **Transport**: Configure via `TRANSPORT_MODE` environment variable (`stdio`, `sse`, or `streamable-http`).
- **CORS**: If serving HTTP from Cloud Run, ensure CORS headers are added for ADK calls.
- **Debug**: Enable debug mode for development.

### Email Configuration
- **Gmail Integration**: Requires app-specific password
- **Email Templates**: Customizable email templates for different scenarios
- **Attachment Handling**: Automatic PDF attachment processing

### Database Configuration
- **MongoDB Atlas (Recommended)**: Managed MongoDB service for production
  - Connection string format: `mongodb+srv://username:password@cluster.mongodb.net/purchase_orders`
  - Automatic backups, scaling, and monitoring
- **Local MongoDB**: Default connection to localhost:27017 for development
- **Collections**: Automatic collection creation for PO records
- **Indexing**: Optimized indexes for query performance

### Document Processing
- **OCR Engine**: PaddleOCR for text extraction
- **AI Processing**: Google Generative AI for data extraction
- **LaTeX**: Full LaTeX document generation support

## 🛡️ Security Considerations

- **Environment Variables**: Store sensitive data in `.env` locally; use Cloud Run service-level env vars in production
- **Gmail App Passwords**: Use app-specific passwords, not account passwords
- **API Keys**: Secure storage of Google AI API keys
- **Database Access**: 
  - **MongoDB Atlas**: Use strong passwords, enable IP whitelisting, create database-specific users
  - **Connection Strings**: Never commit connection strings to version control
  - **Authentication**: Always enable authentication in production MongoDB instances
- **File Permissions**: Ensure proper file system permissions

## 🧪 Testing

### Sample Data Generation
```python
# Generate test data
result = await create_sample_po_data(3, "Test Supplier")

# Validate generated items
result = await validate_po_items(sample_items)
```

### Manual Testing
```python
# Test email fetching
emails = await fetch_emails()

# Test document parsing
parsed = await parse_document("test_po.pdf")

# Test PO generation
po = await generate_purchase_order("Test Corp", sample_items)
```

## 🐛 Troubleshooting

### Common Issues

#### MongoDB Connection Errors
```bash
# Check MongoDB status
mongosh --eval "db.adminCommand('ismaster')"

# Restart MongoDB service
sudo systemctl restart mongod
```

#### Gmail Authentication Errors
- Verify app-specific password is correct
- Ensure 2FA is enabled on Gmail account
- Check GMAIL_EMAIL and GMAIL_APP_PASSWORD environment variables

#### LaTeX Compilation Errors
```bash
# Test LaTeX installation
pdflatex --version

# Install missing packages (MiKTeX)
miktex packages install <package-name>
```

#### OCR Processing Issues
- Ensure sufficient system memory for PaddleOCR
- Verify image/PDF file accessibility
- Check Google AI API key validity

### Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 API Reference

### Response Format
All tools return JSON-formatted strings with consistent structure:

```json
{
  "status": "success|error",
  "message": "Descriptive message",
  "data": { /* Tool-specific data */ },
  "metadata": { /* Additional information */ }
}
```

### Error Handling
- **Validation Errors**: Detailed field-level validation messages
- **System Errors**: Graceful error handling with user-friendly messages
- **Retry Logic**: Automatic retries for transient failures

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make changes and add tests
4. Commit changes: `git commit -am 'Add new feature'`
5. Push to branch: `git push origin feature/new-feature`
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the API documentation

## 🔄 Version History

- **v0.1.0**: Initial release with core PO management features
- Features: Email monitoring, document processing, PO generation, inventory management

---

**Note**: This MCP server is designed to work with Model Context Protocol clients. Ensure your client supports MCP specification v0.1.0 or later.

---

## 🔗 Integration with This Repository (ADK + Next.js)

### Architecture Summary
- **Hosting**: MCP server runs on **Google Cloud Run** (managed, serverless HTTPS service)
- **Database**: MCP server connects to **MongoDB Atlas** (managed MongoDB database service)
- **MCP Tools**: Buyer/Supplier orchestrators in ADK call MCP tools via HTTPS

### Configuration

Set `MCP_SERVER_URL` in the ADK backend environment (local `.env` or deployment env vars):

```bash
MCP_SERVER_URL=https://mcp-server-xyz-uc.a.run.app/mcp
```

The supply chain buyer/supplier orchestrators call MCP tools via this URL. Frontend (Next.js on Vercel) does not call MCP directly; it talks to the ADK backend which invokes MCP tools.

### Deployment Order

1. **Set up MongoDB Atlas** → Get connection string (e.g., `mongodb+srv://...`)
2. **Deploy MCP server to Cloud Run** → Pass MongoDB Atlas connection string as env var → Capture Cloud Run URL
3. **Deploy ADK agents to Agent Engine** → Set `MCP_SERVER_URL` to Cloud Run URL
4. **Deploy Next.js to Vercel** → Point to ADK backend URL

### Troubleshooting 429 / Resource Limits
- If Agent Engine returns 429 RESOURCE_EXHAUSTED during heavy usage, add retries and reduce concurrency. The frontend now surfaces a friendly message instead of freezing.
#### Check service status
Test results: /mcp returns 406 (Not Acceptable), which means the endpoint exists but requires proper MCP protocol headers. This is expected.

FastMCP exposes the MCP protocol endpoint at /mcp. The 406 response indicates the endpoint exists; ADK's MCPToolset will send the correct headers.

Set MCP_SERVER_URL to include /mcp:
✅ CORRECT - Include /mcp path
MCP_SERVER_URL=https://mcp-server-uucrxxrxsq-uc.a.run.app/mcp

❌ WRONG - Base URL only
MCP_SERVER_URL=https://mcp-server-uucrxxrxsq-uc.a.run.app

- gcloud run services describe mcp-server --region us-central1 --project baseshare
#### MCP Server running on gcloud?
- gcloud run services logs read mcp-server --region us-central1 --project baseshare --limit 10 --format="table(timestamp,severity,textPayload)" 2>/dev/null | head -30

### Share
I just stood up a real, working multi‑agent system powered by Google ADK—now live with a 5‑mode UI (Auto, Planning, Docs Q&A, Buyer, Supplier). It answers from your Google Docs, plans complex goals and orchestrates end‑to‑end supply‑chain workflows using an MCP server on GCP Cloud Run for standardized tools like email, OCR, PO generation, and production queue updates.

What this unlocks
- Faster decisions: Plans in minutes, not days.
- Knowledge on tap: Trustworthy answers from your existing docs with citations.
- Operational lift: Buyer and Supplier agent clusters automate inventory checks, approvals, PO creation, order intake, and production scheduling.
- Scales securely: Serverless backend, standardized tool protocol (MCP), clean observability, and graceful error handling.
- Built for enterprise: Modular, multi‑agent architecture that slots into real workflows—today.

