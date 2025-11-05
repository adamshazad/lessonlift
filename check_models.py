import json
from google.oauth2 import service_account
import google.generativeai as genai

# Load your service account JSON
key_path = "/Users/adamshazad/Documents/lessonlift/gen-lang-client-0875480873-4b5bcde4f769.json"
creds = service_account.Credentials.from_service_account_file(key_path)
genai.configure(credentials=creds)

# List all available models
models = genai.list_models()
for m in models:
    if hasattr(m, "supported_methods") and "generateContent" in m.supported_methods:
        print("✅", m.name)
