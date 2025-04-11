import os
import requests
import certifi
from dotenv import load_dotenv
import urllib3
import PyPDF2
import datetime

# Disable insecure request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables from .env file
load_dotenv()

# Set SSL certificate environment variables before starting HTTPS connections
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

# Retrieve configuration from environment variables
tenant_id = os.getenv("TENANT_ID")
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
resource = os.getenv("RESOURCE")
deployment_name = os.getenv("DEPLOYMENT_NAME")
openai_api_base = os.getenv("OPENAI_API_BASE")
subscription_key = os.getenv("SUBSCRIPTION_KEY")

# Function to obtain an Azure AD access token
def get_access_token():
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
    return response.json().get("access_token")

# Function to log errors to a file
def log_error_to_file(error_message, response_text=None):
    log_folder = "error_logs"
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = os.path.join(log_folder, f"error_{timestamp}.log")
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(f"Error occurred at {timestamp}\n")
        f.write(f"Error message: {error_message}\n")
        if response_text:
            f.write(f"Response content:\n{response_text}\n")
    print(f"Error details logged to {log_file}")

# Class to handle OpenAI text generation requests
class OpenAITextGenerator:
    def __init__(self, api_base, deployment, access_token, subscription_key):
        self.api_base = api_base.rstrip("/")  # remove trailing slash if present
        self.deployment = deployment
        self.access_token = access_token
        self.subscription_key = subscription_key
        self.api_version = "2024-07-01-preview"
    
    def send_request(self, system_message, user_message):
        api_url = f"{self.api_base}/deployments/{self.deployment}/chat/completions?api-version={self.api_version}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Ocp-Apim-Subscription-Key": self.subscription_key,
            "Content-Type": "application/json",
            "api-key": self.access_token
        }
        data = {
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
        }
        try:
            response = requests.post(api_url, headers=headers, json=data, verify=False)
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
            result = response.json()
            return result['choices'][0]['message']['content']
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            print(f"Response content: {response.text}")
            log_error_to_file(str(http_err), response.text)
        except requests.exceptions.RequestException as req_err:
            print(f"Request error occurred: {req_err}")
            log_error_to_file(str(req_err))
        except KeyError as key_err:
            print(f"Unexpected response format: {key_err}")
            log_error_to_file(str(key_err), response.text)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            log_error_to_file(str(e))


# Function to list all txt files in a given folder
def list_txt_files(folder_path):
    files = []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".txt") and filename.lower() != "pre_paper_prompt.txt":
            files.append(filename)
    files.sort()
    return files

# Function to list all pdf files in a given folder
def list_pdf_files(folder_path):
    pdfs = []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".pdf"):
            pdfs.append(filename)
    pdfs.sort()
    return pdfs

# Function to extract text from a PDF file using PyPDF2
def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text

