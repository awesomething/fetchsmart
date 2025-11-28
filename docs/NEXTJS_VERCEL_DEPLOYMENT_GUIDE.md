# Next.js Frontend Deployment Guide - Vercel

## Overview
This guide explains how to deploy your Next.js frontend to Vercel and configure it to connect to your deployed ADK agent backend. The frontend automatically detects the deployment environment and configures endpoints accordingly.

## Architecture: Hybrid Web + Local Electron Service

**Single Next.js Deployment on Vercel with Floating Window Support**

Your Next.js app is deployed **once** to Vercel as a web application. The floating window functionality works through a **local Electron companion service** that users run on their machines.

### How It Works

1. **Web App (Vercel)**: Your Next.js app is deployed to Vercel and accessible via browser
2. **Local Electron Service**: Users install and run the Electron service locally (runs on `http://127.0.0.1:6415`)
3. **Communication**: When users click "Open in Floating Window" in the web UI, the Vercel-deployed app makes HTTP requests to the local Electron service
4. **Floating Windows**: The local Electron service creates floating windows on the user's desktop

### User Experience

- Users access your app via browser (deployed on Vercel)
- If they want floating window functionality, they install and run the Electron service locally
- The web app automatically detects if the Electron service is running
- Floating window buttons work seamlessly when the service is available

## Prerequisites

