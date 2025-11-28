# MCP Server Local Testing Guide

## 🎯 Purpose

Test the MCP server locally before deploying to Cloud Run. This ensures all tools work correctly and dependencies are properly configured.

## 📋 Prerequisites

Before testing locally, ensure you have:

1. **Python 3.11+** installed
2. **MongoDB** running (Atlas or local)
3. **LaTeX** installed (for PDF generation)
4. **Gmail App Passwords** configured
5. **Google AI API Key**

## 🚀 Local Setup

### 1. Create Virtual Environment

```bash
cd mcp_server/

# Create virtual environment
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt
```

If `requirements.txt` is empty or incomplete, install these core dependencies:

```bash
pip install fastmcp python-dotenv requests google-generativeai paddleocr paddlepaddle pymongo
```

### 3. Create Local Environment File

Create `mcp_server/.env` (this file is gitignored):

```env
# Gmail Configuration (Buyer/Company Email)
GMAIL_EMAIL=your-buyer-email@gmail.com
GMAIL_APP_PASSWORD=your-16-char-app-password
email=your-buyer-email@gmail.com
password=your-16-char-app-password

# Supplier Email Configuration
supemail=supplier-email@gmail.com
suppassword=supplier-16-char-app-password

# Google AI Configuration
GOOGLE_API_KEY=your-google-ai-api-key

# MongoDB Configuration
# Option 1: MongoDB Atlas (Recommended)
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/purchase_orders
MONGODB_DATABASE=purchase_orders

# Option 2: Local MongoDB
# MONGODB_URI=mongodb://localhost:27017
# MONGODB_DATABASE=purchase_orders

# Server Configuration (Local Testing)
MCP_SERVER_PORT=8099
TRANSPORT_MODE=stdio

# Company Information
COMPANY_NAME=Test Company Inc
COMPANY_ADDRESS=123 Test Street, Test City
COMPANY_EMAIL=company@test.com
```

### 4. Verify MongoDB Connection

**If using MongoDB Atlas:**
1. Go to your cluster → Connect → Connect your application
2. Copy the connection string
3. Replace `<password>` with your database user password
4. Paste into `MONGODB_URI` in `.env`

**If using Local MongoDB:**
```bash
# Check if MongoDB is running
mongosh --eval "db.adminCommand('ismaster')"

# If not running:
# Windows: Start MongoDB service from Services
# macOS: brew services start mongodb-community
# Linux: sudo systemctl start mongod
```

### 5. Test Individual Components

#### Test MongoDB Connection
```python
# test_mongo.py
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

try:
    client = MongoClient(os.getenv("MONGODB_URI"))
    db = client[os.getenv("MONGODB_DATABASE")]
    print("✅ MongoDB connected!")
    print(f"Collections: {db.list_collection_names()}")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
```

Run:
```bash
python test_mongo.py
```

#### Test Gmail Authentication
```python
# test_gmail.py
import imaplib
import os
from dotenv import load_dotenv

load_dotenv()

try:
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(os.getenv("GMAIL_EMAIL"), os.getenv("GMAIL_APP_PASSWORD"))
    print("✅ Gmail authentication successful!")
    mail.logout()
except Exception as e:
    print(f"❌ Gmail authentication failed: {e}")
```

Run:
```bash
python test_gmail.py
```

#### Test Google AI API
```python
# test_google_ai.py
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Hello, test!")
    print("✅ Google AI API working!")
    print(f"Response: {response.text[:100]}...")
except Exception as e:
    print(f"❌ Google AI API failed: {e}")
```

Run:
```bash
python test_google_ai.py
```

### 6. Run the MCP Server Locally

```bash
# Make sure you're in mcp_server/ with .venv activated
python mcppoagent.py
```

Expected output:
```
All tools initialized successfully.
MCP server running on port 8099...
```

### 7. Test MCP Tools (Two Options)

#### Option A: Direct Tool Testing (Simplest - Recommended)

Test individual tool classes directly without running the MCP server:

