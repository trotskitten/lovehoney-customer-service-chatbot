# Lovehoney-Style RAG Product Discovery Chatbot

A Streamlit-based applied AI chatbot that guides a shopper through product-discovery questions, retrieves relevant product context, and generates source-backed recommendations using OpenAI, ChromaDB, Tavily, and LangChain.

## Why This Project Matters

This project demonstrates how an LLM application can support a real retail customer-service workflow without requiring access to internal order, customer, or account data. Instead of acting as a generic chatbot, the app collects user preferences through a structured discovery flow, uses semantic retrieval to ground follow-up questions, and then searches public Lovehoney.eu product pages to produce recommendations with visible sources.

The result is a focused prototype for AI-assisted e-commerce support: practical, scoped, retrieval-aware, and designed around business value rather than open-ended chat.

## Highlights

- Builds an LLM-based AI application for a retail customer-service/product-discovery use case.
- Uses RAG patterns with OpenAI embeddings, ChromaDB semantic search, and Tavily web retrieval.
- Applies prompt engineering for question generation, query rewriting, and grounded recommendation output.
- Uses LangChain integrations for OpenAI chat models, embeddings, vector retrieval, and Tavily search.
- Maintains session-state memory across a guided multi-turn conversation.
- Includes API key handling through environment variables and `.env` loading.
- Adds a rate-limiting wrapper around LLM calls to reduce provider throttling.
- Shows GitHub-ready project organization and documentation for reproducible setup.

## Demo / App Overview

The app runs as a Streamlit chat interface called **Lovehoney Product Finder**.

At a high level, the chatbot:

1. Starts a product-discovery survey.
2. Collects user preferences over several turns.
3. Converts the answers into semantic retrieval queries.
4. Retrieves relevant product/customer-service context from a local ChromaDB vector store.
5. Uses retrieved context to generate better follow-up questions.
6. Creates a final Tavily search query for public Lovehoney.eu product pages.
7. Filters retrieved results to product pages.
8. Generates a final recommendation grounded in the retrieved product context.
9. Displays source links for the final product suggestions.

This is a prototype portfolio project. It does not use private Lovehoney systems, internal product feeds, customer accounts, order data, return systems, or payment workflows.

## Technical Stack

| Area | Technology | Role in the project |
| --- | --- | --- |
| App interface | Streamlit | Chat UI, message rendering, session state, local demo app |
| Language model | OpenAI GPT-4o mini | Question generation, query rewriting, recommendation generation |
| Embeddings | OpenAI text-embedding-3-large | Converts product-intent queries into vectors for semantic search |
| Vector database | ChromaDB | Persists and searches local product/customer-service chunks |
| Retrieval | Tavily | Searches and extracts public Lovehoney.eu product-page context |
| LLM orchestration | LangChain | Integrates chat model, embeddings, Chroma, and Tavily |
| Configuration | python-dotenv | Loads API keys and runtime settings from `.env` |
| Reliability helper | Custom rate limiter | Serializes LLM calls and enforces a minimum interval |
| Core language | Python 3.11 | Main application and retrieval logic |

## Architecture Overview

```text
User
  |
  v
Streamlit chat UI
  |
  v
CustomerServiceChatbot
  |
  +--> GPT-4o mini
  |      - first question generation
  |      - preference-to-query rewriting
  |      - follow-up question generation
  |      - final recommendation generation
  |
  +--> OpenAI text-embedding-3-large
  |      - embeds semantic product-intent queries
  |
  +--> ChromaDB local vector store
  |      - retrieves relevant stored product/context chunks
  |
  +--> Tavily search
         - retrieves public Lovehoney.eu product pages for final recommendations
```

The app uses a hybrid retrieval design:

- **ChromaDB** supports the survey phase by grounding follow-up questions in local product/context chunks.
- **Tavily** supports the final recommendation phase by retrieving current public product-page context.
- **GPT-4o mini** handles language generation but is instructed to use retrieved context rather than inventing product details.

## Building The Chroma Knowledge Base

