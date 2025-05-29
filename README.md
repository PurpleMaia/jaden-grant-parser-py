# grant-parser

This repository contains two implementations for parsing grant PDFs and extracting structured information using LangChain:

- **Python version** (`grant.py`)
- **TypeScript version** (`ts/grant.ts`)

Both versions load a PDF, create an in-memory vector store from embeddings, perform a similarity search for relevant pages, and then ask a language model to return JSON data describing the grant.

## Installation

### Python

1. Create a virtual environment using [uv](https://github.com/astral-sh/uv):

   ```bash
   uv venv
   ```

2. Install the Python requirements:

   ```bash
   uv pip install -r requirements.txt
   ```

### TypeScript

Inside the `ts/` directory use [Yarn](https://yarnpkg.com/) to install dependencies:

```bash
cd ts
yarn install
```

## CLI Python usage

- embedding model **nomic-embed-text**, chat llm **gemma3**

```bash
uv run grant.py [<path to pdf> ...] [-f <folder>] [-k <k-value>] [-m <model>]
```

Provide either a list of PDF files or use `-f`/`--folder` to recursively search
for PDFs under the given directory.

The resulting JSON file name includes the model name from `--model` or the
`MODEL` environment variable and the grant source. For example:

```
grant-gemma3-mygrant.json
```

## CLI TypeScript usage

The TypeScript project lives in the `ts/` directory. After installing the dependencies with Yarn, run:

```bash
npx ts-node grant.ts <k-value> [-m <model>] [--folder <dir> | <path to pdf> [additional pdfs...]]
```

You can provide multiple PDF files for a single grant, or pass `--folder` to load every PDF under a directory recursively. All pages will be loaded together.

The JSON output is saved as `grant_<MODEL>_<source>.json`, where `<MODEL>` comes
from `--model` if provided or from the `MODEL` environment variable. If
`--folder` is used, `<source>` is the name of that folder; otherwise it is a
list of the provided PDF file names joined with underscores.

## Environment variables

The scripts look for these variables in a `.env` file, but you can also pass the
model name with the `--model` command-line option to override `MODEL`.
Create a `.env` file in the project root and provide values for:

- `MODEL` – name of the chat completion model to use
- `OPENAI_KEY` – your API key
- `OPENAI_BASE_URL` – base URL for the OpenAI-compatible endpoint
- `API_TOKEN` – bearer token required for `POST /api/grant` (not required for CLI-only)
- `WEB_USER` – username for the `/web` basic-auth form (not required for CLI-only)
- `WEB_PASS` – password for the `/web` basic-auth form (not required for CLI-only)

Example `.env` file:

```env
MODEL=gemma3
OPENAI_KEY=sk-...
OPENAI_BASE_URL=https://api.example.com/v1
```

## Python FastAPI

The code also comes with a HTML web UI and protected API endpoint. For example, to run in dev mode:

```
uv run uvicorn api_app:app --reload
```

Then once that loads, open the browser to http://localhost:8000/web

## CLI Evaluation

The `evaluate.py` script automates running `grant.py` on a set of PDFs and
compares the produced JSON against reference files. The configuration is
provided as a JSON array where each object specifies either a folder of PDFs or
an explicit list of files along with the expected output path.

Run the evaluator with:

```bash
uv run evaluate.py <config.json> [-m <model>]
```

Example configuration:

```json
[
  {
    "files": ["pdfs/example1.pdf"],
    "expected": "expected/example1.json",
    "k": 2
  },
  {
    "folder": "pdfs/grant2",
    "expected": "expected/grant2.json"
  }
]
```

Each entry may include a custom `k` value for the similarity search. Runtime and
accuracy scores are aggregated and printed in a summary table.