```bash
cd mcp_server/

# Test inventory analysis
python -c "from restock_inventory_tool import RestockInventoryTool; tool = RestockInventoryTool(); print(tool.analyze_inventory('restock_needed', urgency_level='all'))"

# Test financial data
python -c "from financial_tool import FinancialDataTool; tool = FinancialDataTool(); print(tool.get_financial_data('approval_limits', 5000))"

# Test report saving
python -c "from report_file_tool import ReportFileTool; tool = ReportFileTool(); print(tool.save_report('test_report.txt', 'Test data'))"

# Test purchase queue
python -c "from purchase_queue_tool import PurchaseQueueTool; tool = PurchaseQueueTool(); print(tool.manage_queue('get_pending'))"

# Test email response generator (simple test)
python -c "from email_response_tool import EmailResponseGenerator; tool = EmailResponseGenerator(); print('✅ Email tool initialized:', tool.name)"
```

**Benefits:**
- ✅ No MCP server needed
- ✅ Tests core tool logic directly
- ✅ Faster iteration for debugging
- ✅ Verifies all dependencies work

#### Option B: MCP Inspector (Full Server Testing)

Test through the MCP server with MCP Inspector UI:

**Start the Inspector:**
```bash
cd mcp_server/
npx @modelcontextprotocol/inspector python mcppoagent.py
```

**Open Inspector:**
- Browser automatically opens at `http://localhost:6274`
- Or manually open: `http://localhost:6274`

**Configure Connection:**
- Transport Type: `Streamable HTTP`
- URL: `http://127.0.0.1:8099/sse`
- Click **Connect**

**Test Tools in UI:**
- All 14 tools will be listed
- Click any tool to see parameters
- Fill in parameters and click "Run"
- View real-time request/response

**Benefits:**
- ✅ Tests full MCP server protocol
- ✅ Visual interface for tool testing
- ✅ Matches production Cloud Run behavior
- ✅ Great for demo/presentation


## 🐛 Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'pip'`

Your Python installation is missing pip. Fix:

```bash
# Windows - download and run get-pip.py
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py

# Or reinstall Python with pip included
```

### Issue: `requirements.txt` is Empty

The file exists but has no content. Manually install dependencies:

```bash
pip install fastmcp python-dotenv requests google-generativeai paddleocr paddlepaddle pymongo
```

Then generate a proper requirements file:

```bash
pip freeze > requirements.txt
```

### Issue: MongoDB Connection Refused

```bash
# Check if MongoDB is running
# Windows:
# Open Services → Find MongoDB → Start

# macOS:
brew services start mongodb-community

# Linux:
sudo systemctl start mongod
sudo systemctl status mongod
```

### Issue: Gmail Authentication Error

1. Verify 2FA is enabled on your Gmail account
2. Generate a new App Password:
   - Google Account → Security → 2-Step Verification → App passwords
3. Copy the 16-character code (no spaces)
4. Update `.env` file with the new password

### Issue: LaTeX Not Found

PDF generation will fail if LaTeX isn't installed:

```bash
# Windows - Install MiKTeX
# Download from: https://miktex.org/download

# macOS
brew install --cask mactex

# Ubuntu/Debian
sudo apt-get install texlive-full

# Test installation
pdflatex --version
```

### Issue: Port 8099 Already in Use

```bash
# Windows
netstat -ano | findstr :8099
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:8099 | xargs kill -9

# Or change port in mcppoagent.py:
# mcp = FastMCP("potool", port=8100)
```

## ✅ Pre-Deployment Checklist

Before deploying to Cloud Run, verify:

- [ ] All test scripts pass without errors
- [ ] MongoDB Atlas connection string works
- [ ] Gmail authentication succeeds
- [ ] Google AI API key is valid
- [ ] Sample PO data can be created
- [ ] Inventory analysis returns results
- [ ] Email fetching works (if emails exist)
- [ ] PO generation completes (if LaTeX installed)
- [ ] No sensitive data in code (use env vars)
- [ ] `.env` file is NOT committed to git
- [ ] All tool endpoints respond correctly

## 📚 Documentation

- **Full Testing Guide**: [`mcp_server/LOCAL_TESTING.md`](./mcp_server/LOCAL_TESTING.md)
- **MCP Server Features**: [`mcp_server/README.md`](./mcp_server/README.md)
- **MongoDB Setup**: [`mcp_server/MONGO.MD`](./mcp_server/MONGO.MD)
- **Integration Plan**: [`google-docs-q-a-bot.plan.md`](./google-docs-q-a-bot.plan.md)
  
## 🚀 Deploy to Cloud Run

Once local testing passes:

```bash
# Deactivate virtual environment
deactivate

# Navigate back to repo root
cd ..

# Deploy using the guide in README.md
# Section: "☁️ Cloud Run Deployment"
```

