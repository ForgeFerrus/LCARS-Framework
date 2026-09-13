import requests, os
from dotenv import load_dotenv

load_dotenv(dotenv_path="C:/Users/Forge/MyProject/LCARS-Framework/.env")
API_KEY = os.environ.get("GROQ_API_KEY")
url = "https://api.groq.com/openai/v1/models"
headers = {"Authorization": f"Bearer {API_KEY}"}
r = requests.get(url, headers=headers)
print(f"[DEBUG] API_KEY={API_KEY}")
print(r.status_code, r.json())
