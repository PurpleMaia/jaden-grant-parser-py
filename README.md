# grant-parser-py
Langchain Python for parsing grant PDFs and returning JSON of wanted information

- embedding model **nomic-embed-text**, chat llm **gemma3**

### Environment variables
Create a `.env` file or export the following variables before running any script:

- `MODEL` – name of the chat model used by `ChatOpenAI`
- `OPENAI_KEY` – API key for the model
- `OPENAI_BASE_URL` – base URL of the OpenAI endpoint

### python grant.py \<path to pdf\> \<k-value\>
