🧠 Complaint Chatbot Project

This project provides two versions of a complaint registration chatbot:

Terminal-based chatbot for command-line interaction
Flask API chatbot for web-based interaction via tools like Postman

Both versions store complaints in a local SQLite database and use a simple retrieval-augmented generation (RAG) style response system, backed by OpenAI.

---

📂 Files Overview

* app_Terminal_Version.py – Run this for terminal-based chatbot interaction
* app_Flask_Version.py – Flask API with endpoints to create, check, and chat
* complaints.db – SQLite database file (auto-created)
* postman_command.txt – Sample Postman/CURL commands
* requirements.txt – List of Python dependencies


---

Setup Instructions

1. Install dependencies

   pip install flask openai

2. Set your OpenAI API key

   You can either:

    Edit the api_key="your-openai-api-key" line in both scripts, OR
    Set an environment variable:

     set OPENAI_API_KEY=your-key     

--- While Using Terminal Version
 Asks user for complaint details
 Responds from keyword-based knowledge or OpenAI
 Stores complaint with a unique ID in complaints.db

---

🌐 Using the Flask API

bash
python app.py

Available Endpoints:

| Method | Endpoint           | Description                   |
| ------ | ------------------ | ----------------------------- |
| POST   | `/complaints`      | Register a new complaint      |
| GET    | `/complaints/<id>` | Get complaint status by ID    |
| POST   | `/chat`            | Ask a question to the chatbot |

---
