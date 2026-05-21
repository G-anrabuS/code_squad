# CodeSquad 🚀

AI-powered GitHub Repository Code Review Platform

CodeSquad is a Flutter + FastAPI application that allows users to log in with GitHub, fetch their repositories, select a branch, clone the selected repository, and intelligently filter relevant source files for future AI-based code review.

---

# Current Features

✅ GitHub OAuth Login
✅ JWT Authentication
✅ Fetch user repositories
✅ Fetch repository branches
✅ Clone public/private repositories
✅ Intelligent source file filtering
✅ Flutter Android frontend login flow
✅ Backend deployed on Render

---

# Tech Stack

## Frontend

- Flutter
- Dio
- flutter_web_auth_2

## Backend

- FastAPI
- Authlib
- GitPython
- HTTPX
- python-jose
- python-dotenv

## Deployment

- Render

---

# Project Structure

```bash
Code Squad/
│
├── fastapi_backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py
│   │   │   ├── repos.py
│   │   │   └── scan.py
│   │   │
│   │   ├── core/
│   │   │   ├── auth_dependency.py
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   │
│   │   ├── services/
│   │   │   ├── clone_service.py
│   │   │   └── parser_service.py
│   │   │
│   │   └── main.py
│   │
│   ├── requirements.txt
│   └── .env
│
└── flutter_frontend/
    └── lib/
        ├── config/
        ├── models/
        ├── screens/
        └── services/
```

---

# Backend Setup

## 1. Clone Repository

```bash
git clone https://github.com/G-anrabuS/code_squad
cd fastapi_backend
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / Mac

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# GitHub OAuth Setup

Create a GitHub OAuth App.

Go to:

https://github.com/settings/developers

Then:

**New OAuth App**

Fill:

### Application name

```text
CodeSquad
```

### Homepage URL

For local:

```text
http://127.0.0.1:8000
```

For deployed:

```text
https://your-render-url.onrender.com
```

### Authorization callback URL

For local:

```text
http://127.0.0.1:8000/auth/github/callback
```

For deployed:

```text
https://your-render-url.onrender.com/auth/github/callback
```

Save.

Copy:

- Client ID
- Client Secret

---

# Environment Variables

Create:

```bash
fastapi_backend/.env
```

Add:

```env
GITHUB_CLIENT_ID=your_client_id
GITHUB_CLIENT_SECRET=your_client_secret
JWT_SECRET=your_random_secret_key
```

Example:

```env
GITHUB_CLIENT_ID=Ov23lixxxxxxxx
GITHUB_CLIENT_SECRET=xxxxxxxxxxxxxxxx
JWT_SECRET=super_secret_key
```

---

# Run Backend Locally

```bash
uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

---

# Render Deployment

## 1. Push backend to GitHub

```bash
git add .
git commit -m "deploy backend"
git push
```

---

## 2. Create Render Web Service

Go:

https://render.com

Create:

```text
New → Web Service
```

Settings:

### Runtime

```text
Python
```

### Build Command

```bash
pip install -r requirements.txt
```

### Start Command

```bash
uvicorn app.main:app --host 0.0.0.0 --port 10000
```

---

## 3. Add Environment Variables

Render Dashboard → Environment:

```env
GITHUB_CLIENT_ID=...
GITHUB_CLIENT_SECRET=...
JWT_SECRET=...
```

---

## 4. Update GitHub OAuth App

Set callback:

```text
https://your-render-url.onrender.com/auth/github/callback
```

---

# Flutter Frontend Setup

## 1. Move to frontend

```bash
cd flutter_frontend
```

---

## 2. Install packages

```bash
flutter pub get
```

Required packages:

```yaml
dio:
flutter_web_auth_2:
```

---

# Flutter API Config

Update:

```dart
lib/config/api_config.dart
```

For deployed backend:

```dart
class ApiConfig {
  static const String baseUrl =
      "https://your-render-url.onrender.com";
}
```

---

# Login Screen Config

In:

```dart
login_screen.dart
```

Use:

```dart
final result = await FlutterWebAuth2.authenticate(
  url: "https://your-render-url.onrender.com/auth/github/login",
  callbackUrlScheme: "codesquad",
);
```

---

# Run Flutter

## Android

```bash
flutter clean
flutter pub get
flutter run
```

---

# Current App Flow

```text
Login with GitHub
   ↓
GitHub OAuth
   ↓
Return to app
   ↓
JWT authentication
   ↓
Fetch repositories
   ↓
Show repository list
   ↓
Select repo
   ↓
Branch screen (next implementation)
```

---

# Current API Endpoints

## Login

```http
GET /auth/github/login
```

---

## Fetch Repositories

```http
GET /user/repos
```

Requires:

```http
Authorization: Bearer <jwt>
```

---

## Fetch Branches

```http
GET /user/branches/{repo_name}
```

---

## Scan Repository

```http
POST /scan/repo
```

Body:

```json
{
    "repo_name": "hostel_pulse",
    "branch": "main"
}
```

---

# What's Next

Planned:

- Branch selection UI
- Scan trigger
- Results screen
- Code chunking
- Embeddings
- Qdrant integration
- Multi-agent AI reviewers
- Save scan history
- Cleanup cloned repos

---

# Notes

Temporary cloned repositories are currently NOT auto-deleted.

Planned fix:

```python
finally:
    cleanup_repo(repo_path)
```

after result persistence is implemented.

---
