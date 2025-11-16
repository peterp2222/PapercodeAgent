# Paperagent

# Overview

This project provides a tool for analyzing PDF documents using the Qwen API. The system consists of a backend server and a simple frontend interface for uploading and processing PDF files.

# Setup and Usage
## Backend Setup
- Navigate to the backend directory:
```bash
cd backend
```
- Set up the required environment variable for the Qwen API:
```bash
# For Linux/MacOS
export DASHSCOPE_API_KEY="your_qwen_api_key_here"

# For Windows (PowerShell)
$env:DASHSCOPE_API_KEY="your_qwen_api_key_here"
```
**Note**: You must obtain your API key from the DashScope console and set it as an environment variable before running the backend.

- Run the backend server:
```bash
python run.py
```
The server will start running on the default port 5000.

## Frontend Usage
- Open the frontend HTML file in your browser:
```text
frontend/page.html
```
- Use the upload interface to select and upload your local PDF file.
- The analysis process will begin automatically after upload. Please note that processing may take 5-10 minutes depending on the size and complexity of your document.
- Once the analysis is complete, the generated results will be saved in the backend/generated folder.
