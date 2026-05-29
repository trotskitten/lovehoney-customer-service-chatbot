from pathlib import Path
import os

from dotenv import load_dotenv

from scripts.rate_limited_client import RateLimitedClient

from langchain_tavily import TavilySearch
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from scripts.product_discovery_tool import ProductDiscoveryTool

#------------------------------------------------------------------------------------------------
class CustomerServiceChatbot:
    def __init__(self):
        self.project_root = Path(__file__).resolve().parents[1]
        load_dotenv(self.project_root / ".env")
        self.chat_model = os.getenv("CHAT_MODEL", 
                                    "gpt-4o-mini")     
        raw_llm = ChatOpenAI(model=self.chat_model,
                                 temperature=0.6, #0 the model is deterministic 2 the model is creative
                                 max_retries=2,
                                 )
        self.llm = RateLimitedClient( # Wrap the real client before storing it on the chatbot.
                                    raw_llm,  # Pass the real Mistral client into the wrapper.
                                    min_interval_seconds=1.0,  # Enforce at least 1.0 seconds between completed calls.
                                    )  # Finish creating the throttled LLM object.

        self.product_search = TavilySearch(max_results=20,
                                     search_depth="basic",
                                     include_answer=True,
                                     include_domains=["lovehoney.eu"],
                                     include_raw_content="markdown"
                                     )
        
        self.embedding_model = OpenAIEmbeddings(model="text-embedding-3-large")
        self.vector_store = Chroma(
            collection_name="langchain",
            persist_directory=str(self.project_root / "chroma_db"),
            embedding_function=self.embedding_model,
        )

        self.product_discovery = ProductDiscoveryTool(
            llm=self.llm,
            search=self.product_search,
            question_context_retriever=self.vector_store,
        )
    

    def start_product_discovery (self):
        return self.product_discovery.start_survey()

    def handle_message(self, user_query, product_discovery_session = None):
        if self.product_discovery.is_active(product_discovery_session):
            return self.product_discovery.handle(user_query, product_discovery_session)
        return self.start_product_discovery()
        

