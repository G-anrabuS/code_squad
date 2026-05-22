# FastAPI Backend

This backend powers GitHub authentication, repository cloning/scanning, Qdrant-backed retrieval, and Gemini-based multi-agent analysis for Code Squad.

## Core capabilities

- GitHub OAuth login and JWT exchange
- Repository listing and branch listing
- Repository cloning and scan previews
- Local sentence-transformer embeddings stored in Qdrant
- Gemini-powered analysis agents:
  - `summary`
  - `judge`
  - `architect`
  - `performance`
  - `security`
- Analysis export in JSON, markdown, and PDF

## Configuration

Add the following variables to `fastapi_backend/.env`:

```dotenv
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
JWT_SECRET=your_jwt_secret
GEMINI_API_KEY=your_gemini_api_key
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_COLLECTION=codebase
QDRANT_DISTANCE=Cosine
```

## Main endpoints

- `GET /auth/github/login`
- `GET /auth/github/callback`
- `POST /auth/exchange`
- `GET /user/repos`
- `GET /user/branches/{full_repo_name}`
- `POST /scan/repo`
- `POST /analysis/analyze`
- `POST /analysis/embed`
- `POST /analysis/chat`

## Notes

- Repository analysis is Gemini-only and returns structured success/error responses.
- Embeddings are generated locally with `all-MiniLM-L6-v2`, not via OpenAI.
