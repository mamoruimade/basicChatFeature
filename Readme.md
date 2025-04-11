# Azure OpenAI Chat Basic

This project provides a Python script (`main.py`) to interact with Azure OpenAI services. It allows users to summarize PDF files, generate text responses based on system prompts, and log errors for debugging.

## Features

- Summarize PDF files using a predefined system prompt (`paper_summarizer.txt`).
- Generate text responses based on custom system prompts.
- Log errors to a dedicated folder for debugging.

---

## Prerequisites

### 1. Install Required Libraries
Ensure the following Python libraries are installed:
- `requests`
- `certifi`
- `python-dotenv`
- `urllib3`
- `PyPDF2`

You can install the required libraries using `pip`:
```bash
pip install -r requirements.txt
```

Alternatively, install them individually:
```bash
pip install requests certifi python-dotenv urllib3 PyPDF2
```

### 2. Set Up Environment Variables
Create a `.env` file in the project directory and define the following variables:
```env
TENANT_ID=<your-tenant-id>
CLIENT_ID=<your-client-id>
CLIENT_SECRET=<your-client-secret>
RESOURCE=<your-resource>
DEPLOYMENT_NAME=<your-deployment-name>
OPENAI_API_BASE=<your-openai-api-base-url>
SUBSCRIPTION_KEY=<your-subscription-key>
```

### 3. Create Required Folders
Before running the script, create the following folders in the project directory:

- **`paper`**: Store PDF files that you want to summarize.
- **`output`**: Store the output summary text files.
- **`error_logs`**: Store error logs when issues occur.
- **`system_prompt`**: Add system prompt text files here. These files define the instructions for the language model to generate responses.

You can create these folders manually or by running the following commands in the terminal:
```bash
mkdir paper output error_logs system_prompt
```

---

## How to Use

### 1. Run the Script
Execute the script using Python:
```bash
python main.py
```

### 2. Select a System Prompt
When prompted, select a system prompt file from the `system_prompt` folder. For example:
- `paper_summarizer.txt`: Used for summarizing PDF files.
- `responseInJapanese.txt`: Used for generating responses in Japanese.

### 3. Summarize a PDF File
If you select `paper_summarizer.txt`:
1. Place the PDF file you want to summarize in the `paper` folder.
2. Select the PDF file from the list displayed in the terminal.
3. The script will summarize the content and save the output in the `output` folder.

### 4. Generate Text Responses
If you select a system prompt other than `paper_summarizer.txt`:
1. Enter your prompt in the terminal.
2. The script will generate a response based on the selected system prompt.

### 5. Error Handling
If an error occurs during execution, the script logs the details in the `error_logs` folder. Check the log files for debugging.

---

## Folder Structure

```
azureOpenaiChatBasic/
│
├── main.py               # Main script
├── .env                  # Environment variables
├── requirements.txt      # List of required Python libraries
├── system_prompt/        # Folder for system prompt files
│   ├── paper_summarizer.txt
│   └── responseInJapanese.txt
├── paper/                # Folder to store PDF files
├── output/               # Folder to store output summary files
└── error_logs/           # Folder to store error logs
```

---

## Notes

- Ensure that the `system_prompt` folder contains the required prompt files (e.g., `paper_summarizer.txt`).
- The script disables SSL warnings for simplicity. For production use, ensure proper SSL configurations.
- Use the `pre_paper_prompt.txt` file in the `system_prompt` folder to customize the system prompt for PDF chat functionality.
```