def main():
    access_token_value = get_access_token()
    
    # Define folder paths
    prompt_folder = os.path.join("C:\\", "python_scripts", "azureOpenaiChatBasic", "system_prompt")
    paper_folder = os.path.join("C:\\", "python_scripts", "azureOpenaiChatBasic", "paper")
    output_folder = os.path.join("C:\\", "python_scripts", "azureOpenaiChatBasic", "output")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Function to select a system prompt file; returns tuple(system_message, filename)
    def select_system_prompt():
        txt_files = list_txt_files(prompt_folder)
        print("Select a system prompt file by entering its number:")
        for idx, filename in enumerate(txt_files, start=1):
            print(f"{idx}: {filename}")
        selected_num = int(input("Enter the number: "))
        selected_file = txt_files[selected_num - 1]
        system_prompt_path = os.path.join(prompt_folder, selected_file)
        with open(system_prompt_path, "r", encoding="utf-8") as f:
            return f.read(), selected_file
    
    # Select system prompt for the first time
    system_message, system_filename = select_system_prompt()
    
    # Global variable to store extracted PDF text (if any)
    extracted_pdf_text = None
    pdf_title = None
    
    # If paper_summarizer.txt is selected, handle PDF summarization
    if system_filename.lower() == "paper_summarizer.txt":
        pdf_files = list_pdf_files(paper_folder)
        if not pdf_files:
            print("No PDF files found in the paper folder.")
        else:
            print("Select a PDF file by entering its number:")
            for idx, pdf_filename in enumerate(pdf_files, start=1):
                print(f"{idx}: {pdf_filename}")
            selected_pdf_num = int(input("Enter the number: "))
            selected_pdf_file = pdf_files[selected_pdf_num - 1]
            pdf_path = os.path.join(paper_folder, selected_pdf_file)
            extracted_pdf_text = extract_text_from_pdf(pdf_path)
            # Use the PDF file name (without extension) as the paper title
            pdf_title = os.path.splitext(selected_pdf_file)[0]
            if extracted_pdf_text:
                print("Summarizing paper...")
                # Use paper_summarizer.txt as the system message and extracted PDF text as the prompt
                temp_generator = OpenAITextGenerator(openai_api_base, deployment_name, access_token_value, subscription_key)
                response = temp_generator.send_request(system_message, extracted_pdf_text)
                print("Summarization Response:")
                print(response)
                # Save the summarization response to a txt file with filename "summary_<pdf_title>.txt"
                output_path = os.path.join(output_folder, "summary_" + pdf_title + ".txt")
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(response)
                print(f"Summarization output saved as: {output_path}")
                print()
    else:
        # For non-paper_summarizer.txt system prompts, immediately prompt for user input
        generator = OpenAITextGenerator(openai_api_base, deployment_name, access_token_value, subscription_key)
        while True:
            user_message = input("Enter your prompt (type 'exit' to return to menu): ")
            if user_message.strip().lower() == "exit":
                break
            response = generator.send_request(system_message, user_message)
            responseLabel = "\n" + "Response:"
            print(responseLabel)
            print(response)
            print()
    
    # Instantiate the text generator for conversation
    generator = OpenAITextGenerator(openai_api_base, deployment_name, access_token_value, subscription_key)
    
    while True:
        # Display conversation option menu
        print("Select an option:")
        print("1: Change system prompt file")
        print("2: Use the same system prompt for another prompt.")
        if system_filename.lower() == "paper_summarizer.txt" and extracted_pdf_text:
            print("3: Chat with PDF text")
            print("4: Exit conversation")
        else:
            print("3: Exit conversation")
            
        choice = input("Enter your choice: ")
        if choice == "1":
            # Change system prompt file and update system_message and system_filename
            system_message, system_filename = select_system_prompt()
            if system_filename.lower() == "paper_summarizer.txt":
                pdf_files = list_pdf_files(paper_folder)
                if not pdf_files:
                    print("No PDF files found in the paper folder.")
                    extracted_pdf_text = None
                else:
                    print("Select a PDF file by entering its number:")
                    for idx, pdf_filename in enumerate(pdf_files, start=1):
                        print(f"{idx}: {pdf_filename}")
                    selected_pdf_num = int(input("Enter the number: "))
                    selected_pdf_file = pdf_files[selected_pdf_num - 1]
                    pdf_path = os.path.join(paper_folder, selected_pdf_file)
                    extracted_pdf_text = extract_text_from_pdf(pdf_path)
                    pdf_title = os.path.splitext(selected_pdf_file)[0]
            else:
                # Prompt user for input if non-paper_summarizer.txt is selected
                while True:
                    user_message = input("Enter your prompt (type 'exit' to return to menu): ")
                    if user_message.strip().lower() == "exit":
                        break
                    response = generator.send_request(system_message, user_message)
                    responseLabel = "\n" + "Response:"
                    print(responseLabel)
                    print(response)
                    print()
        elif choice == "2":
            # For paper_summarizer.txt mode, re-select PDF file and summarize it
            if system_filename.lower() == "paper_summarizer.txt":
                pdf_files = list_pdf_files(paper_folder)
                if not pdf_files:
                    print("No PDF files found in the paper folder.")
                    extracted_pdf_text = None
                else:
                    print("Select a PDF file by entering its number:")
                    for idx, pdf_filename in enumerate(pdf_files, start=1):
                        print(f"{idx}: {pdf_filename}")
                    selected_pdf_num = int(input("Enter the number: "))
                    selected_pdf_file = pdf_files[selected_pdf_num - 1]
                    pdf_path = os.path.join(paper_folder, selected_pdf_file)
                    extracted_pdf_text = extract_text_from_pdf(pdf_path)
                    pdf_title = os.path.splitext(selected_pdf_file)[0]
                    if extracted_pdf_text:
                        print("Summarizing paper...")
                        temp_generator = OpenAITextGenerator(openai_api_base, deployment_name, access_token_value, subscription_key)
                        response = temp_generator.send_request(system_message, extracted_pdf_text)
                        print("Summarization Response:")
                        print(response)
                        output_path = os.path.join(output_folder, "summary_" + pdf_title + ".txt")
                        with open(output_path, "w", encoding="utf-8") as f:
                            f.write(response)
                        print(f"Summarization output saved as: {output_path}")
                        print()
            else:
                # Prompt user for input if non-paper_summarizer.txt is selected
                while True:
                    user_message = input("Enter your prompt (type 'exit' to return to menu): ")
                    if user_message.strip().lower() == "exit":
                        break
                    response = generator.send_request(system_message, user_message)
                    responseLabel = "\n" + "Response:"
                    print(responseLabel)
                    print(response)
                    print()
        elif choice == "3" and system_filename.lower() != "paper_summarizer.txt":
            print("Exiting conversation.")
            break
        elif choice == "4" and system_filename.lower() == "paper_summarizer.txt":
            print("Exiting conversation.")
            break
        elif choice == "3" and system_filename.lower() == "paper_summarizer.txt" and extracted_pdf_text:
            # Option 3: Update system prompt for PDF chat and enter a dedicated conversation loop
            pre_prompt_path = os.path.join(prompt_folder, "pre_paper_prompt.txt")
            if os.path.exists(pre_prompt_path):
                with open(pre_prompt_path, "r", encoding="utf-8") as f:
                    pre_prompt = f.read()
                system_message = pre_prompt + "\n" + extracted_pdf_text
                print("System prompt updated for chatting with PDF text.")
                # Start inner conversation loop for PDF chat (exits when user types 'exit')
                while True:
                    user_message = input("Enter your prompt (type 'exit' to return to menu): ")
                    if user_message.strip().lower() == "exit":
                        break
                    response = generator.send_request(system_message, user_message)
                    responseLabel = "\n" + "Response:"
                    print(responseLabel)
                    print(response)
                    print()
            else:
                print("pre_paper_prompt.txt not found in system_prompt folder. Cannot update system prompt.")
        else:
            print("Invalid choice. Exiting conversation.")
            break

if __name__ == "__main__":
    main()