The local Chroma database was built as a separate knowledge-processing pipeline before the Streamlit app runs. The diagram titled **Building the Chroma Knowledge Base** summarizes this build process: raw public website data is discovered, extracted, cleaned, embedded, and stored for semantic retrieval.

```text
Raw website content
  -> Tavily discovery and extraction
  -> data cleaning
  -> OpenAI text-embedding-3-large embeddings
  -> ChromaDB vector database
```

The build process followed these steps:

1. **Product URL discovery**
   Public Lovehoney.eu product-page URLs were identified using Tavily Map-style discovery. This created the candidate product-page list used for retrieval preparation.

2. **Product page extraction**
   Product-page content was retrieved with Tavily Extract. The extracted raw website information included page text, product descriptions, and product characteristics from public pages.

3. **Data cleaning**
   The raw extracted content was cleaned before embedding. Navigation text, metadata, duplicate content, and irrelevant boilerplate were removed where possible so the knowledge base focused on meaningful product information.

4. **Embedding generation**
   Cleaned product descriptions were converted into semantic vectors using OpenAI `text-embedding-3-large`. This embedding model produces the vector representation used by ChromaDB for similarity search.

5. **Vector storage in ChromaDB**
   The embedded product records were stored in the persisted local `chroma_db/` directory. The current app expects the `langchain` Chroma collection and uses the same `text-embedding-3-large` model at runtime so query vectors match the stored product vectors.

In the current demo setup, the Chroma knowledge base contains 197 embedded product/context records. At runtime, the chatbot does not rebuild this database; it loads `chroma_db/`, embeds the user's preference query, and retrieves the closest matching records to ground the next discovery question.

## Workflow Explanation

### 1. App startup

`streamlit_app.py` loads `CustomerServiceChatbot`, initializes Streamlit page settings, loads the visual assets, and creates the chat interface.

### 2. Model and retrieval setup

`scripts/chatbot.py` loads environment variables, initializes the OpenAI chat model, wraps it with the rate limiter, connects to Tavily, loads OpenAI embeddings, and opens the local ChromaDB collection.

The active vector-store configuration expects:

- Persist directory: `chroma_db/`
- Collection name: `langchain`
- Embedding model: `text-embedding-3-large`

### 3. Guided discovery

`scripts/product_discovery_tool.py` manages the survey state. It stores previous questions, user answers, generated queries, retrieved sources, and final recommendation context inside a session dictionary that is kept in Streamlit session state.

### 4. Retrieval-assisted follow-up questions

After each user answer, the app:

1. Saves the answer.
2. Uses GPT-4o mini to rewrite accumulated preferences into a compact semantic query.
3. Searches ChromaDB for relevant chunks.
4. Adds retrieved context to the prompt for the next question.
5. Asks one follow-up question designed to narrow product fit.

### 5. Final product recommendation

After the survey reaches its question limit, the app:

1. Converts the full preference history into a Tavily search query.
2. Searches public Lovehoney.eu pages.
3. Filters results to likely product URLs.
4. Builds a product context block from retrieved result content.
5. Prompts GPT-4o mini to recommend only products found in that context.
6. Displays the answer and source links in Streamlit.

## Key Features

- Guided multi-turn product-discovery survey.
- Semantic search over a persisted ChromaDB vector store.
- Live web retrieval against public Lovehoney.eu product pages.
- Query rewriting for both vector search and web search.
- Grounded recommendation prompt that restricts output to retrieved context.
- Source-backed final product suggestions.
- Session-state memory for previous questions, answers, sources, and completion status.
- Basic product URL filtering before final recommendation generation.
- Rate-limited LLM wrapper for more stable local demos.
- Environment-variable based API key handling.

## Key Technical Contributions

