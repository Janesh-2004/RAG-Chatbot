"""
RAG Indexer for document processing and retrieval using Azure AI Search
"""
import logging
import os
import re
from typing import Dict, List, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceNotFoundError
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile
)

from utils import extract_text_from_file

logger = logging.getLogger("rag-indexer")

# Load environment variables
load_dotenv()


class RAGIndexer:
    """
    Manages document indexing and retrieval for RAG chatbot using Azure AI Search.
    """
    
    def __init__(self):
        """Initialize the RAG indexer with Azure OpenAI embeddings and Azure AI Search."""
        # Load environment variables
        self.search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        self.search_key = os.getenv("AZURE_SEARCH_KEY")
        self.index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")  # Default/base index name
        self.embedding_deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION")
        self.azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.azure_openai_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.chat_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

        self._validate_environment()
        
        # Cache for per-chat search clients
        self.search_clients: Dict[str, SearchClient] = {}
        
        # Cache for per-chat search clients
        self.search_clients: Dict[str, SearchClient] = {}
        
        # Initialize Azure OpenAI Embeddings
        self.embeddings = AzureOpenAIEmbeddings(
            azure_deployment=self.embedding_deployment,
            openai_api_version=self.api_version,
            azure_endpoint=self.azure_openai_endpoint,
            api_key=self.azure_openai_key
        )

        vector_dims_env = os.getenv("VECTOR_DIMENSIONS")
        if vector_dims_env:
            self.vector_dimensions = int(vector_dims_env)
            logger.info("Using VECTOR_DIMENSIONS override: %s", self.vector_dimensions)
        else:
            probe_embedding = self.embeddings.embed_query("dimension probe")
            if not probe_embedding:
                raise RuntimeError("Failed to detect embedding dimensions from Azure OpenAI.")
            self.vector_dimensions = len(probe_embedding)
            logger.info(
                "Detected embedding dimension %s from Azure OpenAI deployment '%s'.",
                self.vector_dimensions,
                self.embedding_deployment,
            )
        
        # Initialize Azure Search clients
        credential = AzureKeyCredential(self.search_key)
        self.index_client = SearchIndexClient(
            endpoint=self.search_endpoint,
            credential=credential
        )
        
        # Create or get default search index (for backward compatibility)
        self._create_search_index_for_name(self.index_name)
        
        # Initialize default search client for document operations
        self.search_client = SearchClient(
            endpoint=self.search_endpoint,
            index_name=self.index_name,
            credential=credential
        )
        
        # Initialize Azure Chat OpenAI
        self.llm = AzureChatOpenAI(
            azure_deployment=self.chat_deployment,
            openai_api_version=self.api_version,
            azure_endpoint=self.azure_openai_endpoint,
            api_key=self.azure_openai_key,
            temperature=0.2
        )
        
        # Get chunk settings from environment
        self.chunk_size = int(os.getenv("CHUNK_SIZE", "1000"))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "200"))
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
        )

        # Chat history storage per chat_id
        self.chat_history: Dict[str, List[dict]] = {}

    @staticmethod
    def _sanitize_document_id(filename: str, chunk_index: int) -> str:
        """
        Azure AI Search document keys allow letters, digits, _, -, = only.
        Replace other characters with underscores to keep IDs valid.
        """
        base_name = os.path.splitext(os.path.basename(filename))[0]
        safe_base = re.sub(r"[^A-Za-z0-9_\-=]", "_", base_name)
        safe_base = safe_base or "document"
        return f"{safe_base}_{chunk_index}"

    @staticmethod
    def _sanitize_index_name(chat_name: str) -> str:
        """
        Sanitize chat name to create valid Azure AI Search index name.
        Index names must be lowercase, start with letter, contain only letters, digits, hyphens.
        Max length: 128 characters.
        """
        # Convert to lowercase and replace invalid characters with hyphens
        sanitized = re.sub(r"[^a-z0-9\-]", "-", chat_name.lower())
        # Remove leading/trailing hyphens and consecutive hyphens
        sanitized = re.sub(r"-+", "-", sanitized).strip("-")
        # Ensure it starts with a letter
        if not sanitized or not sanitized[0].isalpha():
            sanitized = f"chat-{sanitized}"
        # Limit length
        if len(sanitized) > 100:  # Leave room for prefix
            sanitized = sanitized[:100]
        return sanitized

    def _get_index_name_for_chat(self, chat_name: str) -> str:
        """Get the Azure AI Search index name for a specific chat."""
        sanitized_name = self._sanitize_index_name(chat_name)
        return f"rag-{sanitized_name}"

    def _get_search_client_for_chat(self, chat_name: str) -> SearchClient:
        """Get or create a search client for a specific chat's index."""
        index_name = self._get_index_name_for_chat(chat_name)
        
        # Return cached client if exists
        if index_name in self.search_clients:
            return self.search_clients[index_name]
        
        # Create index if doesn't exist
        self._create_search_index_for_name(index_name)
        
        # Create and cache new search client
        credential = AzureKeyCredential(self.search_key)
        client = SearchClient(
            endpoint=self.search_endpoint,
            index_name=index_name,
            credential=credential
        )
        self.search_clients[index_name] = client
        return client

    @staticmethod
    def _escape_filter_value(value: str) -> str:
        """Escape single quotes for use in OData filters."""
        return value.replace("'", "''")
    def _validate_environment(self):
        """Ensure all required Azure settings are present."""
        required_vars = {
            "AZURE_SEARCH_ENDPOINT": self.search_endpoint,
            "AZURE_SEARCH_KEY": self.search_key,
            "AZURE_SEARCH_INDEX_NAME": self.index_name,
            "AZURE_OPENAI_EMBEDDING_DEPLOYMENT": self.embedding_deployment,
            "AZURE_OPENAI_API_VERSION": self.api_version,
            "AZURE_OPENAI_ENDPOINT": self.azure_openai_endpoint,
            "AZURE_OPENAI_API_KEY": self.azure_openai_key,
            "AZURE_OPENAI_DEPLOYMENT_NAME": self.chat_deployment,
        }
        missing = [name for name, value in required_vars.items() if not value]
        if missing:
            raise ValueError(
                "Missing required Azure environment variables: "
                + ", ".join(missing)
            )
    
    def _create_search_index_for_name(self, index_name: str):
        """Create Azure Search index with given name if it doesn't exist or fix schema drift."""
        fields = [
            SearchField(
                name="id",
                type=SearchFieldDataType.String,
                key=True,
                filterable=True,
            ),
            SearchField(
                name="chat_id",
                type=SearchFieldDataType.String,
                filterable=True,
                retrievable=True,
            ),
            SearchField(
                name="content",
                type=SearchFieldDataType.String,
                searchable=True,
                retrievable=True,
            ),
            SearchField(
                name="content_vector",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                retrievable=False,
                vector_search_dimensions=self.vector_dimensions,
                vector_search_profile_name="default-profile",
            ),
            SearchField(
                name="source",
                type=SearchFieldDataType.String,
                filterable=True,
                retrievable=True,
            ),
        ]

        vector_search = VectorSearch(
            algorithms=[
                HnswAlgorithmConfiguration(
                    name="default-algo",
                    parameters={
                        "m": 4,
                        "efConstruction": 400,
                        "efSearch": 500,
                        "metric": "cosine",
                    },
                )
            ],
            profiles=[
                VectorSearchProfile(
                    name="default-profile",
                    algorithm_configuration_name="default-algo",
                )
            ],
        )

        index = SearchIndex(
            name=index_name,
            fields=fields,
            vector_search=vector_search,
        )

        try:
            existing_index = self.index_client.get_index(index_name)
            existing_fields = {field.name: field for field in existing_index.fields or []}

            required_fields = {field.name for field in fields}
            missing_fields = required_fields - set(existing_fields.keys())
            content_vector_field = existing_fields.get("content_vector")
            dimension_mismatch = (
                content_vector_field is None
                or getattr(content_vector_field, "vector_search_dimensions", None) != self.vector_dimensions
            )

            if not missing_fields and not dimension_mismatch:
                logger.info(
                    "Index '%s' already exists with required fields (dimension=%s).",
                    index_name,
                    self.vector_dimensions,
                )
                return

            reason = []
            if missing_fields:
                reason.append(f"missing fields {missing_fields}")
            if dimension_mismatch:
                existing_dim = getattr(content_vector_field, "vector_search_dimensions", None)
                reason.append(
                    f"vector dimension mismatch (existing={existing_dim}, expected={self.vector_dimensions})"
                )
            logger.warning(
                "Index '%s' drift detected (%s). Recreating index.",
                index_name,
                "; ".join(reason),
            )
            self.index_client.delete_index(index_name)
        except ResourceNotFoundError:
            logger.info("Index '%s' not found. Creating new index.", index_name)
        except Exception as exc:
            logger.error("Failed to inspect index '%s': %s", index_name, exc)
            raise

        self.index_client.create_index(index)
        logger.info("Created index '%s' with vector search settings.", index_name)
    
    def process_document(self, file_path: str, filename: str, chat_id: str, chat_name: str = None) -> dict:
        """
        Process a document and add it to the vector store scoped to a chat.
        
        Args:
            file_path: Path to the document file
            filename: Original filename
            chat_id: Chat session identifier
            chat_name: Chat name for index creation (optional, defaults to chat_id)
            
        Returns:
            Dictionary with processing status and chunk count
        """
        try:
            if not chat_id.strip():
                return {
                    "success": False,
                    "message": "chat_id is required to process documents.",
                    "chunks": 0,
                }

            # Use chat_name for index, fallback to chat_id if not provided
            index_key = chat_name if chat_name else chat_id
            
            # Get or create chat-specific search client
            search_client = self._get_search_client_for_chat(index_key)

            # Extract text from the file
            text = extract_text_from_file(file_path)
            
            if not text.strip():
                return {
                    "success": False,
                    "message": "No text could be extracted from the file",
                    "chunks": 0
                }
            
            # Create document and split into chunks
            doc = Document(page_content=text, metadata={"source": filename})
            chunks = self.text_splitter.split_documents([doc])
            
            # Prepare documents for Azure AI Search
            if not chunks:
                return {
                    "success": False,
                    "message": "No chunks were produced from this document.",
                    "chunks": 0,
                }
            
            texts = [chunk.page_content for chunk in chunks]
            embeddings = self.embeddings.embed_documents(texts)

            if not embeddings:
                return {
                    "success": False,
                    "message": "Embedding service returned no vectors.",
                    "chunks": 0,
                }

            detected_dim = len(embeddings[0])
            if detected_dim != self.vector_dimensions:
                raise ValueError(
                    "Embedding dimension mismatch: Azure Search index expects "
                    f"{self.vector_dimensions} but embedding deployment returned {detected_dim}. "
                    "Set VECTOR_DIMENSIONS to the correct value or recreate the index."
                )
            
            documents = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                scoped_filename = f"{chat_id}_{filename}"
                documents.append(
                    {
                        "id": self._sanitize_document_id(scoped_filename, i),
                        "content": chunk.page_content,
                        "content_vector": embedding,
                        "source": chunk.metadata.get("source", filename),
                        "chat_id": chat_id,
                    }
                )
            
            if not documents:
                return {
                    "success": False,
                    "message": "No embeddable content found after preprocessing.",
                    "chunks": 0,
                }
            
            upload_results = search_client.upload_documents(documents=documents)
            failures = [r for r in upload_results if not getattr(r, "succeeded", True)]
            if failures:
                raise RuntimeError(
                    f"Failed to index {len(failures)} chunk(s). "
                    f"First error: {getattr(failures[0], 'error_message', 'Unknown')}"
                )
            
            return {
                "success": True,
                "message": f"Successfully processed {filename} for chat {chat_id}",
                "chunks": len(chunks)
            }
            
        except (ValueError, IOError, RuntimeError) as e:
            return {
                "success": False,
                "message": f"Error processing document: {str(e)}",
                "chunks": 0
            }
    
    def query(self, question: str, chat_id: str, chat_name: str = None) -> dict:
        """
        Query the RAG system with a question.
        
        Args:
            question: User's question
            chat_id: Chat session identifier
            chat_name: Chat name for index lookup (optional, defaults to chat_id)
            
        Returns:
            Dictionary with answer and source information
        """
        try:
            if not chat_id.strip():
                return {
                    "success": False,
                    "answer": "chat_id is required to perform a query.",
                    "sources": [],
                }

            # Use chat_name for index, fallback to chat_id if not provided
            index_key = chat_name if chat_name else chat_id
            
            # Get chat-specific search client
            search_client = self._get_search_client_for_chat(index_key)

            # Generate embedding for the question
            question_vector = self.embeddings.embed_query(question)
            
            # Perform vector search using the correct Azure Search syntax
            vector_query = VectorizedQuery(
                vector=question_vector,
                k_nearest_neighbors=3,
                fields="content_vector"
            )
            
            filter_value = self._escape_filter_value(chat_id)
            search_results = search_client.search(
                search_text=None,
                vector_queries=[vector_query],
                select=["content", "source"],
                filter=f"chat_id eq '{filter_value}'",
            )
            
            # Extract relevant documents
            relevant_docs = []
            sources = []
            for result in search_results:
                relevant_docs.append(result["content"])
                sources.append({
                    "content": result["content"][:200] + "...",
                    "source": result.get("source", "Unknown")
                })
            
            if not relevant_docs:
                return {
                    "success": True,
                    "answer": "I couldn't find any relevant information in the uploaded documents to answer your question.",
                    "sources": []
                }
            
            # Format context from retrieved documents
            context = "\n\n".join(relevant_docs)
            
            # Format chat history
            history = self.chat_history.get(chat_id, [])
            history_text = ""
            if history:
                history_text = "\n".join([
                    f"Human: {h['question']}\nAssistant: {h['answer']}"
                    for h in history[-3:]  # Last 3 exchanges
                ])
            
            # Create prompt
            prompt_template = """You are a helpful AI assistant. Use the following context from documents to answer the question. If you cannot find the answer in the context, say so.

Chat History:
{history}

Context from documents:
{context}

Question: {question}

Answer:"""
            
            prompt = ChatPromptTemplate.from_template(prompt_template)
            
            rag_chain = prompt | self.llm | StrOutputParser()
            
            answer = rag_chain.invoke(
                {
                    "context": context,
                    "question": question,
                    "history": history_text,
                }
            )
            
            # Store in chat history
            history.append({
                "question": question,
                "answer": answer
            })
            self.chat_history[chat_id] = history
            
            return {
                "success": True,
                "answer": answer,
                "sources": sources
            }
            
        except (ValueError, RuntimeError, KeyError) as e:
            return {
                "success": False,
                "answer": f"Error processing query: {str(e)}",
                "sources": []
            }
    
    def reset(self, chat_id: Optional[str] = None) -> dict:
        """
        Reset the conversation history and optionally remove documents for a chat.
        """
        if chat_id:
            self.chat_history.pop(chat_id, None)
            deleted = self._delete_documents(chat_id)
            return {
                "success": True,
                "message": f"Chat {chat_id} reset. Removed {deleted} indexed chunks.",
            }

        self.chat_history = {}
        deleted = self._delete_documents(None)
        return {
            "success": True,
            "message": f"System reset. Removed {deleted} indexed chunks across all chats.",
        }
    
    def get_status(self, chat_id: Optional[str] = None) -> dict:
        """
        Get the current status of the RAG system.
        
        Returns:
            Dictionary with system status information
        """
        has_documents = self._chat_has_documents(chat_id)
        target = f"chat '{chat_id}'" if chat_id else "the system"
        
        return {
            "has_documents": has_documents,
            "ready": True,
            "message": f"Ready to answer questions for {target}."
        }

    def _chat_has_documents(self, chat_id: Optional[str]) -> bool:
        """Determine whether any documents exist for the chat (or globally if None)."""
        try:
            filter_clause = None
            if chat_id:
                filter_clause = f"chat_id eq '{self._escape_filter_value(chat_id)}'"
            results = self.search_client.search(
                search_text="*",
                filter=filter_clause,
                select=["id"],
                top=1,
            )
            return any(results)
        except (ValueError, RuntimeError) as exc:
            logger.warning("Error checking status: %s", exc)
            return False

    def _delete_documents(self, chat_id: Optional[str]) -> int:
        """Delete all documents for a chat (or globally if chat_id is None)."""
        filter_clause = None
        if chat_id:
            filter_clause = f"chat_id eq '{self._escape_filter_value(chat_id)}'"

        results = self.search_client.search(
            search_text="*",
            filter=filter_clause,
            select=["id"],
        )

        ids = [{"id": doc["id"]} for doc in results]
        deleted = 0
        while ids:
            batch = ids[:1000]
            self.search_client.delete_documents(documents=batch)
            deleted += len(batch)
            ids = ids[1000:]
        return deleted
