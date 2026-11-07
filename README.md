# TDS Data Analyst Agent

A FastAPI service that accepts a question file and data files, then returns JSON analysis results and optional base64 visualizations.

## LLM provider

This repository uses **OpenRouter** with the default model:

google/gemma-4-26b-a4b-it

The application uses the OpenAI Python SDK as an OpenAI-compatible client, configured to send requests to OpenRouter. It does not call the OpenAI API directly.

## Features

- CSV, Excel, JSON and Parquet data loading
- ZIP and TAR.GZ archive extraction with path, link, entry-count and expansion-size checks
- Pandas/NumPy data processing; large CSVs are scanned with memory-bounded DuckDB and summarized without loading the full file into Pandas
- Matplotlib scatter plots with a regression line
- FastAPI multipart endpoint at POST /api/
- Configurable OpenRouter model and request timeout
- Render health endpoint at GET /health

## Browser interface

Open the live application at **https://tds-data-agent-final-63w7.onrender.com**.

The homepage provides a browser-based workspace where you can:
- Write one or more questions in plain language.
- Upload CSV, Excel, JSON, Parquet, ZIP or TAR.GZ files.
- Run an analysis against the existing `POST /api/` endpoint.
- View structured answers and generated charts.
- Copy or download the JSON response.

The dataset upload is optional for question-only requests. The API route and its existing JSON response formats remain available for integrations.

## Configuration

Create a local .env file for development (it is ignored by Git), or add these variables in Render:

    OPENROUTER_API_KEY=your_openrouter_api_key
    OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
    OPENROUTER_MODEL=google/gemma-4-26b-a4b-it
    OPENROUTER_APP_NAME=TDS Data Analyst Agent
    LLM_TIMEOUT_SECONDS=90
    MAX_UPLOAD_BYTES=157286400
    MAX_TOTAL_UPLOAD_BYTES=157810688
    MAX_QUESTIONS_BYTES=524288
    MAX_ARCHIVE_ENTRIES=2000
    MAX_ARCHIVE_UNPACKED_BYTES=157286400

A safe starter file is available at .env.example. Never commit a real API key.

Create an OpenRouter key at https://openrouter.ai/settings/keys.

## Run locally

    python -m pip install -r requirements.txt
    uvicorn app:app --reload --host 127.0.0.1 --port 8000

Health check: GET /health

## API usage

POST /api/ accepts multipart form data:

- questions.txt (required): analysis instructions and questions
- One or more supported data files (optional)

Example:

    curl -X POST http://localhost:8000/api/ -F questions.txt=@questions.txt -F data.csv=@data.csv

The response preserves the project's JSON array/object formats. If a visualization is requested, the app returns a base64 data URI (PNG or WebP).

## Deploy on Render

The repository includes a render.yaml Blueprint.

Manual Web Service settings:

- Runtime: Python
- Build command: pip install -r requirements.txt
- Start command: uvicorn app:app --host 0.0.0.0 --port $PORT
- Health check path: /health

Add these Render environment variables:

| Key | Value |
|---|---|
| OPENROUTER_API_KEY | Your OpenRouter API key (secret) |
| OPENROUTER_BASE_URL | https://openrouter.ai/api/v1 |
| OPENROUTER_MODEL | google/gemma-4-26b-a4b-it |
| LLM_TIMEOUT_SECONDS | 90 |

The Blueprint prompts for OPENROUTER_API_KEY because it is marked sync:false. Do not put API keys in render.yaml, source code, or GitHub.

## Supported file types

- .csv
- .xlsx, .xls
- .json
- .parquet
- .zip, .tar.gz, .tgz (containing supported data files)

## Upload size

The interface and API accept **up to 150 MiB per file and 150 MiB combined per request**. Archive extraction is separately bounded to 150 MiB of unpacked content. These are upload/validation limits, not a guarantee that every 150 MiB dataset can be analyzed on a low-memory instance: tabular data can use several times its on-disk size when loaded into Pandas. Large-file analysis may require a higher-memory Render plan.

The current web-table loader only accepts an explicit HTTPS Wikipedia page URL included in questions.txt. It is not a general-purpose crawler and does not directly query remote S3 buckets.

## Technical stack

- FastAPI + Uvicorn
- Pandas, NumPy, DuckDB, PyArrow
- Matplotlib, NumPy
- Requests, BeautifulSoup4
- OpenAI-compatible Python SDK pointed at OpenRouter
- Pillow, aiofiles

## Validation notes

The language model receives complete rows for compact files (up to 200 rows), and a bounded sample plus whole-file descriptive statistics for larger files. Large CSV files are scanned with DuckDB using a fixed memory limit and disk-backed temporary work; only a small sample is retained in Pandas for prompt examples and charts. This limits memory use and prompt size, but arbitrary question-specific calculations should still be verified against deterministic SQL/Python results. Verify exact high-stakes numerical results against Python/SQL calculations.

Run the automated checks with:

    pip install -r requirements.txt -r requirements-dev.txt
    python -m compileall -q .
    pytest -q

## Author

Sana Bint Salim
