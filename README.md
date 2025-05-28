# grant-parser

This repository contains two implementations for parsing grant PDFs and extracting structured information using LangChain:

- **Python version** (`grant.py`)
- **TypeScript version** (`ts/grant.ts`)

Both versions load a PDF, create an in-memory vector store from embeddings, perform a similarity search for relevant pages, and then ask a language model to return JSON data describing the grant.

## Python usage

- embedding model **nomic-embed-text**, chat llm **gemma3**

```bash
python grant.py <path to pdf> <k-value>
```

## TypeScript usage

The TypeScript project lives in the `ts/` directory. Install its dependencies with `npm install` and then run:

```bash
npx ts-node grant.ts <path to pdf> <k-value>
```

## Environment variables

The scripts expect the following variables to be set (usually via a `.env` file):

- `MODEL` – name of the chat completion model to use
- `OPENAI_KEY` – your API key
- `OPENAI_BASE_URL` – base URL for the OpenAI-compatible endpoint
