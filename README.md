# grant-parser-py
Langchain Python for parsing grant PDFs and returning JSON of wanted information

- embedding model **nomic-embed-text**, chat llm **gemma3**

## Installation

Install dependencies with pip:

```bash
pip install -r requirements.txt
```

## Environment setup

Create a `.env` file in the project root and set the following variables:

```bash
OPENAI_KEY=<your OpenAI API key>
OPENAI_BASE_URL=<OpenAI base URL>
MODEL=<model name>
```

## Usage

Run the parser by providing the PDF file path and the `k` value used for similarity search:

```bash
python grant.py <path to pdf> <k-value>
```

Example:

```bash
python grant.py my_grant.pdf 4
```
