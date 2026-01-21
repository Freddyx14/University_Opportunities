# Novo - Hyper-personalized Career Agent

A Flask-based application for university students to get personalized career guidance through AI analysis of their CV and audio "brain dump."

## Setup

1. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```
   Note: Make sure to use the same Python version that has the packages installed.

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

4. **Run the application:**
   ```bash
   python3.14 app.py
   ```
   Or if Python 3.14 is your default Python 3:
   ```bash
   python3 app.py
   ```

5. **Access the application:**
   Open your browser and navigate to `http://localhost:5000`

## Project Structure

```
University_Opportunities/
├── app.py                 # Flask application entry point
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment variables
├── .gitignore            # Git ignore rules
├── uploads/              # Temporary file storage (created automatically)
├── src/
│   ├── __init__.py
│   ├── routes.py         # Route handlers
│   └── services/
│       ├── __init__.py
│       └── ai_agent.py   # Gemini API integration
└── templates/
    └── profile.html      # Profile upload page
```

## Features

- **Profile Upload:** Upload CV (PDF) and audio brain dump (MP3/WAV/M4A/OGG)
- **Gemini Integration:** Ready for multimodal AI analysis
- **Modern UI:** Beautiful interface built with TailwindCSS

## Tech Stack

- **Backend:** Python 3.14, Flask
- **AI:** Google Gemini 1.5 Pro
- **Frontend:** HTML5, TailwindCSS (CDN)
- **Environment:** python-dotenv

## License

MIT
