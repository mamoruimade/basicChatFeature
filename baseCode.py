import os
import requests
from dotenv import load_dotenv  
import certifi



load_dotenv()

tenant_id = os.getenv("TENANT_ID")
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
resource = os.getenv("RESOURCE")
deployment_name = os.getenv("DEPLOYMENT_NAME")
openai_api_base = os.getenv("OPENAI_API_BASE")
subscription_key = os.getenv("SUBSCRIPTION_KEY")


os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"

token_data = {
    "grant_type": "client_credentials",
    "client_id": client_id,
    "client_secret": client_secret,
    "scope": resource + ".default"
}

token_headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}

response = requests.post(token_url, data=token_data, headers=token_headers)
response.raise_for_status()
access_token = response.json().get("access_token")

# print(access_token)

system_prompt_path = os.path.join("C:\\", "python_scripts", "azureOpenaiChatBasic", "system_prompt", "systemPrompt.txt")
with open(system_prompt_path, "r", encoding="utf-8") as f:
    system_prompt = f.read()

api_url = f"{openai_api_base}/deployments/{deployment_name}/chat/completions?api-version=2024-07-01-preview"
headers = {
    "Authorization": f"Bearer {access_token}",
    "Ocp-Apim-Subscription-Key": subscription_key,
    "Content-Type": "application/json",
    "api-key": access_token
}
 
data = {
    "messages": [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": "Explain Atmic layer Deposition in 50 words."
        }
    ]
}
 
# Make the request to the Azure OpenAI API
response = requests.post(api_url, headers=headers, json=data, verify=False)
response.raise_for_status()
result = response.json()

final_results=result['choices'][0]['message']['content']

# Print the response
print(final_results)

