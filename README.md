# 📊 Sales Insight Automator

**AI-powered executive sales briefs by Rabbitt AI**

A secure, containerized application where team members upload sales data files (CSV/XLSX) and instantly receive an AI-generated executive brief via email.

![Architecture](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=flat&logo=react&logoColor=black)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![Gemini](https://img.shields.io/badge/Google%20Gemini-4285F4?style=flat&logo=google&logoColor=white)

---

## 🏗️ Architecture Overview

```
┌──────────────┐     ┌──────────────────┐     ┌──────────────┐
│   React SPA  │────▶│  FastAPI Backend  │────▶│ Google Gemini│
│  (Nginx/80)  │     │   (Uvicorn/8000)  │     │   LLM API    │
└──────────────┘     └────────┬─────────┘     └──────────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │   SMTP Email     │
                     │   (Gmail/etc.)   │
                     └──────────────────┘
```

**Flow:** Upload CSV/XLSX → Parse & Analyze → AI Summary (Gemini) → Email Delivery → Done ✅

---

## 🚀 Quick Start with Docker Compose

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) & Docker Compose
- A [Google Gemini API key](https://aistudio.google.com/app/apikey)
- SMTP credentials (Gmail with [App Password](https://myaccount.google.com/apppasswords) recommended)

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/Rabbit_Ai.git
   cd Rabbit_Ai
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys and SMTP credentials
   ```

3. **Start the stack**
   ```bash
   docker compose up --build
   ```

4. **Access the application**
   - **Frontend:** http://localhost
   - **Backend API:** http://localhost:8000
   - **Swagger Docs:** http://localhost:8000/docs
   - **ReDoc:** http://localhost:8000/redoc

5. **Test with sample data**
   - Upload the included `sales_q1_2026.csv`
   - Enter a recipient email
   - Click "Generate & Send Brief"

### Stop the stack

```bash
docker compose down
```

---

## 🛠️ Local Development (without Docker)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
# Create .env in the project root with your config
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server proxies `/api` requests to `localhost:8000` automatically.

---

## 🔒 Security Implementation

### Endpoint Protection

| Layer | Implementation |
|-------|---------------|
| **Rate Limiting** | `slowapi` enforces 10 requests/minute per IP on the upload endpoint, preventing resource abuse and DoS |
| **CORS** | Strict origin allowlist — only configured domains can call the API |
| **File Validation** | Whitelist-only file extensions (`.csv`, `.xlsx`), max size enforcement (10 MB), content parsing validation |
| **Input Sanitization** | Email validation via `pydantic` + `email-validator`; all user data is validated before processing |
| **Security Headers** | Custom middleware injects `X-Content-Type-Options`, `X-Frame-Options`, `Strict-Transport-Security`, `CSP`, `Referrer-Policy`, `Permissions-Policy` on every response |
| **HTML Injection Prevention** | Email HTML content is escaped via `html.escape()` before rendering |
| **Non-root Containers** | Both Docker containers run as non-root users |
| **No Secrets in Images** | Environment variables are injected at runtime via `.env` file, never baked into Docker images |
| **Request Tracing** | Each response includes a unique `X-Request-ID` header for security logging |

### Nginx Hardening
- Hidden file access denied (`location ~ /\.`)
- Client upload size limited (`client_max_body_size 10M`)
- Security headers on all static responses
- Gzip compression for performance

---

## 📡 API Documentation

Interactive Swagger UI is available at `/docs` when the backend is running.

### `GET /api/health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### `POST /api/upload`

Upload a sales data file and trigger AI summary + email delivery.

**Body (multipart/form-data):**
| Field | Type | Description |
|-------|------|-------------|
| `file` | File | `.csv` or `.xlsx` file (max 10 MB) |
| `email` | String | Recipient email address |

**Success Response (200):**
```json
{
  "success": true,
  "message": "Sales brief generated and sent to user@example.com.",
  "summary": "## Executive Overview\n...",
  "rows_processed": 6
}
```

**Error Responses:** `400` (bad input), `413` (file too large), `429` (rate limited), `500` (server error)

---

## 🔄 CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/ci.yml`) triggers on every PR to `main`:

| Job | Actions |
|-----|---------|
| **Backend** | Install Python 3.12 → Lint with Ruff → Validate imports |
| **Frontend** | Install Node 20 → ESLint → Production build |
| **Docker** | Build all images via `docker compose build` → Verify creation |

---

## 🌐 Deployment

### Backend (Render)

1. Create a new **Web Service** on [Render](https://render.com)
2. Connect your GitHub repo, set root directory to `backend`
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables from `.env.example`

### Frontend (Vercel)

1. Import project on [Vercel](https://vercel.com)
2. Set root directory to `frontend`
3. Framework preset: **Vite**
4. Add environment variable: `VITE_API_URL=https://your-backend.onrender.com`

---

## 📁 Project Structure

```
Rabbit_Ai/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app factory
│   │   ├── config.py          # Pydantic settings
│   │   ├── security.py        # Security headers middleware
│   │   ├── routers/
│   │   │   └── upload.py      # Upload + summarize endpoint
│   │   └── services/
│   │       ├── ai_engine.py   # Gemini LLM integration
│   │       ├── data_parser.py # CSV/XLSX parser
│   │       └── email_service.py # SMTP email delivery
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx            # Main SPA component
│   │   ├── App.css            # Styles
│   │   ├── main.jsx           # Entry point
│   │   └── index.css          # Global styles
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── .github/workflows/
│   └── ci.yml                 # CI/CD pipeline
├── docker-compose.yml
├── .env.example
├── sales_q1_2026.csv          # Sample test data
└── README.md
```

---

## ⚙️ Configuration Keys

See `.env.example` for all required environment variables:

| Key | Required | Description |
|-----|----------|-------------|
| `GEMINI_API_KEY` | ✅ | Google Gemini API key |
| `SMTP_HOST` | ✅ | SMTP server hostname |
| `SMTP_PORT` | ✅ | SMTP server port (587 for TLS) |
| `SMTP_USER` | ✅ | SMTP username/email |
| `SMTP_PASSWORD` | ✅ | SMTP password or app password |
| `SMTP_FROM_EMAIL` | ✅ | Sender email address |
| `AI_MODEL` | ❌ | Gemini model (default: `gemini-2.0-flash`) |
| `ALLOWED_ORIGINS` | ❌ | Comma-separated CORS origins |
| `MAX_FILE_SIZE_MB` | ❌ | Max upload size (default: 10) |
| `RATE_LIMIT` | ❌ | Rate limit string (default: `10/minute`) |

---

## 📝 License

Built for Rabbitt AI — Internal Tooling Sprint
