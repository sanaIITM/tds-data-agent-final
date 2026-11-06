# TDS Data Analyst Agent

A FastAPI service for answering data-analysis questions about uploaded files and returning JSON results, including base64 visualizations where requested.

## LLM provider

This repository uses OpenRouter with the default model:

google/gemma-4-26b-a4b-it

The project uses the OpenAI Python SDK as an OpenAI-compatible HTTP client. Requests are sent to OpenRouter, not directly to OpenAI.

## Features

- CSV, Excel, JSON and Parquet data loading
- ZIP and TAR.GZ archive extraction
- Pandas/NumPy data processing and DuckDB Parquet support
- Matplotlib visualizations
- FastAPI multipart endpoint at POST /api/
- Configurable OpenRouter model

## Configuration

Create a local .env file for development (it is ignored by Git), or add the same variables in Render:

    OPENROUTER_API_KEY=your_openrouter_api_key
    OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
    OPENROUTER_MODEL=google/gemma-4-26b-a4b-it
    LLM_TIMEOUT_SECONDS=90

A safe starter file is available at .env.example. Never commit a real API key.

Get an OpenRouter key at https://openrouter.ai/settings/keys.

## Run locally

    python -m pip install -r requirements.txt
    uvicorn app:app --reload --host 127.0.0.1 --port 8000

The service health endpoint is GET /.

## API usage

The POST /api/ endpoint accepts multipart form data. Include:

- questions.txt (required): analysis instructions/questions
- One or more supported data files (optional)

Example:

    curl -X POST http://localhost:8000/api/ -F questions.txt=@questions.txt -F data.csv=@data.csv

The response preserves the project's JSON array/object formats. A requested visualization is returned as a data:image/png;base64,... value.

## Deploy on Render

The repository includes a render.yaml Blueprint configuration. You can create/update a Render service from that Blueprint or configure an existing Web Service manually.

Manual settings:

- Runtime: Python 3
- Build command: pip install -r requirements.txt
- Start command: uvicorn app:app --host 0.0.0.0 --port $PORT
- Health check path: /

Set these Render environment variables:

| Key | Value |
|---|---|
| OPENROUTER_API_KEY | Your OpenRouter API key (secret) |
| OPENROUTER_BASE_URL | https://openrouter.ai/api/v1 |
| OPENROUTER_MODEL | google/gemma-4-26b-a4b-it |
| LLM_TIMEOUT_SECONDS | 90 |

Do not put secrets in render.yaml, source code, or GitHub.

## Supported file types

- .csv
- .xlsx, .xls
- .json
- .parquet
- .zip, .tar.gz, .tgz

## Technical stack

- FastAPI + Uvicorn
- Pandas, NumPy, DuckDB, PyArrow
- Matplotlib, scikit-learn
- Requests, BeautifulSoup4
- OpenAI-compatible Python SDK pointed at OpenRouter
- Pillow, aiofiles

## Notes

- Keep your OpenRouter key private and rotate it if it is ever exposed.
- LLM output should be treated as untrusted input. Validate and parse structured output before returning it.
- Exact numerical results should be computed from the dataframe in Python rather than guessed by the language model.

## Author

Sana Bint Salim
