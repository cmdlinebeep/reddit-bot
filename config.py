import os

# Get environment secret GLOBALS
if not os.getenv("REDDIT_PASSWORD"):
    raise RuntimeError("REDDIT_PASSWORD is not set")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")

if not os.getenv("REDDIT_CLIENT_SECRET"):
    raise RuntimeError("REDDIT_CLIENT_SECRET is not set")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")

if not os.getenv("MAILJET_API_KEY"):
    raise RuntimeError("MAILJET_API_KEY is not set")
MAILJET_API_KEY = os.getenv("MAILJET_API_KEY")

if not os.getenv("MAILJET_API_SECRET"):
    raise RuntimeError("MAILJET_API_SECRET is not set")
MAILJET_API_SECRET = os.getenv("MAILJET_API_SECRET")


FROM_EMAIL = "xxx_FROM_EMAIL_HERE_xxx"  # Sending email authorized with MailJet
TO_EMAIL = "xxx_YOUR_EMAIL_HERE_xxx"    # Admin to be notified