- Designed a product-discovery flow that narrows user intent before recommendation instead of relying on a single prompt.
- Implemented a RAG loop where retrieved product context influences follow-up questions during the survey phase.
- Combined local semantic retrieval and live web retrieval to separate stable product taxonomy/context from final product-page lookup.
- Built prompt templates for first-question generation, follow-up generation, semantic query generation, Tavily query generation, and final recommendation generation.
- Added session memory to avoid stateless responses and preserve the user's preference history across turns.
- Added source extraction and display so final recommendations can be traced back to retrieved product pages.
- Added a lightweight rate-limiting wrapper around the LLM client to reduce avoidable API throttling during interactive use.
- Documented setup, architecture, limitations, and future improvements for recruiter and engineering review.

## Repository Structure

```text
rag_customer_service_chatbot/
|-- streamlit_app.py                  # Streamlit entrypoint and chat UI
|-- scripts/
|   |-- chatbot.py                    # Model, embedding, vector store, and Tavily setup
|   |-- product_discovery_tool.py     # Survey state, retrieval flow, prompts, recommendations
|   |-- rate_limited_client.py        # Simple LLM invoke-rate limiter
|   `-- __init__.py
|-- chroma_db/                        # Persisted local Chroma vector store for demo use
|-- docs/                             # Local architecture and workflow notes
|-- data/                             # Local data/debug artifacts; ignored by Git
|-- logs/                             # Local logs; ignored by Git
|-- prompts/                          # Local prompt experiments; ignored by Git
|-- image.png                         # Streamlit background image
|-- chatbot_icon.jpeg                 # Assistant avatar
|-- product_discovery_chatbot.pptx    # Project presentation
|-- requirements.txt                  # Local pip dependency file; ignored by Git
|-- environment.yml                   # Local Conda environment file; ignored by Git
|-- .env.example                      # Local environment template; ignored by Git
`-- README.md
```

Note: `data/`, `logs/`, `prompts/`, `.env`, `.env.example`, `requirements.txt`, and `environment.yml` are ignored so local artifacts and credentials are not published accidentally.

## Setup

### Prerequisites

- Python 3.11
- OpenAI API key
- Tavily API key
- Local copy of this repository

### Clone the repository

```bash
git clone https://github.com/trotskitten/lovehoney-customer-service-chatbot.git
cd lovehoney-customer-service-chatbot
```

### Option 1: Conda

If you have the local `environment.yml` file:

```bash
conda env create -f environment.yml
conda activate rag-customer-service-chatbot
```

### Option 2: venv and pip

If you have the local `requirements.txt` file:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If dependency files are not present in your clone, install the core dependencies manually:

```bash
pip install streamlit langchain langchain-openai langchain-chroma langchain-tavily chromadb openai tavily-python python-dotenv pandas numpy tiktoken
```

## Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
CHAT_MODEL=gpt-4o-mini
```

`CHAT_MODEL` is optional. If it is not set, the app defaults to `gpt-4o-mini`.

Do not commit `.env` or real API keys.

## Run Instructions

Start the Streamlit app:

```bash
streamlit run streamlit_app.py
```

Streamlit will print a local URL, usually:

```text
http://localhost:8501
```

Open the URL in a browser and answer the product-discovery questions.

## Limitations

- The app is a local prototype, not a production deployment.
- It does not access private Lovehoney systems, internal catalogs, CRM data, order data, returns, payments, or customer accounts.
- Final product quality depends on Tavily retrieval quality and public page availability.
- The vector store must match the active embedding model and Chroma collection configuration.
- There is no formal offline evaluation suite or production monitoring dashboard in the repository.
- The app does not currently include authentication, moderation policy enforcement, analytics, or human handoff.

## Future Improvements

- Add an evaluation set for recommendation relevance, source faithfulness, and retrieval quality.
- Add automated tests for URL filtering, session-state transitions, query generation, and fallback behavior.
- Add structured logging for survey steps, retrieved chunks, final sources, and model outputs.
- Add guardrails for sensitive content, age gating, user safety language, and unsupported support requests.
- Add Docker packaging and deployment configuration for reproducible cloud hosting.
- Add a small admin/reporting view to inspect retrieval outcomes and identify weak product categories.
- Add SQL-backed analytics for product-discovery patterns and user preference trends.
- Add CI checks for formatting, tests, and dependency health.