### 1. Vercel Account Setup
1. Go to [vercel.com](https://vercel.com) and sign up/sign in
2. Connect your GitHub/GitLab/Bitbucket account


### 2. Backend Deployment
Your Next.js frontend needs a backend to connect to:
- **Agent Engine** - Follow the [ADK Deployment Guide](./ADK_DEPLOYMENT_GUIDE.md)


## Environment Variables by Deployment Type

The frontend automatically detects which backend type to use based on available environment variables. Here's what you need for each deployment scenario:

### 🚀 Agent Engine Backend (Recommended)

**Required Variables:**
```bash
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
REASONING_ENGINE_ID=your-reasoning-engine-id
GOOGLE_SERVICE_ACCOUNT_KEY_BASE64=your-base64-encoded-service-account-key
ADK_APP_NAME=your-adk-app-name
AGENT_ENGINE_ENDPOINT=your-agent-engine-endpoint
GOOGLE_CLOUD_LOCATION=us-central1
```

**How to get these values:**
1. **GOOGLE_CLOUD_PROJECT**: Your Google Cloud project ID
2. **REASONING_ENGINE_ID**: From your ADK deployment output (e.g., `projects/123/locations/us-central1/reasoningEngines/abc123` → use `abc123`)
3. **GOOGLE_CLOUD_LOCATION**: Region where you deployed your agent (default: `us-central1`)
4. **GOOGLE_SERVICE_ACCOUNT_KEY_BASE64**: Base64-encoded service account key (see setup instructions below)

## Service Account Setup for Agent Engine

If you're using Agent Engine backend, you need to create a Google Cloud service account and configure authentication. This is required for the frontend to authenticate with Google Cloud's Vertex AI API.

### Step 1: Create Service Account

1. **Go to Google Cloud Console:**
   - Navigate to [Google Cloud Console](https://console.cloud.google.com)
   - Select your project (the same one where you deployed your ADK agent)

2. **Navigate to Service Accounts:**
   - Go to **IAM & Admin** → **Service Accounts**
   - Click **"Create Service Account"**

3. **Configure Service Account:**
   - **Service account name**: `agent-engine-frontend` (or any descriptive name)
   - **Service account ID**: Will be auto-generated
   - **Description**: `Service account for frontend to access Agent Engine`
   - Click **"Create and Continue"**

4. **Add Required Roles:**
   Add these roles to your service account:
   - **Vertex AI User** (`roles/aiplatform.user`) - Required for Agent Engine API access
   - **Service Account Token Creator** (`roles/iam.serviceAccountTokenCreator`) - Required for token generation
   
   Click **"Continue"** then **"Done"**

### Step 2: Generate Service Account Key

1. **Access Service Account:**
   - In the Service Accounts list, click on the service account you just created
   - Go to the **"Keys"** tab

2. **Create New Key:**
   - Click **"Add Key"** → **"Create new key"**
   - Select **"JSON"** as the key type
   - Click **"Create"**

3. **Download Key:**
   - The JSON key file will be automatically downloaded to your computer
   - **Important**: Store this file securely and never commit it to version control

### Step 3: Convert JSON Key to Base64

You need to convert the JSON key to base64 for safe storage in environment variables.

**Option A: Using Terminal/Command Line (Recommended)**

```bash
# On macOS/Linux
cat path/to/your-service-account-key.json | base64

# On Windows (PowerShell)
[Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes((Get-Content path/to/your-service-account-key.json -Raw)))
```

**Option B: Using Node.js**

```javascript
const fs = require('fs');
const keyFile = fs.readFileSync('path/to/your-service-account-key.json', 'utf8');
const base64Key = Buffer.from(keyFile).toString('base64');
console.log(base64Key);
```

**Option C: Using Online Tool**

1. Go to [base64encode.org](https://www.base64encode.org/)
2. Copy the entire contents of your JSON key file
3. Paste it into the encoder
4. Copy the base64 output


**For Vercel Production:**
1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Add a new environment variable:
   - **Name**: `GOOGLE_SERVICE_ACCOUNT_KEY_BASE64`
   - **Value**: The base64 string you generated
   - **Environments**: Select Production, Preview, and Development


## Deploy via Vercel Dashboard (Recommended)

1. **Import Your Repository:**
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your Git repository
   - Select the `nextjs` folder as the root directory

2. **Configure Build Settings:**
   - **Framework Preset**: Next.js
   - **Root Directory**: `nextjs`
   - **Build Command**: `npm run build`
   - **Output Directory**: Leave empty (uses default)
   - **Note**: The Electron folder (`nextjs/electron/`) is included in the build but not executed on Vercel - it's only used when users run the Electron service locally

3. **Set Environment Variables:**
   - In project settings, go to "Environment Variables"
   - Add your variables based on your backend type (see sections above)
   - Set for "Production", "Preview", and "Development" as needed

4. **Deploy:**
   - Click "Deploy"
   - Vercel will build and deploy your app

## Electron Floating Window Service (Local Companion)

The Electron service (`nextjs/electron/`) is a **local companion** that users run on their machines to enable floating window functionality from your Vercel-deployed web app.

### How the Integration Works

1. **Web App (Vercel)**: Deployed Next.js app includes floating window UI buttons
2. **Local Service**: Users run Electron service locally (optional)
3. **Communication**: Web app detects and communicates with local service via `http://127.0.0.1:6415`
4. **Floating Windows**: When users click "Open in Floating Window", the web app sends HTTP requests to the local Electron service

### Configuration in Next.js App

The web app uses this environment variable to connect to the local Electron service:

```bash
# Optional: Custom port (default: 127.0.0.1:6415)
NEXT_PUBLIC_FLOATING_WINDOW_SERVICE_URL=http://127.0.0.1:6415
```

**For Vercel Deployment:**
- This environment variable is optional
- If not set, defaults to `http://127.0.0.1:6415`
- The web app gracefully handles when the Electron service is not running (opens in new tab instead)

### Building Electron Service for Distribution

To create distributable Electron service installers for your users:

1. **Install electron-builder** (if not already installed):
   ```bash
   cd nextjs
   npm install --save-dev electron-builder
   ```

2. **Configure electron-builder** in `nextjs/package.json`:
   ```json
   {
     "build": {
       "appId": "com.yourcompany.recruitment-floating-windows",
       "productName": "Recruitment Floating Windows",
       "directories": {
         "output": "dist-electron"
       },
       "files": [
         "electron/**/*",
         "package.json"
       ],
       "win": {
         "target": ["nsis"],
         "icon": "electron/icon.ico"
       },
       "mac": {
         "target": ["dmg"],
         "icon": "electron/icon.icns"
       },
       "linux": {
         "target": ["AppImage"],
         "icon": "electron/icon.png"
       }
     }
   }
   ```

3. **Build the Electron service**:
   ```bash
   npm run electron:build
   ```

4. **Distribution files** will be created in `nextjs/dist-electron/`:
   - Windows: `.exe` installer
   - macOS: `.dmg` disk image
   - Linux: `.AppImage` executable

5. **Distribute to users**: Share the installer files so users can install and run the Electron service locally

### Development

For local development, run both services:

```bash
# Terminal 1: Start Next.js dev server
cd nextjs
npm run dev

# Terminal 2: Start Electron service
cd nextjs
npm run electron:service
```

### User Instructions

Provide these instructions to users who want floating window functionality:

1. **Download and install** the Electron service installer for their OS
2. **Run the Electron service** (it will start automatically on port 6415)
3. **Access your web app** on Vercel via browser
4. **Click "Open in Floating Window"** buttons in the UI
5. The web app will automatically detect and use the local Electron service

### Important Notes

- **Single Vercel Deployment**: Deploy your Next.js app once to Vercel - no separate deployment needed
- **Electron is Optional**: The web app works perfectly without Electron (floating window buttons open in new tabs instead)
- **Local Service Only**: Electron service runs on users' machines, not on Vercel
- **Automatic Detection**: The web app automatically detects if Electron service is running
- **Graceful Fallback**: If Electron service is not running, floating window buttons open in regular browser tabs

