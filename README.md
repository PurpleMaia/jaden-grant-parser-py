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

## Python usage

- embedding model **nomic-embed-text**, chat llm **gemma3**

```bash
uv run grant.py <path to pdf> <k-value>
```

## TypeScript usage

The TypeScript project lives in the `ts/` directory. After installing the dependencies with Yarn, run:

```bash
npx ts-node grant.ts <k-value> <path to pdf> [additional pdfs...]
```

You can provide multiple PDF files for a single grant; all pages will be loaded together.

## Environment variables

The scripts expect the following variables to be set. Create a `.env` file in the project root and provide values for:

- `MODEL` – name of the chat completion model to use
- `OPENAI_KEY` – your API key
- `OPENAI_BASE_URL` – base URL for the OpenAI-compatible endpoint

Example `.env` file:

```env
MODEL=gemma3
OPENAI_KEY=sk-...
OPENAI_BASE_URL=https://api.example.com/v1
```
