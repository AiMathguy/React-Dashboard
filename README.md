# jsdashboard

A JavaScript dashboard app with a React frontend and Python backend.

## Project structure

- `frontend/` - React application source and frontend assets
- `Backend/` - Python backend and API routes
- Root files - static HTML/JS for quick demo and app integration

## Getting started

### Backend

```bash
cd Backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python app/main.py
```

### Frontend

```bash
cd frontend
npm install
npm start
```

## Notes

- Ignore generated files and local environment files via `.gitignore`
- This repo is initialized inside `jsdashboard/`
