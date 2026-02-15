# EaseForm

**Privacy-first, open-source form builder alternative to Google Forms.**

EaseForm is designed for users who need a simple, secure, and privacy-respecting way to collect data without the bloat of enterprise form builders. It prioritizes respondent anonymity and data ownership while delivering a polished, modern user experience.

---

## 🚀 Why EaseForm? (The Motive)

In an era of enhance data tracking, EaseForm was built on three core principles:

1.  **Privacy First**: No respondent login required. No tracking pixels. We use a privacy-preserving device hash to prevent duplicate submissions without storing personal identifiers.
2.  **Simplicity & Speed**: A lightweight tech stack that loads instantly. No heavy interaction frameworks—just pure, optimized performance.
3.  **Ownership**: You own your data. Powered by your own Supabase instance, giving you full control over your backend and Row Level Security (RLS) policies.

---

## 🛠️ Technology Stack & Logic

EaseForm uses a modern, decoupled architecture separating the frontend client from the API backend.

### 1. Backend (`/backend`)
*   **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
    *   Chosen for its high performance (Asynchronous), authentic data validation (`Pydantic`), and automatic documentation (`/docs`).
*   **Authentication & Database**: [Supabase](https://supabase.com/)
    *   Acts as the Auth provider and PostgreSQL database.
    *   **Logic**: The backend verifies Supabase JWTs for protected routes (creating forms, viewing responses) but allows public access for submitting responses.
*   **Security**:
    *   **Rate Limiting**: `slowapi` protects against abuse (e.g., 5 requests/minute for submissions).
    *   **Security Headers**: Custom middleware enforces `HSTS`, `X-Frame-Options`, and `CSP`.
    *   **CORS**: Strictly configured to allow only trust origins.

### 2. Frontend (`/frontend`)
*   **Core**: Vanilla HTML5, JavaScript (ES6+), and CSS3, Tailwind CSS.
    *   **Logic**: No heavy framework (React/Vue) means zero build-time overhead for logic. We use native browser APIs for fetching data and DOM manipulation.
*   **Styling**: [Tailwind CSS](https://tailwindcss.com/)
    *   Uses a local build process (`npm run build`) to generate a tiny, optimized CSS file (`output.css`).
*   **State Management**:
    *   `window.API`: A centralized wrapper for all backend calls.
    *   `window.CacheUtils`: Implements a "stale-while-revalidate" strategy to keep the dashboard snappy without constant network requests.

### 3. Database (`/database`)
*   **PostgreSQL**: relational data model.
*   **RLS (Row Level Security)**: Policies enforced at the database level ensure:
    *   Users can only see/edit *their* forms.
    *   Respondents can *insert* responses but cannot *read* them.

---

## 💻 Setup Guide (How to run on another system)

Follow these steps to set up EaseForm locally or on a server.

### Prerequisites
*   [Python 3.9+](https://www.python.org/downloads/)
*   [Node.js 18+](https://nodejs.org/) (for Tailwind CSS build)
*   A [Supabase](https://supabase.com/) project (Free tier works great).

### Phase 1: Environment Setup

1.  **Clone the repository**
    ```bash
    git clone https://github.com/yourusername/easeform.git
    cd easeform
    ```

2.  **Configure `.env`**
   root : # Your Supabase project URL (e.g., https://xxxxx.supabase.co)
SUPABASE_URL=https://soqcmihyqsiednppptly.supabase.co

# Your Supabase anonymous/public key
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNvcWNtaWh5cXNpZWRucHBwdGx5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA3MTE2NjcsImV4cCI6MjA4NjI4NzY2N30.LbEaksKF_jQVGSSAB38bAX-FJAsiOg720SoplMcMleA

/backend/.env :
# Supabase Configuration
SUPABASE_URL=https://soqcmihyqsiednppptly.supabase.co

SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNvcWNtaWh5cXNpZWRucHBwdGx5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA3MTE2NjcsImV4cCI6MjA4NjI4NzY2N30.LbEaksKF_jQVGSSAB38bAX-FJAsiOg720SoplMcMleA

SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNvcWNtaWh5cXNpZWRucHBwdGx5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDcxMTY2NywiZXhwIjoyMDg2Mjg3NjY3fQ.IEyJ0GBhZ545qdWSpPSX3bK2-rRI4Wa9MbUZl6fV3eI

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:8080

# Environment
ENVIRONMENT=development


### Phase 2: Backend Setup

1.  **Create Virtual Environment**
    ```bash
    cd backend
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Start Server**
    ```bash
    python -m uvicorn app.main:app --reload
    ```
    *   API will run at `http://localhost:8000`.
    *   Docs available at `http://localhost:8000/api/docs`.

### Phase 3: Frontend Setup

1.  **Install Build Tools**
    ```bash
    cd ../frontend
    npm install
    ```

2.  **Generate Configuration**
    *   This script reads your `.env` and checks for system variables to generate `frontend/config.js`.
    ```bash
    node ../generate-config.js
    ```

3.  **Build CSS**
    ```bash
    # One-time build
    npm run build
    
    # Or watch for changes during development
    npm run watch
    ```

4.  **Serve Frontend**
    *   You can use any static file server. For VS Code users, "Live Server" extension is recommended.
    *   Serve the `frontend` directory.

### Phase 4: Database Setup

1.  Go to your Supabase SQL Editor.
2.  Run the validation script located at `database/validation.sql` to confirm your schema is ready.
3.  (Optional) If setting up from scratch, you will need the initial schema migration scripts (ensure `forms`, `questions`, `responses`, `profiles` tables exist).

---

## 📂 Project Structure

```
easeform/
├── backend/            # FastAPI Application
│   ├── app/            # Source code (routers, models)
│   └── requirements.txt
├── frontend/           # Static Web Application
│   ├── src/            # Input CSS for Tailwind
│   ├── dist/           # Compiled Output CSS
│   ├── utils/          # Shared JS logic (API, Auth, Cache)
│   ├── dashboard/      # Dashboard Page
│   ├── create/         # Form Builder
│   ├── forms/          # Public Form View
│   └── package.json    # Build dependencies
├── database/           # SQL Scripts
└── generate-config.js  # Config generator utility
```

---

## 🛡️ Privacy & Security Features

*   **Anonymous Mode**: Forms can be set to not collect any user data.
*   **One Response Per Device**: Uses a browser-generated distinct hash stored in local storage and verified by RLS to prevent spam without requiring login.
*   **Secure Headers**: Defaults to high-security standards (HSTS, No-Sniff) to protect users.

---

Copyrights Deserved to only Praful Mohite 
