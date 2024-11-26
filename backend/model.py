import os
import requests

# Configura el caché en el disco D
os.environ["HF_HOME"] = "D:/huggingface_cache"
os.environ["HUGGINGFACE_HUB_CACHE"] = "D:/huggingface_cache"

API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.1-405B"
headers = {"Authorization": "Bearer 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"}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    print("Status Code:", response.status_code)  # Esto te dará el código de estado de la respuesta
    print("Response Headers:", response.headers)  # Esto puede proporcionar detalles útiles sobre la respuesta
    return response.json()

output = query({
    "inputs": "Can you please let us know more details about your? ",
})
print("Output:", output) 
