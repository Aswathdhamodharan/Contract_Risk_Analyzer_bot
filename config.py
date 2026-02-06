import os

# API Key Configuration
# Users should replace this with their actual key or set it in the UI/Environment
# The app logic will prefer the key from the UI sidebar if provided
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "YOUR_API_KEY_HERE")

# Model Configuration
GEMINI_MODEL = "gemini-1.5-flash" # Cost-effective and fast model suitable for hackathon 

# App Settings
APP_TITLE = "Legalis - AI Contract Risk Bot"
APP_ICON = "⚖️"
