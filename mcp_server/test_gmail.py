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