Remember to pass environment variables during Cloud Run deployment!

## 📚 Next Steps

After local testing and Cloud Run deployment:

1. **Integrate with ADK**: Set `MCP_SERVER_URL` in ADK backend
2. **Deploy ADK Agents**: Deploy buyer/supplier orchestrators
3. **Test End-to-End**: Use frontend UI to trigger workflows
4. **Monitor Logs**: Check Cloud Run logs for issues

## 🔗 Related Documentation

- [MCP Server README](./README.md) - Full feature documentation
- [MongoDB Setup Guide](./MONGO.MD) - Detailed MongoDB configuration
- [Main Project README](../README.md) - Integration with ADK
- [Supply Chain Integration Plan](../google-docs-q-a-bot.plan.md) - Full architecture

## Buyer mode sample questions

**Inventory checks:**
- "Check inventory levels for office supplies"
- "What items need restocking?"
- "Show me inventory status for electronics"
- "Analyze inventory and identify items below threshold"
- "Generate an inventory report"

**Purchase validation:**
- "Validate a purchase request for 50 laptops at $800 each"
- "Check if we have budget for office furniture purchase worth $5000"
- "Can I approve a purchase order for $10,000 in office supplies?"
- "Verify budget availability for purchasing new monitors"

**Purchase order generation:**
- "Create a purchase order for 100 units of office chairs from Supplier Tech Hardware"
- "Generate a PO for 25 laptops, delivery needed by end of month"
- "Create purchase order: 50 notebooks, unit price $5.99, supplier Paper Corp"
- "I need to order office supplies - generate the purchase order"

**End-to-end buyer workflow:**
- "Check inventory, validate purchase, and create PO for office supplies"
- "I need office supplies restocked - handle the full buyer workflow"
- "Process a purchase: analyze inventory, check budget, generate PO"

## Supplier mode sample questions

**Order processing:**
- "Check for incoming purchase orders in my email"
- "Process new purchase orders from emails"
- "Monitor incoming orders and extract order details"
- "Fetch and parse purchase order documents from email"

**Production queue:**
- "Show me the current production queue"
- "What orders are pending in production?"
- "Record a new purchase order in the production system"
- "Update production schedule for pending orders"

**Order confirmations:**
- "Send confirmation email for order PO-001"
- "Generate order confirmation for recently received purchase order"
- "Confirm receipt of order and send acknowledgment to customer"

**End-to-end supplier workflow:**
- "Process incoming purchase orders and add them to production queue"
- "Monitor emails for new orders, extract details, and schedule production"
- "Handle incoming order: extract information and send confirmation"

## Testing tips

1. Start simple: "Check inventory levels" (Buyer) or "Show production queue" (Supplier)
2. Then try workflows: "Process a purchase order" (Buyer) or "Monitor incoming orders" (Supplier)
3. Test mode directives work by selecting Buyer/Supplier in the UI
4. Verify MCP tools: questions should trigger actual MCP server calls

Use these to validate routing, MCP integration, and workflow coordination.

Test Use one of these queries to trigger email sending:

**Simple query (minimal details):**
```
Send a purchase order email to <your-email> for Supplier Tech Hardware. Items: 20 units of 27" 4K Monitor at $299 each, 20 units of Mechanical Keyboard at $89.50 each. Total should be under $9000.
```

**Slightly more detailed:**
```
Create and send a purchase order to <youremail>@email.com (Supplier Tech Hardware). Order 20 units of 27" 4K Monitor ($299 each) and 20 units of Mechanical Keyboard ($89.50 each). Include delivery date in 2 weeks and mark as urgent.
```

**Most detailed (for complete testing):**
```
Send a purchase order email to <youremail>@email.com for Supplier Tech Hardware. Purchase 20 units of 27" 4K Monitor (MON-27-4K) at $299.00 each, and 20 units of Mechanical Keyboard (KB-MECH-US) at $89.50 each. Delivery date: 2 weeks from now. This is urgent.
```

**Why these work:**
- Includes `supplier_email` <youremail>@email.com
- Includes `supplier_name` (Supplier Tech Hardware, from the agent's instruction)
- Lists items with quantities and prices
- Mentions urgency if needed

The purchase order agent should route to Buyer mode and use `generate_po_email` with action="send_po_email" to send the email.
