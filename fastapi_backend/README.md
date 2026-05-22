# FastAPI Backend Qdrant Embedding Integration

This README documents the recent changes made to add repository chunking, OpenAI embeddings, and Qdrant vector storage to the backend.

## What was added

- `app/core/config.py`
  - Added OpenAI and Qdrant configuration values:
    - `OPENAI_API_KEY`
    - `OPENAI_EMBEDDING_MODEL`
    - `QDRANT_URL`
    - `QDRANT_API_KEY`
    - `QDRANT_COLLECTION`
    - `QDRANT_DISTANCE`

- `app/services/chunk_service.py`
  - Implemented code file discovery and filtering.
  - Added text chunking with configurable chunk size and overlap.
  - Added metadata generation for each chunk:
    - `path`, `filename`, `language`, `chunk_index`, `line_range`, `text`

- `app/services/embedding_service.py`
  - Implemented OpenAI embedding generation using `text-embedding-3-small` by default.
  - Added batch embedding ingestion.
  - Added Qdrant collection creation and upsert logic.
  - Added the repository ingestion workflow:
    - traverse codebase
    - chunk files
    - embed chunks
    - insert vectors into Qdrant

- `app/db/qdrant.py`
  - Added Qdrant client factory.
  - Added collection creation helper.
  - Added upsert helper for vector points.

- `app/api/analysis.py`
  - Added new endpoint: `POST /analysis/embed`
  - Accepts repository path, optional model, and optional collection name.

- `requirements.txt`
  - Added dependencies:
    - `openai>=1.8.0`
    - `qdrant-client>=1.8.0`

## How to configure

Add the following variables to `fastapi_backend/.env`:

```dotenv
OPENAI_API_KEY=your_openai_api_key
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_COLLECTION=codebase
QDRANT_DISTANCE=Cosine
```

## How to use

1. Install dependencies:

```bash
pip install -r fastapi_backend/requirements.txt
```

2. Run the FastAPI backend.

3. Call the new endpoint:

```http
POST /analysis/embed
Content-Type: application/json

{
  "repo_path": "c:\\Users\\janna\\Desktop\\code_squad\\fastapi_backend",
  "model": "text-embedding-3-small",
  "collection_name": "codebase"
}
```

## Output

The endpoint returns:

- `status`
- `message`
- `ingested_points`
- `collection_name`
- `model`

## Phase 9: Intelligent Chunking

The repository is no longer split into random token windows. Instead, chunks are created using content structure:

- Python functions and classes
- JavaScript/TypeScript functions, classes, and arrow-function assignments
- Configuration sections in YAML, TOML, INI, and JSON

Each chunk payload includes:

- `chunk_id`
- `file_path`
- `language`
- `content`
- `line_range`
- `chunk_index`

This improves retrieval quality because search is performed against logical code sections.

## Phase 10: Embedding + RAG

Embeddings are generated for each logical chunk and stored in Qdrant using the model configured in `OPENAI_EMBEDDING_MODEL`.

The stored Qdrant payload includes:

- `chunk_id`
- `path`
- `filename`
- `language`
- `content`
- `line_range`
- `chunk_index`

This makes the codebase searchable with RAG-style retrieval.

## LLM Agent Wrapping

Each analysis agent is wrapped by the LLM wrapper to enrich findings and summaries using OpenAI chat models.

Per-agent default models are configured internally and can be overridden using `OPENAI_LLM_MODEL_MAP` in `.env`.

## Validation

The updated files were compiled with Python and no syntax errors were reported.
