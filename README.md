# Diagnostyx Backend (Python Watchdog)

A controlled AI workflow system where a medical-analysis AI operates under a deterministic Python watchdog which enforces rules, validates outputs, and controls execution through permission gates.

## Setup & Running on Termux / Local Environment

### Prerequisites
- Python 3.9+
- Groq API Key

### Installation

1. Create a virtual environment (optional) or install directly:
   ```bash
   pip install fastapi uvicorn groq python-dotenv python-multipart
   ```

2. Create a `.env` file in this directory and add your Groq API Key:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

### Running the API
The main API that connects to the frontend is located in `api.py`. It uses a lightweight `csv` or JSON parser to avoid heavy memory usage on Termux.

Run the FastAPI server:
```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```
The backend will run on `http://localhost:8000`.

### Security Note
- The `.env` file and `data/*.csv` files are ignored by git to protect credentials and sensitive patient data.
