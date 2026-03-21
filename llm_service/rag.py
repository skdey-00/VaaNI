import os
from pathlib import Path
from typing import List
import faiss
import numpy as np
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, UnstructuredMarkdownLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from config import FAISS_INDEX_PATH, CHUNK_SIZE, CHUNK_OVERLAP, OLLAMA_HOST


class RAGService:
    """Retrieval-Augmented Generation service using FAISS vector store."""

    def __init__(self, processes_dir: str = "processes"):
        self.processes_dir = Path(processes_dir)
        self.index_path = Path(FAISS_INDEX_PATH)
        self.embeddings = OllamaEmbeddings(
            base_url=OLLAMA_HOST,
            model="nomic-embed-text"  # Good embedding model
        )
        self.vector_store = None
        self._initialize()

    def _initialize(self):
        """Initialize or load the FAISS index."""
        # Check if pre-built index exists
        if self.index_path.exists():
            print(f"Loading existing FAISS index from {self.index_path}")
            try:
                self.vector_store = FAISS.load_local(
                    self.index_path,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
            except TypeError:
                # If allow_dangerous_deserialization is not supported, try without it
                print("Falling back to loading without allow_dangerous_deserialization")
                try:
                    self.vector_store = FAISS.load_local(
                        self.index_path,
                        self.embeddings
                    )
                except Exception as e:
                    print(f"Failed to load index: {e}. Rebuilding...")
                    self._build_index()
        else:
            print("Building new FAISS index from markdown files")
            self._build_index()

    def _build_index(self):
        """Build FAISS index from markdown files."""
        # Load markdown files
        loader = DirectoryLoader(
            str(self.processes_dir),
            glob="**/*.md",
            loader_cls=UnstructuredMarkdownLoader,
            show_progress=True
        )
        documents = loader.load()

        if not documents:
            print("Warning: No documents found in processes directory")
            # Create empty index
            self.vector_store = FAISS.from_texts(
                ["No banking processes available."],
                self.embeddings
            )
            return

        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", "##", "###", ". ", " ", ""]
        )
        texts = text_splitter.split_documents(documents)

        print(f"Created {len(texts)} chunks from {len(documents)} documents")

        # Create FAISS index
        self.vector_store = FAISS.from_documents(
            texts,
            self.embeddings
        )

        # Save the index
        self.index_path.mkdir(parents=True, exist_ok=True)
        self.vector_store.save_local(str(self.index_path))
        print(f"FAISS index saved to {self.index_path}")

    def retrieve(self, query: str, k: int = 3) -> List[str]:
        """Retrieve relevant document chunks for the query."""
        if self.vector_store is None:
            return []

        try:
            docs = self.vector_store.similarity_search(query, k=k)
            return [doc.page_content for doc in docs]
        except Exception as e:
            print(f"Error retrieving documents: {e}")
            return []

    def retrieve_with_scores(self, query: str, k: int = 3) -> List[tuple[str, float]]:
        """Retrieve relevant document chunks with similarity scores."""
        if self.vector_store is None:
            return []

        try:
            docs_with_scores = self.vector_store.similarity_search_with_score(query, k=k)
            return [(doc.page_content, float(score)) for doc, score in docs_with_scores]
        except Exception as e:
            print(f"Error retrieving documents: {e}")
            return []

    def get_context(self, query: str, k: int = 3) -> str:
        """Get formatted context string from retrieved documents."""
        chunks = self.retrieve(query, k)
        return "\n\n---\n\n".join(chunks)

    def _detect_query_type(self, text: str) -> str:
        """Detect the type of banking query from text."""
        text_lower = text.lower()

        query_types = {
            "account_opening": ["account", "open", "new account", "savings", "current", "salary account"],
            "loan_enquiry": ["loan", "borrow", "credit", "emi", "interest rate"],
            "kyc_verification": ["kyc", "verify", "identity", "document", "aadhaar", "pan", "know your customer"],
            "fd_booking": ["fd", "fixed deposit", "term deposit", "invest"],
            "remittance": ["remit", "transfer", "send money", "neft", "rtgs", "imps", "wire"],
            "complaint_lodging": ["complaint", "issue", "problem", "dispute", "grievance", "lodging"]
        }

        for qtype, keywords in query_types.items():
            if any(kw in text_lower for kw in keywords):
                return qtype

        return "general"

    def get_all_processes(self) -> List[dict]:
        """Get list of all available processes."""
        processes = []
        for md_file in sorted(self.processes_dir.glob("*.md")):
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Extract title (first # heading)
                title = md_file.stem.replace('_', ' ').title()
                for line in content.split('\n')[:10]:
                    if line.strip().startswith('# '):
                        title = line.strip().lstrip('# ').strip()
                        break

                # Count steps (numbered lists)
                steps_count = len([line for line in content.split('\n')
                                if line.strip() and any(line.strip().startswith(f"{i}.")
                                for i in range(1, 100))])

                processes.append({
                    "id": md_file.stem,
                    "name": title,
                    "steps_count": steps_count,
                    "file": md_file.name
                })
        return processes


# Singleton instance
_rag_service = None

def get_rag_service() -> RAGService:
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
