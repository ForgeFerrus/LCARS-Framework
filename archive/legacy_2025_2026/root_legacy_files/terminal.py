import json

import requests

API_KEY = "sk-nry-iHDzgOa5Jbuje-dZX5TOSpiq70IWHoPWPLtolDlJM_I"   # встав свій ключ
ENDPOINT = "https://router.bynara.id/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "model": "mistral-large",   # або інша доступна модель
    "messages": [
        {"role": "system", "content": "Ти — LCARS Interface."},
        {"role": "user", "content": "Привіт, поясни мені як працює LCARS."}
    ]
}

response = requests.post(ENDPOINT, headers=headers, json=payload)

if response.status_code == 200:
    data = response.json()
    print(data["choices"][0]["message"]["content"])
else:
    print("Error:", response.status_code, response.text)


# CLI loop
while True:
    cmd = input("LCARS> ")
    payload["messages"].append({"role": "user", "content": cmd})
    print(requests.post(ENDPOINT, headers=headers, json=payload))
